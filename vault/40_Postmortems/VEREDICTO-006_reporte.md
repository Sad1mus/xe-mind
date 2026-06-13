---
id: VEREDICTO-006
titulo: reporte (M6) — cockpit de cartera, validado leyendo el registro
fecha: 2026-06-13
estado: PASA (oracle + e2e local) · parcial por diseño (ROI #23) · pendiente ratificación humana
---
**Hipótesis probada:** Xe puede tener su **cockpit de administración** (módulo M6) como un módulo al contrato (`packages/reporte/`) que lee la **verdad exacta** del registro (§3.1) y agrega el estado de la agencia, **sin inventar** las métricas que aún no tiene.

**Resultado: ✅ PASA (oracle + e2e local).**
- `oracle` → **PASA**: sobre fixtures deterministas, cuentas por lente/tier/estado correctas (3 clientes, EMEA=2/Americas=1), proyectos por plan_entrega (basic=1, PENDIENTE-#17=1), filtro `lente=EMEA` (2 clientes/1 proyecto), ROI = `PENDIENTE-#23` (no inventado), lente `LATAM` → BLOQUEO.
- **e2e real:** se sembraron 3 clientes en 2 lentes/tiers en una SQLite local **usando `packages/registro`**; `reporte dry_run` produjo el reporte agregado (total y filtrado por lente); `execute --confirm` persistió el snapshot a `REPORTE_OUT` — **verificado con `cat`**.

**Guardas respetadas:**
- [[GUARDA-001]]: `execute()` persiste el snapshot tras `--confirm`; **NO lo envía al cliente** (enviar es humano).
- [[GUARDA-002]]: agrega por lente/region; cuenta, no extrae el dato regulado.
- [[GUARDA-003]]: las métricas de ROI (ingresos/citas/conversión) salen `PENDIENTE-#23`; no se fabrican.
- [[GUARDA-005]]: DB por `env REGISTRO_DB`, snapshot por `env REPORTE_OUT`. Sin hardcode.

**Confianza: alta** para el reporte de **cartera**. El reporte de **ROI** es parcial por diseño.

**Qué deja:** la herramienta con que Xe **ve la agencia** (clientes/proyectos por continente). Cierra el lado cartera de M6.

**Notas / deuda (huecos, no inventados):**
- **#23:** métricas de ROI requieren (a) conectar a datos de producto (Supabase de clinics, etc., bajo GUARDA-002) y (b) definición humana de KPIs.

**Relaciones:** realiza M6 (lado cartera) del megagoal · compone [[VEREDICTO-004]] (registro) · gobernado por [[GUARDA-001]]/[[GUARDA-002]] · cumple contrato de `contrato-capacidades`.
