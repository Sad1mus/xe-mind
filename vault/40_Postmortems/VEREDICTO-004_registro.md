---
id: VEREDICTO-004
titulo: registro — verdad exacta de clientes y proyectos, validada en ejecución real
fecha: 2026-06-13
estado: PASA (oracle + e2e local) · pendiente ratificación humana
---
**Hipótesis probada:** Xe puede tener su capa de **administración** — la "verdad exacta" de CLAUDE.md §3.1 — como un módulo al contrato (`packages/registro/`) que da de alta y consulta CLIENTES y PROYECTOS a través de las 3 lentes (Americas/EMEA/APAC) con residencia por región, **sin inventar criterio**.

**Resultado: ✅ PASA (oracle + e2e local).**
- `oracle` → **PASA**: valida requeridos, lente∈{Americas,EMEA,APAC} y tier∈DEC-006, rechaza lente `LATAM` y tier `Platino`, exige `capacidades` no vacías, etiqueta residencia EMEA (GDPR), mapea `Starter→basic` y deja `Gold→PENDIENTE-#17` (no inventa), y compone cliente→proyecto.
- **e2e real:** `execute --confirm` con `REGISTRO_DB` a una **SQLite local desechable** creó el cliente `klinik-berlin-mitte` (EMEA · ZENKAI · Gold · `region_datos`=UE/GDPR · estado=prospecto) y su proyecto (`caps=[M1,M2,M3]`, `plan_entrega=PENDIENTE-#17`). **Verificado por SELECT** (vía connector y vía `sqlite3` crudo) — 1 fila en `clientes`, 1 en `proyectos`.

**Guardas respetadas:**
- [[GUARDA-001]]: `execute()` solo escribió con `--confirm`; sin él, BLOQUEA.
- [[GUARDA-002]]: `region_datos` etiquetada por lente; el registro referencia, no copia el dato regulado.
- [[GUARDA-003]]: requerido faltante / lente|tier inválido → BLOQUEO; el mapeo no firmado → `PENDIENTE-#17`, no se fabrica.
- [[GUARDA-005]]: ruta de la DB por `env REGISTRO_DB`, cero hardcode. DB de prueba desechable, **no prod**.

**Confianza: alta** para la capa de datos/validación. El **esquema** (campos, estados, ciclo de vida) es **PROPUESTO** en [[DEC-013]] — el criterio lo ratifica el humano.

**Qué deja:** la primera **herramienta de administración** real de Xe — un registro consultable de clientes y proyectos por continente. Es **precondición de Fase 5 y Fase 6**.

**Notas / deuda (huecos, no inventados):**
- **hueco #17:** mapeo tier→plan para Silver/Gold/Enterprise/Partner (hoy solo Starter→basic, DEC-009).
- **hueco #26 (nuevo):** reconciliación lente↔marca↔LATAM (DEC-007 nombra LATAM/EtherLabX; §1 usa Americas/EMEA/APAC — no es 1:1).
- Falta migrar de SQLite local a la residencia real por región cuando se consolide infra (DEC-010).

**Relaciones:** realiza CLAUDE.md §3.1/§1 · propone [[DEC-013]] · gobernado por [[GUARDA-002]] · cumple contrato de `contrato-capacidades` · habilita Fase 5/6 de `.claude/megagoal.md`.
