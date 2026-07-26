/**
 * bridge.telegram.ts — Entrypoint de Telegram (grammY) del canal de mando.
 *
 * Mantiene el core (`bridge.ts`) framework-agnóstico: este archivo es el ÚNICO que
 * conoce Telegram. Cablea `handleMessage()` a un bot real e implementa la CAPTURA
 * del doble-confirm (GUARDA-001/DEC-012): cuando el gate pide `needs_confirm`, se le
 * muestra el dry-run al humano y se espera su "SÍ" explícito; sin SÍ => NO se ejecuta.
 *
 * Requiere (input humano, por env — GUARDA-005):
 *   TELEGRAM_BOT_TOKEN         token del bot NUEVO de BotFather (secreto crítico)
 *   TELEGRAM_ALLOWED_CHAT_IDS  CSV de chat_id autorizados (tu chat_id)
 * y `npm install` (grammy) antes de correr. Arranque: `npm start`.
 */
import { Bot } from "grammy";
import { handleMessage } from "./bridge.js";

const token = process.env.TELEGRAM_BOT_TOKEN;
if (!token) {
  console.error("FALTA TELEGRAM_BOT_TOKEN (token de BotFather). Ver .env.example.");
  process.exit(1);
}

/** Confirmaciones pendientes por chat: el próximo SÍ/NO del mismo chat las resuelve. */
const pendingConfirms = new Map<string, (ok: boolean) => void>();
const CONFIRM_TIMEOUT_MS = Number(process.env.CONFIRM_TIMEOUT_MS ?? 300_000); // 5 min

const bot = new Bot(token);

bot.on("message:text", async (ctx) => {
  const chatId = String(ctx.chat.id);
  const text = ctx.message.text.trim();

  // ¿Hay un confirm pendiente para este chat? Entonces este mensaje ES la respuesta SÍ/NO.
  const pending = pendingConfirms.get(chatId);
  if (pending) {
    const yes = /^(s[ií]|si|yes|y|ok|dale|confirmo)$/i.test(text);
    pendingConfirms.delete(chatId);
    pending(yes);
    await ctx.reply(yes ? "✅ Confirmado, ejecutando." : "🚫 Cancelado.");
    return;
  }

  // askConfirm: muestra el dry-run y espera el SÍ del MISMO chat (doble gate).
  const askConfirm = (dryRun: string, reason: string): Promise<boolean> =>
    new Promise<boolean>((resolve) => {
      const timer = setTimeout(() => {
        if (pendingConfirms.get(chatId)) {
          pendingConfirms.delete(chatId);
          resolve(false); // sin respuesta a tiempo => NO ejecuta (GUARDA: default deny)
        }
      }, CONFIRM_TIMEOUT_MS);
      pendingConfirms.set(chatId, (ok) => { clearTimeout(timer); resolve(ok); });
      void ctx.reply(`🔐 Confirmación requerida (${reason})\n\n${dryRun}\n\nResponde SÍ para ejecutar.`);
    });

  const reply = async (msg: string): Promise<void> => { await ctx.reply(msg); };

  await handleMessage(chatId, text, askConfirm, reply);
});

bot.catch((err) => console.error("bridge.telegram error:", err.message));

console.log("Canal de mando de Xe escuchando en Telegram (EXEC_MODE=" + (process.env.EXEC_MODE ?? "read_only") + ")");
void bot.start();
