/**
 * governance.ts — El gate del canal de mando de Xe.
 *
 * Núcleo framework-agnóstico: NO depende del Agent SDK ni de Telegram.
 * Implementa GUARDA-001 (dinero/firma/envío), GUARDA-006 (topes + kill switch),
 * y la compuerta de confianza del CLAUDE.md §4. Aquí vive el "no" real.
 *
 * Principio: el gate está en código. Ninguna instrucción del system prompt
 * puede saltarlo, porque la decisión de ejecutar NO la toma el modelo aquí.
 */
import { existsSync } from "node:fs";

export type ExecMode = "read_only" | "reversible" | "money_double_gate";

export interface Caps {
  usdPerAction: number;
  usdPerDay: number;
  usdPerClientPerDay: number;
  tokensPerSession: number;
  tokensPerDay: number;
  outboundActionsPerHour: number;
}

/** Toda tool-call del agente se describe como una Action antes de ejecutarse. */
export interface Action {
  tool: string;
  /** "read" | "write_reversible" | "outbound" | "money" — lo decide classify(), no el modelo. */
  kind: ActionKind;
  /** Monto en USD si es de dinero. */
  usd?: number;
  /** Cliente afectado (para tope por cliente). */
  clientId?: string;
  /** Confianza de la mente para ESTA acción (§4): "alta" | "media" | "baja". */
  confidence: "alta" | "media" | "baja";
  /** Resumen humano de qué hará — se le muestra al fundador en el confirm. */
  summary: string;
}

export type ActionKind = "read" | "write_reversible" | "outbound" | "money";

export type Verdict =
  | { decision: "allow" }
  | { decision: "deny"; reason: string }
  | { decision: "needs_confirm"; reason: string; dryRun: string };

/** Estado de consumo de la ventana actual — lo inyecta quien orquesta (no es global mágico). */
export interface Usage {
  usdToday: number;
  usdTodayByClient: Record<string, number>;
  tokensThisSession: number;
  tokensToday: number;
  outboundLastHour: number;
}

export interface GovConfig {
  execMode: ExecMode;
  caps: Caps;
  killSwitchPath: string;
}

/**
 * La compuerta. Devuelve el veredicto SIN ejecutar nada.
 * El orquestador obedece el veredicto: allow→ejecuta, deny→corta, needs_confirm→pregunta al humano.
 */
export function gate(action: Action, usage: Usage, cfg: GovConfig): Verdict {
  // 0. Kill switch (GUARDA-006) — gana sobre todo.
  if (existsSync(cfg.killSwitchPath)) {
    return { decision: "deny", reason: "KILL SWITCH activo — toda ejecución detenida (GUARDA-006)." };
  }

  // 1. Conflicto de confianza (CLAUDE.md §4): confianza BAJA nunca ejecuta sola.
  if (action.confidence === "baja") {
    return { decision: "deny", reason: "Confianza BAJA: la mente se bloquea y escala (§4). No ejecuta." };
  }

  // 2. Lecturas reversibles de bajo riesgo: pasan directo (si el modo lo permite).
  if (action.kind === "read") return { decision: "allow" };

  // 3. Modo de ejecución (rollout por fases, DEC-012).
  if (cfg.execMode === "read_only") {
    return { decision: "deny", reason: "EXEC_MODE=read_only: el canal no escribe en esta fase." };
  }
  if (action.kind !== "write_reversible" && cfg.execMode === "reversible") {
    return { decision: "deny", reason: `EXEC_MODE=reversible: '${action.kind}' requiere fase money_double_gate.` };
  }

  // 4. Topes duros (GUARDA-006). Sin tope configurado => se bloquea, no asume.
  const capMiss = checkCaps(action, usage, cfg.caps);
  if (capMiss) return { decision: "deny", reason: `Tope excedido o no configurado (GUARDA-006): ${capMiss}` };

  // 5. Acciones irreversibles / dinero (GUARDA-001): SIEMPRE dry-run + confirm humano.
  //    El agente no recibe la credencial de dinero hasta el 2º OK (lo maneja el orquestador).
  if (action.kind === "money" || action.kind === "outbound") {
    return {
      decision: "needs_confirm",
      reason: action.kind === "money"
        ? "Acción de DINERO: doble gate humano (GUARDA-001 + confirm del canal)."
        : "Acción de cara afuera (envío/deploy): requiere OK humano (GUARDA-001).",
      dryRun: action.summary,
    };
  }

  // 6. Escritura reversible, confianza alta/media, dentro de tope: ejecuta.
  return { decision: "allow" };
}

function checkCaps(action: Action, usage: Usage, caps: Caps): string | null {
  if (usage.tokensThisSession >= caps.tokensPerSession) return "tokens por sesión";
  if (usage.tokensToday >= caps.tokensPerDay) return "tokens por día";
  if (action.kind === "outbound" && usage.outboundLastHour >= caps.outboundActionsPerHour)
    return "acciones de cara afuera por hora";
  if (action.kind === "money") {
    const usd = action.usd ?? Infinity; // sin monto explícito => bloquea (no inventa)
    if (usd > caps.usdPerAction) return `monto $${usd} > tope por acción $${caps.usdPerAction}`;
    if (usage.usdToday + usd > caps.usdPerDay) return "tope $ por día";
    const c = action.clientId ? (usage.usdTodayByClient[action.clientId] ?? 0) : 0;
    if (action.clientId && c + usd > caps.usdPerClientPerDay) return "tope $ por cliente/día";
  }
  return null;
}
