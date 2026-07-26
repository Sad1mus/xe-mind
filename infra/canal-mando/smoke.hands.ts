/**
 * smoke.hands.ts — Tarea 3 de Fase A: Xe ejecuta una tool reversible BAJO el gate.
 * Corre runXeSession en modo operativo (permissionMode "default" + gate-hook via --settings),
 * EXEC_MODE=reversible. Xe crea un archivo (reversible) → se verifica que se creó y que el
 * audit registró el allow. Requiere env: SANDBOX_DIR, GATE_SETTINGS, AUDIT_LOG_PATH.
 */
import { runXeSession } from "./agent.js";
import { existsSync, rmSync, readFileSync } from "node:fs";
import { join } from "node:path";

const SANDBOX = process.env.SANDBOX_DIR ?? process.cwd();
const AUDIT = process.env.AUDIT_LOG_PATH ?? join(SANDBOX, "audit.ndjson");
const TARGET = join(SANDBOX, "xe_hizo_esto.txt");
if (existsSync(TARGET)) rmSync(TARGET);
if (existsSync(AUDIT)) rmSync(AUDIT);

async function main(): Promise<void> {
  const reply = await runXeSession(
    `Usá la tool Write para crear el archivo ${TARGET} con el contenido exactamente: XE-CON-MANOS. Después respondé solo: LISTO.`,
    {
      systemPromptPath: "",
      cwd: SANDBOX,
      permissionMode: "default", // el gate-hook gobierna
      settingsPath: process.env.GATE_SETTINGS,
      timeoutMs: 150_000,
    },
  );
  console.log("reply:", JSON.stringify(reply.slice(0, 120)));

  const created = existsSync(TARGET);
  console.log("archivo reversible creado:", created);
  if (created) console.log("contenido:", JSON.stringify(readFileSync(TARGET, "utf8").trim()));

  const lines = existsSync(AUDIT) ? readFileSync(AUDIT, "utf8").trim().split("\n").filter(Boolean) : [];
  const hasWriteAllow = lines.some((l) => {
    try {
      const d = JSON.parse(l);
      return d.verdict?.decision === "allow" && (d.action?.tool === "Write" || d.action?.kind === "write_reversible");
    } catch {
      return false;
    }
  });
  console.log(`audit: ${lines.length} líneas; tiene allow de write_reversible:`, hasWriteAllow);

  if (created && hasWriteAllow) {
    console.log("SMOKE HANDS OK — Xe ejecutó una acción reversible bajo el gate.");
    process.exit(0);
  }
  console.error("SMOKE HANDS FAIL");
  process.exit(1);
}

main().catch((e) => {
  console.error("FAIL:", (e as Error).message);
  process.exit(1);
});
