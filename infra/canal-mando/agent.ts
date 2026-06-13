/**
 * agent.ts — Adaptador al Claude Agent SDK (Claude Code headless).
 *
 * ⚠️ TODO(verificar-SDK): fijar la firma exacta contra la versión instalada de
 * `@anthropic-ai/claude-agent-sdk`. Las APIs del Agent SDK evolucionan; lo que
 * NO cambia es el contrato de este archivo con el resto:
 *   - se le pasa el system prompt (CLAUDE.md de Xe) + el cwd (repo Agencia)
 *   - cada tool-call pasa por `decide()` ANTES de ejecutarse (el gate de governance.ts)
 *   - `decide()` puede ALLOW / DENY / pedir confirm (que el bridge resuelve por Telegram)
 *
 * La idea clave: el SDK expone un hook de permisos (en Claude Code es `canUseTool`).
 * Ese hook es donde enganchamos governance.gate(). Si el nombre/forma del hook
 * difiere en tu versión, sólo cambia este archivo — el gate sigue intacto.
 */
import type { Action, Verdict } from "./governance.js";

// import { query } from "@anthropic-ai/claude-agent-sdk"; // TODO(verificar-SDK): nombre/firma exactos

export interface AgentDeps {
  systemPromptPath: string; // CLAUDE.md de Xe
  cwd: string;              // repo Agencia
  apiKey: string;
  /** Traduce una tool-call cruda del SDK a la Action tipada que governance entiende. */
  classify: (toolName: string, input: unknown) => Action;
  /** El gate: decide allow/deny/needs_confirm. Lo provee el bridge (cierra sobre usage+cfg). */
  decide: (action: Action) => Promise<Verdict>;
}

/**
 * Corre una sesión headless de Claude Code sobre el repo, con el gate enganchado.
 * Devuelve el texto final que el bridge manda de vuelta a Telegram.
 */
export async function runXeSession(prompt: string, deps: AgentDeps): Promise<string> {
  // const system = readFileSync(deps.systemPromptPath, "utf8");
  //
  // TODO(verificar-SDK): forma de referencia (ajustar a la versión instalada):
  //
  // const run = query({
  //   prompt,
  //   options: {
  //     systemPrompt: system,
  //     cwd: deps.cwd,
  //     // El hook de permisos: NINGUNA tool se ejecuta sin pasar por aquí.
  //     canUseTool: async (toolName, input) => {
  //       const action = deps.classify(toolName, input);
  //       const verdict = await deps.decide(action); // governance.gate + (si hace falta) confirm humano
  //       if (verdict.decision === "allow") return { behavior: "allow", updatedInput: input };
  //       // deny y needs_confirm-no-confirmado => se le niega al agente con el motivo.
  //       return { behavior: "deny", message: reasonOf(verdict) };
  //     },
  //   },
  // });
  //
  // let finalText = "";
  // for await (const msg of run) {
  //   if (msg.type === "assistant") finalText += textOf(msg);
  // }
  // return finalText;

  void deps; void prompt;
  throw new Error("agent.ts: integrar Claude Agent SDK (ver TODO(verificar-SDK)).");
}
