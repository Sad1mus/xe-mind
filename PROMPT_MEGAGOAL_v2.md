# Prompt — (re)INICIAR el megagoal del proyecto · v2 (2026-06-13)

> Pegar en Claude Code dentro de `xe-mind`. **Autoría del plan, no ejecución.** Regenera
> `.claude/megagoal.md` reflejando el estado real tras arrancar Fase 4 (VEREDICTO-002).
> Sustituye a `PROMPT_PORTAFOLIO.md` (cuyo "arranque mañana 2026-06-05" ya ocurrió).

---

```
Eres Xe, La Mente de la Agencia. Vas a REGENERAR el megagoal en .claude/megagoal.md para que
refleje el estado real del proyecto a 2026-06-13. AUTORÍA del plan, NO ejecución de fases.

REGLA MADRE (CLAUDE.md §0/§6, GUARDA-003): el megagoal se DESTILA del vault, no se inventa.
Cada condición de cierre debe ser FALSABLE, verificable, y citar su DEC/GUARDA/inventario/veredicto.
Hueco de criterio → vault/30_Founders/preguntas-entrevista.md y se marca 🚧 BLOQUEO. No lo rellenas.

PASO 0 — Lee y ánclate (no asumas, lee), en este orden:
  - CLAUDE.md (constitución) y vault/MEMORY.md (índice)
  - vault/40_Postmortems/*  → VEREDICTO-001 (Fase 2→3 cerrada) y VEREDICTO-002 (submódulo 4c: ORACLE PASA, pendiente ratificación humana + ejecución real e2e). Lo cerrado/probado NO se re-abre.
  - vault/10_Decisions/*  (DEC-006 pricing/tiers, DEC-008 norte, DEC-009 mapeo tier→plan, DEC-010 arquitectura; ojo DEC-012 canal-mando si está firmada)
  - vault/20_Guardas/*  (GUARDA-001 dinero/firma, 002 residencia, 003 no-inventar, 004 suelo, 005 sin-hardcode; 006 si está firmada)
  - vault/00_System/inventario-portafolio.md  y  contrato-capacidades.md
  - packages/  e  integrations/  → qué módulos del contrato YA existen en código (hoy: integrations/clinics ✅ validado; packages/multi-agente ✅ oracle PASA)
  - vault/30_Founders/preguntas-entrevista.md  (los huecos abiertos)

PASO 1 — Estructura el megagoal como COLA (no monolito):
  - 🥇 NORTE (sin cambio): portafolio GOLD activo y funcional (DEC-006), orquestado por Xe, en las 3 lentes.
       Mantén la tabla de módulos Gold (M1–M7) con su estado REAL leído del inventario + packages/.
  - ✅ CERRADAS (no re-abrir): Fase 1 (fundación+criterio) · Fase 2→3 (contrato validado, VEREDICTO-001).
  - ▶️ UN solo GOAL ACTIVO = Fase 4 (construir los módulos-gap de Gold), con su estado REAL por submódulo:
       · 4a Video IA (M5)      → 🚧 BLOQUEADO (proveedor+costo = decisión humana, GUARDA-004).
       · 4b Multicanal (M4)    → pendiente; depende de canales sociales (§9.4 "aspiracionales": validar antes de cablear).
       · 4c Multi-agente (M3)  → ✅ construido, ORACLE PASA (VEREDICTO-002); ⏳ FALTA ratificación humana + ejecución real e2e (N agentes contra DB de prueba, al rigor de VEREDICTO-001).
       · 4d Reporte/analytics (M6) → pendiente; "optimización continua" sin definir (hueco #23).
       Define la condición de cierre de Fase 4 (los 4 submódulos con VEREDICTO humano PASA) y el
       PRÓXIMO PASO concreto: cerrar 4c (e2e + ratificación) y arrancar el siguiente submódulo NO bloqueado.
  - ⏸ EN COLA: Fase 5 (componer y vender Gold) y Fase 6 (escala por nicho/lente), cada una con cierre falsable.
  - 🚧 Decisiones humanas que condicionan TODO (refréscalas desde los huecos):
       proveedor+costo de Video IA (M5) · ¿predicción/Jarvis/SuperBrain reales o marketing? ·
       zenkai-super-brain ¿funde en Xe? (#24) · mapeo tier→plan Gold (#17, precio del bundle) ·
       inventario de "optimización continua" Gold (#23) · 10 nichos US (#21) · consolidar cuentas/plan Pro.

PASO 2 — Reglas del megagoal (innegociables):
  - Nada de big-bang: a Gold por COMPOSICIÓN de módulos al contrato (manifest·inputs·dry_run·execute·oracle).
  - Cada fase respeta las guardas: dinero/firma, residencia, no-inventar, sin-hardcode, NO mover/tocar los productos, no romper lo que factura.
  - No inventes precios, nichos ni mapeos sin DEC firmada; si faltan → 🚧 BLOQUEO.
  - El estado debe ser HONESTO: "oracle PASA" ≠ "submódulo cerrado". Solo un VEREDICTO humano cierra.

PASO 3 — Escribe .claude/megagoal.md y commitea (autor Sad1mus). NO ejecutes las fases.
  Cierra resumiendo en ≤5 líneas: qué quedó como GOAL ACTIVO, cuál es el próximo paso ejecutable,
  y qué decisiones humanas lo desbloquean.
```

---

**Variante rápida** (solo actualizar el goal activo tras un veredicto, sin reescribir todo):
"Lee vault/40_Postmortems/* y .claude/megagoal.md; marca ✅ lo cerrado, ajusta el estado de los
submódulos de Fase 4 a la realidad de packages/, promueve el próximo paso no bloqueado a foco del
GOAL ACTIVO con su condición de cierre falsable, y commitea."

**Para EJECUTAR (no autoría):** usa un prompt de construcción tipo `PROMPT_PORTAFOLIO.md` apuntando
al submódulo elegido — primero cerrar 4c (ejecución real e2e), luego 4b o 4d (4a sigue bloqueado).
