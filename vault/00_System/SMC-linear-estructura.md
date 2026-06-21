# SMC — Estructura en Linear

> **Confirmación operativa · 2026-06-21.** Volcado de [[SMC-entrega-pendientes]] a Linear
> vía MCP oficial, bajo [[DEC-015]] (Linear = capa de coordinación). Linear es coordinación,
> NO fuente de verdad: la verdad sigue siendo la nota de auditoría + el repo. Esto es status,
> no una DEC.

**Workspace:** `zenkai-growth-systems` · **Team:** Zenkai (`ZEN`)

## Project
**SMC — Plataforma de Visualización de Mercados**
`https://linear.app/zenkai-growth-systems/project/smc-plataforma-de-visualizacion-de-mercados-3bb863c04afa`
Estado declarado: demo técnica funcional, **NO entregable** a cliente de pago.

## Issues (7) — desde la nota de auditoría

### Bloqueantes (label `bloqueante`)
| ID | Título | Prioridad |
|---|---|---|
| ZEN-5 | Stripe hard-locked a TEST mode → no factura dinero real | Urgent |
| ZEN-6 | Sin páginas legales (Términos / Privacidad / Reembolsos) | Urgent |
| ZEN-7 | Sin panel de admin (ruta /admin + UI) | High |
| ZEN-8 | Bug — pago único duplica filas en subscriptions | High |

### Deseables (label `deseable`)
| ID | Título | Prioridad |
|---|---|---|
| ZEN-9 | Bug — customers Stripe huérfanos si se abandona el checkout | Low |
| ZEN-10 | Sin vercel.json → env vars a mano, deploy sin versionar | Low |
| ZEN-11 | /precios no existe como ruta (discrepancia con la spec) | Low |

## Milestone
**Entrega comercial** — lo mínimo para que SMC pueda cobrar dinero real y entregarse.
- Incluye: **ZEN-6 → ZEN-5 → ZEN-8** (orden por dependencia: legales destraban Stripe live; el bug de pago único se cierra antes de que entre plata real).
- **Excluye ZEN-7** (admin) hasta cerrar con HaxelGG si está en scope del MVP.
- **Sin `targetDate`**: ZEN-5/7 dependen de decisiones humanas (cuenta Stripe live, scope) — no se inventa fecha ([[GUARDA-003]]).

## Notas
- Issues con hueco humano (ZEN-5, ZEN-7) apuntan a [[preguntas-entrevista]] — no se inventan precios ni scope.
- Sin push: este volcado es en Linear (no toca git). La nota del vault sí queda para commitear con tu OK.
- Regenerar cuando cambie el estado del repo `Sad1mus/smc-platform`.

---
*Fuente: [[SMC-entrega-pendientes]] (auditoría 2026-06-20). Operado bajo [[DEC-015]] · [[GUARDA-001]].*
