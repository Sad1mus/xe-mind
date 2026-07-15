# Prompt — CREAR / regenerar el megagoal

> Pegar en Claude Code dentro de `xe-mind`. Autoría del plan, no ejecución. Sirve para crear el megagoal desde cero o reescribirlo cuando el estado cambie.

---

```
Eres Xe, La Mente de la Agencia. Vas a (re)CREAR el megagoal del proyecto en .claude/megagoal.md.

REGLA MADRE: el megagoal se DESTILA del vault, NO se inventa (GUARDA-003). Cada condición de
cierre debe ser FALSABLE y verificable, y citar la DEC/GUARDA/inventario/veredicto que la respalda.

PASO 0 — Lee y ánclate (no asumas, lee):
  - CLAUDE.md (constitución) y vault/MEMORY.md (índice)
  - vault/10_Decisions/*  (en especial DEC-006 pricing/tiers, DEC-008 norte, DEC-009 mapeo, DEC-010 arquitectura)
  - vault/20_Guardas/*    (las restricciones duras)
  - vault/00_System/inventario-portafolio.md  y  contrato-capacidades.md
  - vault/40_Postmortems/* (veredictos: qué YA está cerrado y probado — no re-abrirlo)
  - vault/30_Founders/preguntas-entrevista.md (los huecos abiertos)

PASO 1 — Estructura el megagoal como COLA (no monolito):
  - 🥇 NORTE: el portafolio GOLD activo y funcional (DEC-006), orquestado por Xe, en las 3 lentes.
       Descompón Gold en sus MÓDULOS de capacidad usando el inventario (qué existe ✅ / gap ❌).
  - ▶️ UN solo GOAL ACTIVO a la vez, con condiciones de cierre falsables + VEREDICTO humano.
       Refleja el estado real leyendo los veredictos: lo cerrado va como ✅, no se re-abre.
  - ⏸ Fases EN COLA, cada una con su condición de cierre.
  - 🚧 Decisiones humanas que condicionan el camino (sácalas de los huecos de entrevista).

PASO 2 — Reglas del megagoal:
  - Nada de big-bang: el camino a Gold es por COMPOSICIÓN de módulos al contrato, no monolitos.
  - Cada fase respeta las guardas (dinero/firma, residencia, no-inventar, sin-hardcode, no mover los productos).
  - No inventes precios, nichos ni mapeos que no estén firmados en una DEC; si faltan, ponlos como BLOQUEO.

PASO 3 — Escribe .claude/megagoal.md y commitea (autor Sad1mus). NO ejecutes las fases; solo
  AUTORÍA del plan. Resume en 5 líneas qué quedó como goal activo y por qué.
```

---

**Variante rápida** (si solo quieres actualizar el goal activo tras un veredicto): "Lee los veredictos en vault/40_Postmortems y .claude/megagoal.md; marca como ✅ lo cerrado, promueve la siguiente fase a GOAL ACTIVO con su condición de cierre falsable, y commitea."
