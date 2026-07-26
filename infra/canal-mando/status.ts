/**
 * status.ts — Fast-path determinista para "¿cómo va la agencia?".
 *
 * Corre el connector de `reporte` (read-only, <1s) que lee el registro (SQLite via
 * REGISTRO_DB) y devuelve el snapshot de cartera. Evita que Xe explore el repo entero
 * con claude -p (lo que disparaba el timeout). Verdad exacta, cero costo, cero latencia.
 */
import { spawnSync } from "node:child_process";
import { join } from "node:path";

/**
 * Heurística: ¿es una CONSULTA de estado (no una orden operativa)?
 * Un verbo de acción imperativo descarta el fast-path (es una orden → va a Xe con manos).
 * Así "creá un cliente en la agencia" NO se confunde con "¿cómo va la agencia?".
 */
export function isStatusQuery(text: string): boolean {
  const t = text.toLowerCase();
  // Si trae una orden de acción, NO es consulta de estado.
  if (/\b(cre[aá]|d[aá]\s+de\s+alta|ejecut[aá]|us[aá]|corr[eé]|actualiz[aá]|agreg[aá]|escrib[ií]|borr[aá]|elimin[aá]|modific[aá]|dise[ñn][aá]|gener[aá]|deploy|sub[ií]|instal[aá]|mand[aá]|env[ií]|cobr[aá]|firm[aá])/.test(t)) {
    return false;
  }
  return /(c[oó]mo va|c[oó]mo vamos|c[oó]mo est[aá]|c[oó]mo anda|qu[eé]\s+tal\s+va|estado\s+de|marcha\s+de|reporte\s+de|resumen\s+de|cartera)/.test(t);
}

/** Snapshot de cartera leyendo el registro vía el connector de reporte. */
export function getAgencyStatus(repoCwd: string): string {
  const script = join(repoCwd, "packages", "reporte", "connector.py");
  const res = spawnSync("python3", [script, "dry-run"], {
    cwd: repoCwd,
    env: process.env, // REGISTRO_DB viaja en la env (GUARDA-005)
    encoding: "utf8",
    timeout: 15_000,
  });
  if (res.error) return `⚠️ No pude leer el registro: ${res.error.message}`;
  if (res.status !== 0) return `⚠️ El registro respondió con error:\n${(res.stderr || res.stdout || "").trim()}`;
  const out = (res.stdout ?? "").trim();
  if (!out) return "El registro no devolvió datos.";
  // Se quitan las líneas operativas del connector ([inputs]/[execute]) — ruido para el fundador.
  const limpio = out.split("\n").filter((l) => !l.trimStart().startsWith("[")).join("\n").trim();
  return limpio || out;
}
