/**
 * echo.oneshot.ts — Prueba e2e del canal (Tarea 3), sin depender del long-poll.
 * Ejercita la MISMA cadena de producción: allowlist → gate (governance) → audit →
 * agent.ts (`claude -p`, plan/read_only) → responde por la API de Telegram.
 * Toma el/los update(s) pendientes, procesa el último del chat autorizado y contesta.
 */
import { runXeSession } from "./agent.js";
import { getAgencyStatus, isStatusQuery } from "./status.js";
import { gate, type Action, type GovConfig, type Usage } from "./governance.js";
import { audit } from "./audit.js";
import { execFileSync } from "node:child_process";

const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
if (!TOKEN) { console.error("falta TELEGRAM_BOT_TOKEN"); process.exit(1); }
const API = `https://api.telegram.org/bot${TOKEN}`;
const ALLOWED = (process.env.TELEGRAM_ALLOWED_CHAT_IDS ?? "").split(",").map((s) => s.trim()).filter(Boolean);

// Transporte por curl: en este sandbox el fetch de node (undici) da CONNECT_TIMEOUT,
// pero curl sale bien. En la VPS real se usa el long-poll normal (grammy).
function tgGet(method: string, query = ""): any {
  const out = execFileSync("curl", ["-sS", `${API}/${method}${query}`], { encoding: "utf8", timeout: 20_000 });
  return JSON.parse(out);
}
async function tg(method: string, params: Record<string, unknown>): Promise<any> {
  const out = execFileSync("curl", ["-sS", `${API}/${method}`, "-H", "content-type: application/json", "-d", JSON.stringify(params)], { encoding: "utf8", timeout: 20_000 });
  return JSON.parse(out);
}

async function main(): Promise<void> {
  const upd = tgGet("getUpdates");
  const results: any[] = upd.result ?? [];
  if (!results.length) { console.log("Sin updates pendientes."); return; }

  const last = results[results.length - 1];
  const msg = last.message ?? last.edited_message ?? {};
  const chatId = String(msg.chat?.id ?? "");
  const text: string = msg.text ?? "";
  console.log(`IN   chat_id=${chatId} · texto=${JSON.stringify(text)}`);

  // 1. Allowlist (DEC-012)
  if (!ALLOWED.includes(chatId)) {
    console.log(`AUTH chat_id ${chatId} NO autorizado → ignorado (silencio).`);
    return;
  }
  console.log("AUTH ok (chat_id en allowlist)");

  // 2. Gate: manejar un mensaje entrante es una lectura; read_only => allow. Se audita.
  const action: Action = { tool: "telegram_message", kind: "read", confidence: "alta", summary: text.slice(0, 80) };
  const cfg: GovConfig = {
    execMode: (process.env.EXEC_MODE as GovConfig["execMode"]) ?? "read_only",
    killSwitchPath: process.env.KILL_SWITCH_PATH ?? "./KILL",
    caps: { usdPerAction: 0, usdPerDay: 0, usdPerClientPerDay: 0, tokensPerSession: 0, tokensPerDay: 0, outboundActionsPerHour: 0 },
  };
  const usage: Usage = { usdToday: 0, usdTodayByClient: {}, tokensThisSession: 0, tokensToday: 0, outboundLastHour: 0 };
  const verdict = gate(action, usage, cfg);
  audit(process.env.AUDIT_LOG_PATH ?? "./audit.ndjson", { ts: new Date().toISOString(), chatId, teatro: "americas", action, verdict });
  console.log(`GATE ${verdict.decision}${verdict.decision !== "allow" ? " — " + (verdict as any).reason : ""}`);
  if (verdict.decision !== "allow") {
    await tg("sendMessage", { chat_id: chatId, text: "🚫 El gate bloqueó esta acción en modo read_only." });
    return;
  }

  // 3. Xe responde. Fast-path determinista para consultas de estado: lee el registro
  //    vía el connector de reporte (<1s), sin que claude explore el repo (evita el timeout).
  const cwd = process.env.XE_REPO_CWD ?? process.cwd();
  let reply: string;
  if (isStatusQuery(text)) {
    console.log("XE   fast-path de estado (reporte/connector, read-only)…");
    reply = getAgencyStatus(cwd);
  } else {
    console.log("XE   pensando (claude -p, plan/read_only)…");
    reply = await runXeSession(text, {
      systemPromptPath: process.env.XE_SYSTEM_PROMPT_PATH ?? "",
      cwd,
      permissionMode: "plan",
      timeoutMs: 300_000,
    });
  }
  console.log(`OUT  reply (${reply.length} chars): ${JSON.stringify(reply.slice(0, 240))}${reply.length > 240 ? "…" : ""}`);

  // 4. Enviar de vuelta a Telegram + avanzar el offset (consumir el update)
  const sent = await tg("sendMessage", { chat_id: chatId, text: reply });
  tgGet("getUpdates", `?offset=${last.update_id + 1}`);
  console.log(sent.ok ? "SENT ✅ respuesta entregada en Telegram. Echo e2e OK." : `SENT ❌ ${JSON.stringify(sent)}`);
}

main().catch((e) => { console.error("FAIL:", (e as Error).message); process.exit(1); });
