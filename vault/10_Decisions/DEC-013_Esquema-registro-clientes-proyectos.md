---
id: DEC-013
titulo: Esquema del registro de clientes y proyectos (verdad exacta §3.1)
dueño: Jordy (Sad1mus) — PENDIENTE VEREDICTO
fuente: CLAUDE.md §3.1 (SQLite verdad-exacta) y §1 (3 lentes/residencia); destilado al construir packages/registro/ ([[VEREDICTO-004]])
estado: propuesta
lente: global
---
**Decisión (propuesta):** El registro de administración de Xe (`packages/registro/`) usa este esquema mínimo de verdad exacta, local-first (DEC-010):

- **CLIENTE**: `id` (slug del nombre) · `nombre` · `lente` ∈ {Americas, EMEA, APAC} · `marca` (DEC-007) · `tier` ∈ {Starter, Silver, Gold, Enterprise, Partner} (DEC-006) · `region_datos` (residencia, GUARDA-002) · `estado` ∈ {prospecto, onboarding, activo, pausado, cerrado}.
- **PROYECTO**: `id` · `cliente_id` (FK) · `capacidades[]` (módulos M1..M7 / ids de packages) · `plan_entrega` (DEC-009; no firmado → `PENDIENTE-#17`) · `estado` ∈ {propuesto, en-construccion, entregado, pausado, cerrado}.

**Porqué:** Xe necesita una capa consultable y no-alucinable para administrar cada cliente y proyecto a través de los 3 continentes; sin ella no hay Fase 5 (vender Gold) ni Fase 6 (escala por lente/nicho). El esquema se mantiene mínimo y atado a DEC ya firmadas.

**Supuestos:** los 5 tiers (DEC-006) y las 3 lentes (§1) son estables; el ciclo de vida de `estado` propuesto cubre la operación real de la agencia.

**Qué la invalidaría:** que la operación exija un estado/campo no contemplado (p. ej. contratos, precios cobrados, métricas ROI como columnas propias), o que la reconciliación lente↔marca↔LATAM (hueco #26) obligue a cambiar el enum de `lente`.

**🚧 Lo que NO fija esta DEC (huecos, no inventar):**
- Campos de **contrato/precio cobrado/métricas ROI** (¿columnas propias o módulo aparte M6?) → decisión humana.
- Mapeo tier→plan para Silver/Gold/Enterprise/Partner (hueco #17).
- Reconciliación lente↔marca↔LATAM (hueco #25).

**Relaciones:** consume [[DEC-006]] · consume [[DEC-007]] · consume [[DEC-009]] · bajo [[DEC-010]] · restringida_por [[GUARDA-002]] · probada por [[VEREDICTO-004]].
