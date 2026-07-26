/**
 * agent.ts — Adaptador a Claude Code headless vía CLI de SUSCRIPCIÓN (`claude -p`).
 *
 * AUTENTICACIÓN: token de suscripción Max (`claude setup-token`). **NO API key.**
 * Este adaptador borra `ANTHROPIC_API_KEY` de la env del hijo a propósito, para que
 * el CLI use el token de suscripción y nunca caiga en facturación por API.
 *
 * Contrato con el resto (sin cambios de intención):
 *   - se le pasa el system prompt (CLAUDE.md de Xe) + el cwd (repo Agencia)
 *   - el gate de governance.ts se engancha a nivel del CLI mediante el modo de permisos:
 *       · Fase 1 (read_only)  => `--permission-mode plan`  (Claude no escribe: solo lee/planifica)
 *   - PUNTO DE INTEGRACIÓN (Tarea 2 de la cola): la intercepción POR-TOOL con
 *     governance.decide() se cablea vía `--permission-prompt-tool` (MCP) o `--settings`.
 *     Los hooks `classify`/`decide` del contrato quedan declarados abajo para esa tarea.
 *
 * Por qué CLI y no el Agent SDK: el SDK espera `ANTHROPIC_API_KEY`; el requisito duro
 * del proyecto es suscripción, cero API. El binario `claude` autentica con el token de
 * suscripción, así que el transporte es `claude -p --output-format json`.
 */
import { spawn } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import type { Action, Verdict } from "./governance.js";

/** Modos de permiso del CLI relevantes al rollout por fases. */
export type PermissionMode = "plan" | "acceptEdits" | "auto" | "manual" | "dontAsk";

export interface AgentDeps {
  /** CLAUDE.md de Xe — se anexa como system prompt. "" o inexistente => se omite. */
  systemPromptPath: string;
  /** Working dir del agente = repo Agencia (substrato + integrations). */
  cwd: string;
  /**
   * IGNORADO a propósito: el camino es suscripción, no API key. Se mantiene el
   * campo por compat con bridge.ts (que lo pasa), pero NUNCA se usa.
   */
  apiKey?: string;
  /** Modo de permisos del CLI. Fase 1 read_only => "plan" (default seguro). */
  permissionMode?: PermissionMode;
  /** Ruta/binario de claude (default: "claude" en PATH). */
  claudeBin?: string;
  /** Modelo opcional (ej. "claude-opus-5"). */
  model?: string;
  /**
   * Modo OPERATIVO (con manos): ruta a un settings JSON con el `gate-hook` en
   * PreToolUse. Cada tool-call pasa por governance.gate() antes de ejecutarse.
   * Con esto, usar permissionMode "default" (el hook gobierna). Sin esto => solo lectura.
   */
  settingsPath?: string;
  /** Timeout duro de la sesión en ms (default 120000). */
  timeoutMs?: number;
  /** (Tarea 2) traduce una tool-call cruda del CLI a Action tipada. */
  classify?: (toolName: string, input: unknown) => Action;
  /** (Tarea 2) el gate: allow/deny/needs_confirm. Lo provee el bridge. */
  decide?: (action: Action) => Promise<Verdict>;
}

export interface XeResult {
  text: string;
  isError: boolean;
  usage?: unknown;               // .usage del CLI — alimenta topes/audit (Tarea 2)
  permissionDenials?: unknown[]; // acciones que el modo de permisos frenó
  raw: unknown;
}

/** Forma del `claude -p --output-format json`. */
interface ClaudeJson {
  result?: string;
  is_error?: boolean;
  subtype?: string;
  usage?: unknown;
  permission_denials?: unknown[];
}

/**
 * Corre una sesión headless de Claude Code y devuelve el texto final para el bridge.
 * Firma preservada respecto del esqueleto: (prompt, deps) => Promise<string>.
 */
export async function runXeSession(prompt: string, deps: AgentDeps): Promise<string> {
  const res = await runXeSessionFull(prompt, deps);
  if (res.isError) throw new Error(`Xe (claude -p) devolvió error: ${res.text || "sin detalle"}`);
  return res.text;
}

/** Igual que runXeSession pero devuelve el resultado estructurado (usage, denials, raw). */
export async function runXeSessionFull(prompt: string, deps: AgentDeps): Promise<XeResult> {
  const bin = deps.claudeBin ?? "claude";
  const args = ["-p", prompt, "--output-format", "json"];

  // El modo de permisos ES el gate a nivel de proceso. Fase 1 read_only => "plan".
  args.push("--permission-mode", deps.permissionMode ?? "plan");

  // System prompt = constitución de Xe (si existe la ruta).
  if (deps.systemPromptPath && existsSync(deps.systemPromptPath)) {
    args.push("--append-system-prompt", readFileSync(deps.systemPromptPath, "utf8"));
  }
  if (deps.model) args.push("--model", deps.model);

  // Modo operativo: el gate-hook (PreToolUse) frena cada tool-call. Sin esto, solo lectura.
  if (deps.settingsPath) args.push("--settings", deps.settingsPath);

  // AUTENTICACIÓN por suscripción: jamás pasamos API key.
  const env: NodeJS.ProcessEnv = { ...process.env };
  delete env.ANTHROPIC_API_KEY;

  const stdout = await spawnCapture(bin, args, {
    cwd: deps.cwd,
    env,
    timeoutMs: deps.timeoutMs ?? 300_000, // 5 min: consultas abiertas pueden explorar el repo
  });

  let parsed: ClaudeJson;
  try {
    parsed = JSON.parse(stdout) as ClaudeJson;
  } catch {
    // No fue JSON (p.ej. error de auth en texto plano) => se reporta como error, no se inventa.
    return { text: stdout.trim(), isError: true, raw: stdout };
  }
  return {
    text: (parsed.result ?? "").trim(),
    isError: Boolean(parsed.is_error),
    usage: parsed.usage,
    permissionDenials: parsed.permission_denials,
    raw: parsed,
  };
}

function spawnCapture(
  bin: string,
  args: string[],
  opts: { cwd: string; env: NodeJS.ProcessEnv; timeoutMs: number },
): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn(bin, args, { cwd: opts.cwd, env: opts.env, stdio: ["ignore", "pipe", "pipe"] });
    let out = "";
    let err = "";
    const timer = setTimeout(() => {
      child.kill("SIGKILL");
      reject(new Error(`claude -p excedió el timeout (${opts.timeoutMs} ms)`));
    }, opts.timeoutMs);

    child.stdout.on("data", (d) => (out += d.toString()));
    child.stderr.on("data", (d) => (err += d.toString()));
    child.on("error", (e) => {
      clearTimeout(timer);
      reject(e);
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      if (code === 0) resolve(out);
      else reject(new Error(`claude -p salió con código ${code}: ${err.trim() || out.trim()}`));
    });
  });
}
