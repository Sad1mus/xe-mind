/**
 * gate-hook.ts — El gate por-cada-tool, enganchado al `PreToolUse` de Claude Code.
 *
 * Claude Code lo invoca ANTES de ejecutar cualquier tool (via --settings). Recibe el
 * tool-call por stdin, lo clasifica, lo pasa por governance.gate(), lo audita, y
 * responde por stdout la decisión que el CLI OBEDECE. Aquí vive el "no" real (DEC-012).
 *
 * Mapa de veredictos → decisión del CLI:
 *   allow         → "allow"  (ejecuta)
 *   deny          → "deny"   (frena; §4 / topes / kill-switch)
 *   needs_confirm → "deny"   (dinero/envío, GUARDA-001): NO se ejecuta autónomamente;
 *                            se le dice a Xe que REDACTE el dry-run para el humano.
 */
import { readFileSync } from "node:fs";
import { gate, type GovConfig, type Usage } from "./governance.js";
import { audit } from "./audit.js";
import { classify } from "./classify.js";

function numEnv(v: string | undefined, dflt: number): number {
  if (v === undefined || v === "") return dflt;
  const n = Number(v);
  return Number.isFinite(n) ? n : dflt;
}

function emit(decision: "allow" | "deny", reason: string): void {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: decision,
        permissionDecisionReason: reason,
      },
    }),
  );
}

let payload: any = {};
try {
  payload = JSON.parse(readFileSync(0, "utf8"));
} catch {
  /* stdin vacío/no-JSON */
}

const toolName = String(payload.tool_name ?? "");
const toolInput = payload.tool_input ?? {};
const action = classify(toolName, toolInput);

const cfg: GovConfig = {
  execMode: (process.env.EXEC_MODE as GovConfig["execMode"]) ?? "read_only",
  killSwitchPath: process.env.KILL_SWITCH_PATH ?? "./KILL",
  caps: {
    usdPerAction: numEnv(process.env.CAP_USD_PER_ACTION, 0),
    usdPerDay: numEnv(process.env.CAP_USD_PER_DAY, 0),
    usdPerClientPerDay: numEnv(process.env.CAP_USD_PER_CLIENT_PER_DAY, 0),
    tokensPerSession: numEnv(process.env.CAP_TOKENS_PER_SESSION, 0),
    tokensPerDay: numEnv(process.env.CAP_TOKENS_PER_DAY, 0),
    outboundActionsPerHour: numEnv(process.env.CAP_OUTBOUND_ACTIONS_PER_HOUR, 0),
  },
};

// Usage real vendrá del substrato (fase posterior). Stub conservador = 0 consumido.
const usage: Usage = {
  usdToday: 0,
  usdTodayByClient: {},
  tokensThisSession: 0,
  tokensToday: 0,
  outboundLastHour: 0,
};

const verdict = gate(action, usage, cfg);

try {
  audit(process.env.AUDIT_LOG_PATH ?? "./audit.ndjson", {
    ts: new Date().toISOString(),
    chatId: process.env.XE_CHAT_ID ?? "canal",
    teatro: process.env.TEATRO ?? "americas",
    action,
    verdict,
  });
} catch {
  /* un fallo de audit no debe abrir el gate: seguimos con la decisión */
}

if (verdict.decision === "allow") {
  emit("allow", "ok");
} else if (verdict.decision === "deny") {
  emit("deny", verdict.reason);
} else {
  // needs_confirm: dinero/envío. En modo autónomo NO se ejecuta — se redacta para el humano.
  emit(
    "deny",
    `GUARDA-001 — accion de '${action.kind}' NO se ejecuta autonomamente. Redacta el dry-run (que harias, con que datos) y devolveselo al humano para que lo ejecute el. Detalle: ${verdict.reason}`,
  );
}
