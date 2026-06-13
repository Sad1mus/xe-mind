---
id: VEREDICTO-005
titulo: onboarding — flujo discovery→cotización→alta→entrega, validado en ejecución real
fecha: 2026-06-13
estado: PASA (oracle + e2e local) · pendiente ratificación humana
---
**Hipótesis probada:** Xe puede ejecutar el **norte v1** (CLAUDE.md §9.2) — discovery → cotización → onboarding — como un módulo al contrato (`packages/onboarding/`) que **compone** `registro` y `clinics` sin reimplementarlos, autónomo salvo cobrar/firmar/enviar.

**Resultado: ✅ PASA (oracle + e2e local).**
- `oracle` → **PASA**: bloquea discovery incompleto, lente `LATAM` y tier `Platino`, `APAC` sin marca firmada y capacidades vacías; la cotización **no inventa** (EMEA/Silver → CONFIRMAR, Americas/Gold → USD 1,749); el alta compuesta es coherente (cliente↔proyecto, marca EMEA=ZENKAI); la entrega da `Starter→basic` (payload) y `Gold→PENDIENTE-#17` (no fabrica).
- **e2e real:** `execute --confirm` con `REGISTRO_DB` a una SQLite local desechable dio de alta el cliente `klinik-berlin-mitte` (EMEA·ZENKAI·Gold·UE/GDPR·prospecto) y su proyecto (`caps=[M1,M2,M3]`, `plan_entrega=PENDIENTE-#17`), **verificado por SELECT** (connector + `sqlite3` crudo).

**Guardas respetadas:**
- [[GUARDA-001]]: `execute()` solo dio de alta con `--confirm`; **no cobró, no firmó, no envió** — dejó el comando de creación del producto como siguiente paso (con su propio `--confirm` en clinics).
- [[GUARDA-003]]: discovery/lente/tier inválidos → BLOQUEO; precio no publicado → `CONFIRMAR`; mapeo no firmado → `PENDIENTE-#17`.
- [[GUARDA-005]]: la DB del registro sale de `env REGISTRO_DB`, sin hardcode; DB de prueba desechable, no prod.

**Confianza: alta** para el flujo de captación→alta. El cobro/firma/envío queda fuera por diseño (humano).

**Qué deja:** el flujo de punta a punta con que Xe **opera comercialmente** la agencia — base directa de **Fase 5** (componer y vender Gold).

**Notas / deuda (huecos, no inventados):**
- **#14** precios locales no publicados (todo salvo Gold US/EU) → `CONFIRMAR`.
- **#17** entrega solo para Starter→basic; otros tiers → `PENDIENTE-#17`.
- **#26** lente APAC sin marca firmada.
- ⚠️ discovery hoy ceñido a verticales de clinics (vet/dental/estética) por reusar su validación; ampliar cuando haya más productos.

**Relaciones:** realiza CLAUDE.md §9.2 (norte v1) · compone [[VEREDICTO-004]] (registro) y [[VEREDICTO-001]] (clinics) · gobernado por [[GUARDA-001]] · habilita Fase 5 de `.claude/megagoal.md`.
