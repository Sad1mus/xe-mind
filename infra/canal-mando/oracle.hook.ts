/**
 * oracle.hook.ts — Prueba el gate-hook end-to-end (Tarea 2 de Fase A).
 * Le manda tool-calls simuladas por stdin (como haría Claude Code) y verifica la
 * decisión emitida, en EXEC_MODE=reversible. Corre con tsx. Sale 0 si todo pasa.
 */
import { spawnSync } from "node:child_process";
import { readFileSync, existsSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const DIR = process.cwd();
const HOOK = join(DIR, "gate-hook.ts");
const TSX = process.env.TSX_BIN ?? "tsx";
const AUDIT = join(DIR, "oracle.hook.audit.ndjson");
const KILL = join(DIR, "ORACLE_HOOK_KILL");
if (existsSync(AUDIT)) rmSync(AUDIT);
if (existsSync(KILL)) rmSync(KILL);

const REV: Record<string, string> = {
  EXEC_MODE: "reversible",
  CAP_TOKENS_PER_SESSION: "1000000", // presupuesto operativo positivo (si no, el cap 0 frena todo)
  CAP_TOKENS_PER_DAY: "1000000",
  KILL_SWITCH_PATH: KILL,
  AUDIT_LOG_PATH: AUDIT,
};

function runHook(payload: object, env: Record<string, string>): { decision: string; reason: string } {
  const res = spawnSync(TSX, [HOOK], {
    input: JSON.stringify(payload),
    encoding: "utf8",
    env: { ...process.env, ...env },
  });
  try {
    const out = JSON.parse(res.stdout);
    return {
      decision: out.hookSpecificOutput.permissionDecision,
      reason: out.hookSpecificOutput.permissionDecisionReason ?? "",
    };
  } catch {
    return { decision: `PARSE_ERR(${res.status})`, reason: (res.stdout + res.stderr).slice(0, 200) };
  }
}

let pass = true;
function check(name: string, got: string, want: string): void {
  const ok = got === want;
  console.log((ok ? "  ok  " : "  FAIL") + ` — ${name}: ${got}` + (ok ? "" : ` (esperado ${want})`));
  if (!ok) pass = false;
}

// En reversible: read y write_reversible pasan; money/outbound/desconocido se frenan.
check("Read → allow", runHook({ tool_name: "Read", tool_input: { file_path: "x" } }, REV).decision, "allow");
check("Write → allow", runHook({ tool_name: "Write", tool_input: { file_path: "x", content: "y" } }, REV).decision, "allow");
check("Bash 'ls -la' → allow (read)", runHook({ tool_name: "Bash", tool_input: { command: "ls -la" } }, REV).decision, "allow");
check("Bash 'node build.js' → allow (write_reversible)", runHook({ tool_name: "Bash", tool_input: { command: "node build.js" } }, REV).decision, "allow");
check("Bash 'git push' → deny (outbound/envío)", runHook({ tool_name: "Bash", tool_input: { command: "git push origin main" } }, REV).decision, "deny");
check("Bash 'stripe charge' → deny (dinero)", runHook({ tool_name: "Bash", tool_input: { command: "stripe charge --amount 5000" } }, REV).decision, "deny");
check("Bash 'rm -rf /srv' → deny (destructivo)", runHook({ tool_name: "Bash", tool_input: { command: "rm -rf /srv/x" } }, REV).decision, "deny");
check("Tool desconocida → deny (baja confianza §4)", runHook({ tool_name: "FooBarTool", tool_input: {} }, REV).decision, "deny");

// P5: descubrimiento read-only y clasificación de MCP (sin abrir el default).
check("ToolSearch → allow (descubrimiento read-only)", runHook({ tool_name: "ToolSearch", tool_input: { query: "select:Read" } }, REV).decision, "allow");
check("mcp__stripe__charge → deny (dinero MCP)", runHook({ tool_name: "mcp__stripe__charge", tool_input: {} }, REV).decision, "deny");
check("mcp__Ramp_Data__pay → deny (dinero MCP: ramp)", runHook({ tool_name: "mcp__Ramp_Data__pay", tool_input: {} }, REV).decision, "deny");
check("mcp__apify__search → allow (MCP genérico reversible)", runHook({ tool_name: "mcp__apify__search-actors", tool_input: {} }, REV).decision, "allow");
check("Frobnicate → deny (tool inventada, baja §4)", runHook({ tool_name: "Frobnicate", tool_input: {} }, REV).decision, "deny");

// DEC-017 / onboarding-meta: construir (provisioning) es reversible; go-live/entrega es visto humano.
check("onboarding-meta dry-run → allow (provisioning read)",
  runHook({ tool_name: "Bash", tool_input: { command: "python3 packages/onboarding-meta/connector.py dry-run" } }, REV).decision, "allow");
check("onboarding-meta execute → allow (alta reversible)",
  runHook({ tool_name: "Bash", tool_input: { command: "REGISTRO_DB=/tmp/x.db python3 packages/onboarding-meta/connector.py execute --confirm" } }, REV).decision, "allow");
check("go-live (abrir al público) → deny (visto humano, DEC-017)",
  runHook({ tool_name: "Bash", tool_input: { command: "python3 packages/onboarding-meta/connector.py go-live --abrir-al-publico" } }, REV).decision, "deny");
check("enviar-al-cliente → deny (visto humano, GUARDA-001)",
  runHook({ tool_name: "Bash", tool_input: { command: "bash entrega.sh enviar-al-cliente clinica-sonrisa" } }, REV).decision, "deny");

// Fase D: entrega dry-run construye (reversible); nueva_clinica hace el INSERT en Supabase = visto humano.
check("entrega_dryrun dry-run → allow (construir, reversible)",
  runHook({ tool_name: "Bash", tool_input: { command: "python3 integrations/clinics/entrega_dryrun.py dry-run" } }, REV).decision, "allow");
check("nueva_clinica (INSERT Supabase) → deny (entrega, visto humano)",
  runHook({ tool_name: "Bash", tool_input: { command: "cd /tmp/clinics-checkout && npx tsx scripts/nueva_clinica.ts --json '{\"nombre\":\"X\"}'" } }, REV).decision, "deny");

// kill-switch corta todo, incluso lectura.
writeFileSync(KILL, "x");
check("kill-switch → deny (incluso Read)", runHook({ tool_name: "Read", tool_input: { file_path: "x" } }, REV).decision, "deny");
rmSync(KILL);

// audit: una línea por decisión.
const lines = existsSync(AUDIT) ? readFileSync(AUDIT, "utf8").trim().split("\n").filter(Boolean) : [];
let auditOk = lines.length >= 19;
for (const l of lines) {
  try {
    JSON.parse(l);
  } catch {
    auditOk = false;
  }
}
check(`audit NDJSON válido (${lines.length} líneas, >=19)`, auditOk ? "ok" : "fail", "ok");

if (pass) {
  console.log("HOOK GATE OK — reversible ejecuta; dinero/envío/destructivo/desconocido bloqueados; kill corta; auditado.");
  process.exit(0);
} else {
  console.error("HOOK ORACLE FAIL");
  process.exit(1);
}
