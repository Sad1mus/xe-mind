---
id: DEC-009
titulo: Mapeo tier comercial → plan de entrega — Starter→basic
dueño: Jordy (Sad1mus) — VEREDICTO dado (2026-06-04)
fuente: decisión humana directa ("confirmo dec")
estado: aceptada (parcial — solo Starter)
lente: global
---
**Decisión:** El tier comercial **Starter** ([[DEC-006]]) mapea al plan de entrega **`basic`** del pipeline (`agente-clinicas/scripts/nueva_clinica.ts`). Confirmado por el humano.

**Porqué:** desbloquea el lazo Starter (Fase 2) — la mente ya puede construir el payload de entrega sin inventar el mapeo (resuelve hueco #17 para Starter).

**Supuestos:** el plan `basic` entrega lo que el tier Starter promete (1 agente · 1 canal · panel · booking).

**Qué la invalidaría:** que `basic` no cubra lo prometido en Starter → habría que ampliar el plan o re-mapear.

**⚠️ Parcial:** solo **Starter→basic** está firmado. El mapeo de Silver/Gold/Enterprise/Partner → (`growth`/`scale`/?) sigue abierto — los planes de entrega son 3 y los tiers son 5, no es 1:1. Ver hueco #17 (resto).

**Relaciones:** desbloquea el lazo Starter (`loop/starter_loop_dryrun.py`, `contrato-capacidades`) · consume [[DEC-006]].
