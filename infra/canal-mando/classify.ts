/**
 * classify.ts — Traduce una tool-call cruda de Claude Code a la Action tipada que
 * governance.ts entiende (read | write_reversible | outbound | money) + confianza.
 *
 * Es un componente de SEGURIDAD vivo: la heurística de Bash es un punto de partida
 * defensivo (dinero/irreversible-hacia-afuera se marcan; lo desconocido baja la
 * confianza para que el gate lo frene). Endurecer con el uso, nunca aflojar.
 */
import type { Action } from "./governance.js";

// Lecturas y descubrimiento: sin efecto de lado. `ToolSearch` sólo revela schemas de
// tools diferidas — es descubrimiento read-only (antes caía en desconocido→baja→deny).
const READ_TOOLS = new Set(["Read", "Grep", "Glob", "LS", "NotebookRead", "WebFetch", "WebSearch", "ToolSearch"]);
const WRITE_TOOLS = new Set(["Write", "Edit", "MultiEdit", "NotebookEdit"]);

// Dinero y sus hermanos (GUARDA-001): cobrar/firmar/pagar.
const MONEY_RE = /\b(stripe|payout|refund|charge|checkout|invoice|paypal|transfer(?:encia)?|pago|cobr\w*|payment|firma\w*|sign(?:ature)?)\b/i;
// Dinero en nombres de tools MCP (separadas por `__`, sin límites de palabra fiables):
// añade proveedores/facturación que MONEY_RE no cubre. Sólo se aplica a `mcp__*`.
const MCP_MONEY_RE = /(stripe|paypal|payment|payout|refund|charge|checkout|invoice|billing|ramp|cobr|pago|firma)/i;
// Irreversible hacia afuera: deploys, push, envíos, borrados destructivos.
const OUTBOUND_RE = /(\bgit\s+push\b|\brm\s+-[rf]|\bdocker\s+(rm|rmi|kill|stop|system\s+prune|compose\s+down)\b|\bdeploy\b|\bscp\b|\brsync\b|\bssh\b|\bcurl\b[^\n]*-X\s*(POST|PUT|DELETE|PATCH)|\bwget\b[^\n]*--post|\bnpm\s+publish\b|\bgh\s+(pr|release)\b|\bsend\b|\bwhatsapp\b|\bmailx?\b|\bsendmail\b)/i;
// Fulfillment (DEC-017 Dec.4 / GUARDA-001): abrir al público / entrega / envío al cliente = VISTO HUMANO.
// La CONSTRUCCIÓN (provisioning + dry-run de entrega) NO cae aquí. SÍ cae el go-live y la ENTREGA real:
// `nueva_clinica` hace el INSERT en Supabase de producción (irreversible) → siempre visto humano.
const GOLIVE_RE = /(go[-_ ]?live|abrir[-_ ]?(al[-_ ]?)?p[uú]blico|enviar[-_ ]?al[-_ ]?cliente|env[ií]o[-_ ]?al[-_ ]?cliente|entregar[-_ ]?al[-_ ]?cliente|primer[-_ ]?env[ií]o|publicar[-_ ]?(al[-_ ]?)?cliente|nueva_clinica)/i;
// Comandos claramente de solo-lectura.
const READ_CMD_RE = /^\s*(ls|cat|head|tail|less|grep|rg|find|pwd|echo|printf|wc|stat|file|which|type|env|date|whoami|id|uname|git\s+(status|log|diff|show|branch|remote|rev-parse)|docker\s+(ps|logs|images|version|inspect)|python3?\s+\S*connector\.py\s+(oracle|dry-run|list))\b/;

function mk(tool: string, kind: Action["kind"], confidence: Action["confidence"], summary: string): Action {
  return { tool, kind, confidence, summary: summary.slice(0, 120) };
}

function summarize(toolName: string, input: any): string {
  if (toolName === "Bash") return `bash: ${String(input?.command ?? "").slice(0, 100)}`;
  if (input?.file_path) return `${toolName}: ${input.file_path}`;
  return `${toolName}`;
}

export function classify(toolName: string, input: any): Action {
  const summary = summarize(toolName, input);

  if (READ_TOOLS.has(toolName)) return mk(toolName, "read", "alta", summary);
  if (WRITE_TOOLS.has(toolName)) return mk(toolName, "write_reversible", "alta", summary);

  if (toolName === "Bash") {
    const cmd = String(input?.command ?? "");
    if (MONEY_RE.test(cmd)) return mk(toolName, "money", "alta", summary);
    // Go-live/entrega al cliente ANTES de READ/write: es outbound (visto humano), aunque el
    // resto del comando parezca inocuo. La construcción/provisioning NO matchea GOLIVE_RE.
    if (GOLIVE_RE.test(cmd)) return mk(toolName, "outbound", "alta", summary);
    if (OUTBOUND_RE.test(cmd)) return mk(toolName, "outbound", "alta", summary);
    if (READ_CMD_RE.test(cmd)) return mk(toolName, "read", "alta", summary);
    // Bash local no clasificado: reversible (git lo rastrea). Reversible ≠ peligroso.
    return mk(toolName, "write_reversible", "alta", summary);
  }

  if (toolName === "Task") return mk(toolName, "write_reversible", "alta", summary);

  if (toolName.startsWith("mcp__")) {
    if (MCP_MONEY_RE.test(toolName)) return mk(toolName, "money", "alta", summary);
    // MCP desconocido: confianza media (pasa el §4 pero queda marcado).
    return mk(toolName, "write_reversible", "media", summary);
  }

  // Tool desconocida => confianza BAJA => el gate la deniega (§4). No se asume nada.
  return mk(toolName, "read", "baja", summary);
}
