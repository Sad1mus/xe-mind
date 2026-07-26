/**
 * oracle.gate.ts — Oracle del gate en modo read_only (Tarea 2 de la cola).
 *
 * Prueba, SIN inventar, que governance.gate() cumple la Fase 1:
 *   - una acción `read` (confianza alta) PASA;
 *   - `write_reversible` / `money` / `outbound` son RECHAZADAS en EXEC_MODE=read_only;
 *   - confianza BAJA se bloquea (§4);
 *   - el kill switch (GUARDA-006) gana sobre todo;
 *   - cada decisión queda en el audit append-only (NDJSON) válido.
 *
 * Correr con tsx. No forma parte del runtime. Sale 0 si todo pasa.
 */
import { gate, type Action, type GovConfig, type Usage } from "./governance.js";
import { audit } from "./audit.js";
import { writeFileSync, existsSync, rmSync, readFileSync } from "node:fs";
import { join } from "node:path";

const AUDIT = join(process.cwd(), "oracle.audit.ndjson");
const KILL = join(process.cwd(), "ORACLE_KILL");
if (existsSync(AUDIT)) rmSync(AUDIT);
if (existsSync(KILL)) rmSync(KILL);

// Topes en CERO (GUARDA-006: sin tope configurado no se asume). En read_only las
// escrituras se frenan por modo antes de llegar a topes; los topes se prueban en fases superiores.
const cfg: GovConfig = {
  execMode: "read_only",
  killSwitchPath: KILL,
  caps: {
    usdPerAction: 0, usdPerDay: 0, usdPerClientPerDay: 0,
    tokensPerSession: 0, tokensPerDay: 0, outboundActionsPerHour: 0,
  },
};
const usage: Usage = {
  usdToday: 0, usdTodayByClient: {}, tokensThisSession: 0, tokensToday: 0, outboundLastHour: 0,
};

function act(kind: Action["kind"], confidence: Action["confidence"]): Action {
  return { tool: "test_tool", kind, confidence, summary: `${kind}/${confidence}` };
}
function logAudit(a: Action, v: ReturnType<typeof gate>): void {
  audit(AUDIT, { ts: new Date().toISOString(), chatId: "oracle", teatro: "americas", action: a, verdict: v });
}

let pass = true;
function check(name: string, cond: boolean): void {
  console.log((cond ? "  ok  " : "  FAIL") + " — " + name);
  if (!cond) pass = false;
}

// 1. read / alta => allow (las lecturas pasan incluso en read_only)
{ const a = act("read", "alta"); const v = gate(a, usage, cfg); logAudit(a, v);
  check("read/alta => allow", v.decision === "allow"); }

// 2. write_reversible / alta => deny (read_only)
{ const a = act("write_reversible", "alta"); const v = gate(a, usage, cfg); logAudit(a, v);
  check("write_reversible/alta => deny en read_only", v.decision === "deny"); }

// 3. money / alta => deny (read_only lo frena antes del doble gate)
{ const a = act("money", "alta"); const v = gate(a, usage, cfg); logAudit(a, v);
  check("money/alta => deny en read_only", v.decision === "deny"); }

// 4. outbound / alta => deny (read_only)
{ const a = act("outbound", "alta"); const v = gate(a, usage, cfg); logAudit(a, v);
  check("outbound/alta => deny en read_only", v.decision === "deny"); }

// 5. confianza baja => deny (§4), aunque sea lectura
{ const a = act("read", "baja"); const v = gate(a, usage, cfg);
  check("read/baja => deny (confianza §4)", v.decision === "deny"); }

// 6. kill switch => deny todo (GUARDA-006)
{ writeFileSync(KILL, "x");
  const v = gate(act("read", "alta"), usage, cfg);
  check("kill switch activo => deny incluso lectura", v.decision === "deny");
  rmSync(KILL); }

// 7. audit append-only: NDJSON válido, una línea por decisión gateada (4 auditadas)
{ const lines = readFileSync(AUDIT, "utf8").trim().split("\n");
  let auditOk = lines.length >= 4;
  for (const l of lines) { try { JSON.parse(l); } catch { auditOk = false; } }
  check(`audit NDJSON válido (${lines.length} líneas)`, auditOk); }

if (pass) {
  console.log("READONLY PASS / WRITE BLOCKED / AUDIT OK");
  process.exit(0);
} else {
  console.error("ORACLE FAIL");
  process.exit(1);
}
