/**
 * bridge.ts — Entrada del canal de mando: Telegram → Xe (Claude Code headless).
 *
 * Responsabilidades (DEC-012):
 *   1. Auth dura: solo responde a chat_id en la allowlist. Todo lo demás se ignora y se loguea.
 *   2. Kill switch / rate-limit antes de invocar nada.
 *   3. Arma el contexto (system = CLAUDE.md de Xe; handoff entrante del substrato).
 *   4. Corre la sesión con el gate de governance.ts enganchado.
 *   5. Resuelve los `needs_confirm` pidiendo el 2º OK humano por Telegram (doble gate).
 *   6. Audita todo y escribe el handoff saliente al substrato (§7).
 *
 * ⚠️ TODO(verificar-SDK) en agent.ts. El cliente de Telegram (abajo) es grammY a modo
 * de referencia — ajustar a tu librería. La lógica de gobierno NO depende de ninguna de las dos.
 */
import { gate, type Action, type GovConfig, type Usage, type Verdict } from "./governance.js";
import { audit } from "./audit.js";
import { runXeSession } from "./agent.js";
import { getAgencyStatus, isStatusQuery } from "./status.js";

// --- Config desde env (GUARDA-005: nada hardcodeado) ---
const env = process.env;
const ALLOWED = (env.TELEGRAM_ALLOWED_CHAT_IDS ?? "").split(",").map((s) => s.trim()).filter(Boolean);
const cfg: GovConfig = {
  execMode: (env.EXEC_MODE as GovConfig["execMode"]) ?? "read_only",
  killSwitchPath: env.KILL_SWITCH_PATH ?? "./KILL",
  caps: {
    usdPerAction: num(env.CAP_USD_PER_ACTION),
    usdPerDay: num(env.CAP_USD_PER_DAY),
    usdPerClientPerDay: num(env.CAP_USD_PER_CLIENT_PER_DAY),
    tokensPerSession: num(env.CAP_TOKENS_PER_SESSION),
    tokensPerDay: num(env.CAP_TOKENS_PER_DAY),
    outboundActionsPerHour: num(env.CAP_OUTBOUND_ACTIONS_PER_HOUR),
  },
};
const AUDIT_LOG = env.AUDIT_LOG_PATH ?? "./audit.ndjson";
const TEATRO = env.TEATRO ?? "americas";

/** num(): sin valor => NaN, y los topes NaN hacen que el gate bloquee (no asume). */
function num(v?: string): number {
  return v === undefined || v === "" ? NaN : Number(v);
}

function isAuthorized(chatId: string): boolean {
  return ALLOWED.includes(chatId);
}

/**
 * Maneja un mensaje entrante. `askConfirm` es cómo el bridge pregunta al humano
 * (mostrar el dry-run + esperar "sí/no"); lo provee el binding de Telegram.
 */
export async function handleMessage(
  chatId: string,
  text: string,
  askConfirm: (dryRun: string, reason: string) => Promise<boolean>,
  reply: (msg: string) => Promise<void>,
): Promise<void> {
  if (!isAuthorized(chatId)) {
    audit(AUDIT_LOG, { ts: nowIso(), chatId, teatro: TEATRO, action: rejected(text), verdict: { decision: "deny", reason: "chat_id no autorizado" } });
    return; // silencio: no confirmamos siquiera que el bot existe a un desconocido
  }

  // Estado de consumo de la ventana — TODO: leer del substrato/contador persistente.
  const usage: Usage = loadUsage();

  // Fast-path determinista para consultas de estado: lee el registro vía el connector
  // de reporte (<1s) en vez de que Xe explore el repo con claude -p (evita el timeout).
  if (isStatusQuery(text)) {
    const action: Action = { tool: "reporte_dry_run", kind: "read", confidence: "alta", summary: text.slice(0, 80) };
    const v = gate(action, usage, cfg);
    audit(AUDIT_LOG, { ts: nowIso(), chatId, teatro: TEATRO, action, verdict: v });
    if (v.decision === "allow") {
      await reply(getAgencyStatus(env.XE_REPO_CWD ?? "../../.."));
      return;
    }
    await reply(`🚫 ${"reason" in v ? v.reason : "bloqueado por el gate"}`);
    return;
  }

  // El gate, cerrado sobre usage+cfg, y con el doble confirm para irreversibles.
  const decide = async (action: Action): Promise<Verdict> => {
    const v = gate(action, usage, cfg);
    if (v.decision === "needs_confirm") {
      const ok = await askConfirm(v.dryRun, v.reason); // 2º OK humano por Telegram (doble gate)
      audit(AUDIT_LOG, { ts: nowIso(), chatId, teatro: TEATRO, action, verdict: v, confirmedBy: ok ? chatId : undefined });
      return ok ? { decision: "allow" } : { decision: "deny", reason: "Humano denegó el confirm." };
    }
    audit(AUDIT_LOG, { ts: nowIso(), chatId, teatro: TEATRO, action, verdict: v });
    return v;
  };

  try {
    const out = await runXeSession(buildPrompt(text), {
      systemPromptPath: env.XE_SYSTEM_PROMPT_PATH ?? "../../CLAUDE.md",
      cwd: env.XE_REPO_CWD ?? "../../..",
      // Modo OPERATIVO (con manos): con GATE_SETTINGS, Xe ejecuta bajo el gate-hook
      // (permissionMode "default"). Sin settings => "plan" (solo lectura, default seguro).
      // El dinero/envío lo frena el gate-hook y Xe lo REDACTA; su respuesta (con el dry-run)
      // se relaya tal cual al humano por Telegram.
      permissionMode: env.GATE_SETTINGS ? "default" : "plan",
      settingsPath: env.GATE_SETTINGS,
    });
    await reply(out);
  } catch (e) {
    await reply(`⚠️ Xe se detuvo: ${(e as Error).message}`);
  }
  // TODO(§7): escribir handoff saliente al substrato (en vuelo / bloqueado / espera-humano).
}

// --- Helpers / stubs a completar ---
function buildPrompt(text: string): string {
  // TODO: prepend del handoff entrante del substrato (§7) antes del mensaje del humano.
  return text;
}
function classify(toolName: string, _input: unknown): Action {
  // TODO: clasificación real por tool. Por defecto, lo desconocido es de baja confianza => se bloquea.
  return { tool: toolName, kind: "read", confidence: "baja", summary: `tool ${toolName}` };
}
function loadUsage(): Usage {
  // TODO: leer contadores persistentes (substrato). Stub conservador = 0 consumido.
  return { usdToday: 0, usdTodayByClient: {}, tokensThisSession: 0, tokensToday: 0, outboundLastHour: 0 };
}
function rejected(text: string): Action {
  return { tool: "telegram_message", kind: "read", confidence: "baja", summary: text.slice(0, 80) };
}
function nowIso(): string {
  return new Date().toISOString(); // en runtime real está bien; evitar en scripts resumibles
}

/*
 * --- Binding de Telegram (referencia grammY — ajustar) ---
 * import { Bot } from "grammy";
 * const bot = new Bot(env.TELEGRAM_BOT_TOKEN!);
 * bot.on("message:text", async (ctx) => {
 *   const chatId = String(ctx.chat.id);
 *   await handleMessage(
 *     chatId,
 *     ctx.message.text,
 *     async (dryRun, reason) => {
 *       await ctx.reply(`🔐 Confirmación requerida (${reason})\n\n${dryRun}\n\nResponde SÍ para ejecutar.`);
 *       // TODO: capturar la siguiente respuesta del MISMO chatId y resolver true/false.
 *       return false; // por defecto: NO ejecuta hasta implementar la captura.
 *     },
 *     (msg) => ctx.reply(msg).then(() => {}),
 *   );
 * });
 * bot.start();
 */
