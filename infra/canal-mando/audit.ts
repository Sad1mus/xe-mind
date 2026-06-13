/**
 * audit.ts — Log append-only de cada decisión del canal (GUARDA-006).
 *
 * "Depurar = leer el historial." Cada acción queda como una línea NDJSON
 * inmutable: qué se decidió, con qué confianza, quién confirmó, qué salió.
 * Es la audit-chain del CLAUDE.md §4 a nivel del canal de mando.
 */
import { appendFileSync } from "node:fs";
import type { Action, Verdict } from "./governance.js";

export interface AuditEntry {
  ts: string;              // ISO 8601 — lo estampa el orquestador (no Date.now() en código resumible)
  chatId: string;
  teatro: string;
  action: Action;
  verdict: Verdict;
  confirmedBy?: string;    // chat_id del humano que dio el 2º OK, si aplica
  result?: "ok" | "error";
  error?: string;
}

export function audit(path: string, entry: AuditEntry): void {
  appendFileSync(path, JSON.stringify(entry) + "\n", "utf8");
}
