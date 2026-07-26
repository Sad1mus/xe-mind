/**
 * smoke.agent.ts — prueba de humo del transporte (Tarea 1 de la cola).
 * Verifica que runXeSession() invoca `claude -p` (suscripción, sin API key) y devuelve texto.
 * Correr con tsx. NO forma parte del runtime del canal.
 */
import { runXeSession } from "./agent.js";

async function main(): Promise<void> {
  const text = await runXeSession("responde unicamente con la palabra: SMOKE-OK", {
    systemPromptPath: "",
    cwd: process.cwd(),
    permissionMode: "plan", // el modo de Fase 1 (read_only)
    timeoutMs: 90_000,
  });
  console.log("RESULT:", JSON.stringify(text));
  if (!text || text.trim().length === 0) {
    console.error("FAIL: runXeSession devolvió texto vacío");
    process.exit(1);
  }
  console.log("SMOKE PASS: runXeSession devolvió texto no vacío vía claude -p (sin API key)");
}

main().catch((e) => {
  console.error("FAIL:", (e as Error).message);
  process.exit(1);
});
