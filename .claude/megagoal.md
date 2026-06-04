# MEGAGOAL — Xe: llegar al portafolio GOLD (el mejor producto)

> Estructura de **cola**: el NORTE es Gold; solo **un goal activo** a la vez, con condiciones de cierre **falsables**; no se avanza sin VEREDICTO humano. Gold se alcanza por **composición de módulos** (no un monolito), porque los tiers son acumulativos (Starter⊂Silver⊂**Gold**) — ver [[DEC-008]].

---

## 🥇 NORTE — Portafolio GOLD activo y funcional, en las 3 lentes, orquestado por Xe

Gold ([[DEC-006]], $1,749/mo) = **Agentes IA ilimitados · Multicanal (web+WhatsApp+social) · Video IA incluido · Reporte semanal · Soporte prioritario + optimización continua.** Es el plan que elige 9 de 10 y el de mayor margen → es el objetivo comercial.

**Gold = bundle de capacidades.** Descomposición vs el inventario real:

| Módulo | Estado hoy | Para Gold |
|---|---|---|
| M1 Agente + WhatsApp + panel + booking | ✅ existe (clinics) | base |
| M2 Web/storefront + diseño production-grade | ✅ existe (orvex/ecommerce) | base |
| M3 Multi-agente / ilimitado por cliente | ❌ **gap** | Gold |
| M4 Multicanal unificado (web + social, un cerebro) | ❌ **gap** | Gold |
| M5 **Video IA** (HeyGen/Higgsfield) | ❌ **gap** | Gold |
| M6 Reporte semanal / analytics ROI | ⚠️ parcial | Gold |
| M7 Optimización continua (priority) | ⚠️ ops + criterio | Gold |

---

## ▶️ GOAL ACTIVO — Fase 2→3: contrato probado en producción (la base de Gold)

**Objetivo:** llevar el lazo (ya probado en dry-run) a **una ejecución real** del bundle base (Starter→`basic`, [[DEC-009]]) — esto valida el **contrato de capacidades** sobre el que se enchufan TODOS los módulos Gold.

**Condición de cierre (falsable):** la mente hace discovery→cotización→propone execute; **un humano aprueba el cobro/creación** y el asistente queda vivo. "La mente lo hizo; yo solo firmé." Sin tocar lo que ya factura (strangler-fig); MCP read-first; `execute()` tras OK humano ([[GUARDA-001]]).

**Progreso:** ✅ conector `integrations/clinics/` construido (cumple contrato; `oracle PASA`; dry-run cotiza+payload; `execute` frenado por GUARDA-001). Falta solo la **ejecución real**: `export CLINICS_REPO=<agente-clinicas>` + Supabase destino (el conectado es de HaxelGG/org Zenkai → **requiere su OK**) + correr `execute --confirm`.

**Bloqueos humanos (no inventar — [[GUARDA-003]]):** designar Supabase destino (¿prueba o el de HaxelGG con su OK?). Prompt: `PROMPT_CONTINUAR.md`.

---

## ⏸ EN COLA hacia Gold (no empezar sin cerrar el anterior)

- **Fase 4 — Construir los módulos-gap de Gold**, cada uno al **contrato de capacidades** (manifest/dry_run/execute/oracle), probado con su oráculo, **sin romper lo que factura**:
  - 4a **Video IA** (M5) — el gap más visible de Gold. Definir proveedor (HeyGen/Higgsfield) y módulo.
  - 4b **Multicanal unificado** (M4) — web + social sobre el mismo cerebro del agente.
  - 4c **Multi-agente / ilimitado** (M3) — del 1-agente-por-cliente a N.
  - 4d **Reporte semanal + analytics ROI** (M6).
  - **Gate de honestidad:** verificar si "predicción / Jarvis / SuperBrain" (nombres de marketing ZENKAI) existen como tecnología real; si no, definirlos como módulo o **no venderlos**. La mente no vende lo que no existe.
  - Cierre de cada submódulo: corre en dry_run + execute con OK + el oráculo confirma.

- **Fase 5 — Componer y vender Gold.** Bundle Gold completo (M1–M7) + **un onboarding Gold real** con OK humano. Mapeo tier→plan para Gold (extender [[DEC-009]], hoy solo Starter→basic). Cierre = **Gold activo y funcional, cliente real aprobado**, replicable en las 3 lentes.

- **Fase 6 — Escala y autonomía supervisada.** Replicar Gold por nicho (los 10 US, una vez elegidos) y por lente regional; autonomía graduada bajo guardas.

---

## 🚧 Decisiones humanas que condicionan el camino a Gold (la mente NO las inventa)
- Inventario oficial de capacidades Gold (hueco #23) — qué incluye exactamente "optimización continua".
- Proveedor de Video IA y su costo (afecta suelo de costo, [[GUARDA-004]]).
- Mapeo tier→plan para Silver/Gold (hueco #17; DEC-009 solo cubre Starter).
- ¿"predicción/Jarvis/SuperBrain" existen o eran marketing? (gate Fase 4)
- Migración de `zenkai-super-brain` (HaxelGG) a Xe (hueco #24).

*Refinar con `/goal-queue`. Una fase = un VEREDICTO humano que la cierra. Gold se gana módulo a módulo, no de un salto.*
