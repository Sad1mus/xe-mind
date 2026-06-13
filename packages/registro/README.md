# registro — verdad exacta de clientes y proyectos (backbone de administración)

La capa **SQLite "verdad exacta"** que CLAUDE.md §3.1 nombra y que faltaba: el lugar donde Xe
**administra cada cliente y proyecto** de la agencia a través de las 3 lentes (Américas/EMEA/APAC),
con **residencia por región** (§1 + GUARDA-002). Es **precondición de Fase 5** (vender/onboardear
Gold) y **Fase 6** (escala por lente/nicho) — no se puede gestionar Gold en 3 continentes sin esto.

## Cómo cumple el contrato
- **manifest** → `manifest.json`.
- **inputs** → `{ cliente: {nombre, lente, marca, tier, region_datos?, estado?}, proyectos?: [{nombre?, capacidades[], plan_entrega?, estado?}] }`.
- **dry_run()** → muestra el alta (cliente + proyectos), la residencia y los planes; **no escribe**.
- **execute()** → escribe en la SQLite de `REGISTRO_DB` **solo con `--confirm`** (GUARDA-001, GUARDA-005).
- **oracle** → valida la lógica nueva: requeridos, lente/tier válidos, residencia etiquetada,
  mapeo tier→plan (sin inventar) y composición cliente→proyecto. → **ORACLE: PASA**.

## Reglas duras propias
- **Residencia (GUARDA-002):** `region_datos` se deriva de la lente (EMEA → UE/GDPR en-región); la
  política por país queda como hueco. El índice **referencia**, no copia el dato regulado.
- **No inventa el mapeo (GUARDA-003 + DEC-009):** solo `Starter→basic` está firmado; cualquier otro
  tier sin `plan_entrega` explícito se marca `PENDIENTE-#17` — **no se fabrica** un plan.

## Uso
```bash
python3 connector.py oracle
python3 connector.py dry-run
REGISTRO_DB=/tmp/registro_test.db python3 connector.py execute --confirm --json '{...}'
REGISTRO_DB=/tmp/registro_test.db python3 connector.py list
```

## Bloqueos conocidos (no se inventan)
- **Esquema** (campos, estados, ciclo de vida) está **PROPUESTO en [[DEC-013]]** → pendiente VEREDICTO humano.
- **hueco #17:** mapeo tier→plan para Silver/Gold/Enterprise/Partner.
- **hueco #26:** reconciliación lente↔marca↔LATAM (DEC-007 nombra LATAM/EtherLabX; §1 usa Américas/EMEA/APAC).
