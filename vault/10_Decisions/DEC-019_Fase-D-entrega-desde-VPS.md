---
id: DEC-019
titulo: Fase D — Xe orquesta la entrega desde la VPS (traer repo → construir → visto humano)
dueño: Jordy (Sad1mus) — PENDIENTE VEREDICTO
fuente: goal `goal-queue-fase-d-entrega.md` (2026-07-27), sobre productos ya versionados
estado: propuesta
lente: global (ejecución regional)
---
**Decisión (propuesta):** Xe puede, desde la VPS y headless, **traer el código de un producto desde su repo privado** (`repo_fetch`, PAT scope repo read → clone a un workdir local = `CLINICS_REPO`), correr el **discovery** y **armar la entrega en dry-run** (`entrega_dryrun` → payload + comando `nueva_clinica`), y dejarla lista para el **visto humano**. La **construcción es automática y reversible**; el **INSERT en Supabase de producción y el envío al cliente son humanos** (`nueva_clinica` clasificado `outbound`→deny en el gate).

**Reparto (no negociable):**
- **Automático (Xe):** `repo_fetch` (traer producto) · discovery · `entrega_dryrun` (payload + comando, sin ejecutar). Gate: reversible/allow.
- **Humano (visto):** correr `nueva_clinica` (INSERT Supabase) + envío al cliente. Gate: deny hasta OK ([[GUARDA-001]]).

**Porqué:** cierra el hueco que hoy impide que Xe entregue desde la VPS (`CLINICS_REPO` vacío) sin ceder el control de lo irreversible: la parte repetitiva (traer + construir) se automatiza; la parte con dinero/marca (crear la clínica en producción + enviarla) se queda en el humano. Concreta Fase D de [[DEC-010]] con los productos ya en repos propios ([[repos-productos-regionales]]).

**Qué está construido y probado (dry-run, 2026-07-27):** `integrations/clinics/repo_fetch.py` (oracle PASA; clone REAL del privado `Sad1mus/agente-clinicas` OK; PAT enmascarado, no persiste en `.git/config`); `integrations/clinics/entrega_dryrun.py` (oracle PASA; Starter→basic arma el comando, Gold→`PENDIENTE-#17` sin inventar); gate `classify.ts` (`nueva_clinica`→outbound/deny, dry-run→allow; oráculo 20 casos). Runbook: `infra/RUNBOOK-fase-d-entrega.md`.

**Qué falta para el execute real (gates humanos, no inventar):**
1. Setear `CLINICS_REPO` + `GITHUB_PAT` en el `.env` 600 de la VPS.
2. Envs de **Supabase de producción** disponibles para `nueva_clinica` (service key = secreto).
3. **Visto humano por entrega** (INSERT + envío) — nunca automático.
4. Confirmar la **rama por defecto** de agente-clinicas para el clone (hoy activa `feat/frontera-tenant`).

**Qué la invalidaría:** que la entrega (INSERT/envío) se vuelva automática (rompe [[GUARDA-001]]) · que el mapeo tier→plan se fabrique más allá de Starter→basic firmado ([[DEC-009]], [[GUARDA-003]]) · que traer el producto exija copiarlo dentro de xe-mind (rompe [[DEC-010]]) · que el PAT no pueda mantenerse fuera de git/logs.

**Relaciones:** concreta Fase D de [[DEC-010]] · reusa `integrations/clinics` + [[DEC-009]] (Starter→basic) · gobernada por [[GUARDA-001]] (entrega=humano) y [[GUARDA-003]] (no inventar) · consume [[repos-productos-regionales]] (productos versionados) · complementa [[DEC-017]] (pago→construye) y `onboarding-meta`.
