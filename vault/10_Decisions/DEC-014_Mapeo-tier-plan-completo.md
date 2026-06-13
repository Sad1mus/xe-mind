---
id: DEC-014
titulo: Mapeo tier comercial → plan de entrega — completo (Silver/Gold/Enterprise/Partner)
dueño: Jordy (Sad1mus) — PENDIENTE VEREDICTO
fuente: DEC-006 (qué promete cada tier) × planes reales del producto agente-clinicas (src/plans.ts, src/types.ts: basic⊂growth⊂scale); destilado 2026-06-13
estado: propuesta
lente: global
---
**Decisión (propuesta):** Completar el hueco #17 mapeando los 5 tiers de [[DEC-006]] a los **3 planes de entrega REALES** del producto (`basic ⊂ growth ⊂ scale`, evidenciados en `agente-clinicas/src/plans.ts`), **componiendo módulos** donde el tier promete más de lo que un plan suelto cubre. Lo que ningún plan ni módulo construido cubre **NO se mapea: se bloquea**.

## Evidencia — qué provisiona cada plan real (no inventado)
| Plan | Incluye (verbatim del producto) |
|---|---|
| **basic** | agente + dashboard (en todos) + agendar citas + recordatorios de cita · 1 agente · 1 canal (WhatsApp) |
| **growth** | basic + reporte semanal + ROI dashboard + reseñas Google + recordatorios de vacunas |
| **scale** | growth + rescate de llamadas perdidas |

Ningún plan provisiona multicanal/social, video IA ni agentes ilimitados.

## Tabla candidata tier → plan (PROPUESTA, no aceptada)
| Tier (DEC-006) | Plan por agente | Composición | Estado |
|---|---|---|---|
| **Starter** | `basic` | 1 agente | ✅ firmado ([[DEC-009]]) |
| **Silver** (3 agentes, reporte mensual, sin video) | `basic` | ×3 agentes vía M3 ([[VEREDICTO-002]]) | 🟡 **propuesto** — plan `basic` y M3 ya existen; "reporte mensual" se cubre con el dashboard (incluido en todos) |
| **Gold** (ilimitado, multicanal, video, reporte semanal) | `growth` (cubre el reporte semanal + ROI que Gold promete) | ilimitado vía M3 + multicanal M4 + video M5 | 🚧 **BLOQUEO** — M4 (multicanal) y M5 (video) **no existen** todavía; el plan suelto NO cubre Gold |
| **Enterprise** (todo Gold + SLA + integraciones + account manager + white-glove) | `scale` | Gold + ops humano (SLA/AM/white-glove) | 🚧 **BLOQUEO** — hereda los gaps de Gold (M4/M5) + SLA/account manager/white-glove son **ops humano, no plan de software** |
| **Partner** (white-label, equipo dedicado) | — | white-label + equipo dedicado | 🚧 **BLOQUEO** — white-label **no construido** (gap inventario); equipo dedicado es ops humano |

**Porqué:** desbloquea onboarding/registro para Starter y Silver (los dos verticales-probados-componibles ya), y deja **explícito y honesto** que Gold/Enterprise/Partner aún no son entregables de punta a punta — su mapeo depende de construir M4/M5 y resolver el white-label/ops, no de fabricar un nombre de plan.

**Supuestos:** los planes del producto siguen siendo `basic/growth/scale`; "reporte mensual" de Starter/Silver se considera cubierto por el dashboard (no hay plan "mensual" en el producto, solo el semanal de growth/scale).

**Qué la invalidaría:** que el producto añada/quite un plan (p. ej. uno con multicanal o video); que se construyan **M4 (multicanal)** y **M5 (video)** — eso desbloquearía Gold y cambiaría su fila de 🚧 a un mapeo real; o que [[DEC-006]] cambie lo que promete un tier.

**🚧 Lo que NO fija esta DEC (huecos, no inventar):**
- El mapeo de **Gold/Enterprise/Partner** queda BLOQUEADO hasta construir M4/M5 y resolver white-label + ops humano.
- Si Silver debe usar `basic`×3 o un plan propio: es la decisión humana concreta a ratificar.

**Relaciones:** extiende [[DEC-009]] (la completa; al aceptarse, supersede su parcialidad) · consume [[DEC-006]] · restringida_por [[GUARDA-003]] · composición habilitada por [[VEREDICTO-002]] (M3) · bloqueada por los gaps M4/M5 del megagoal.
