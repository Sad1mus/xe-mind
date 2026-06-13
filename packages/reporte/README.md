# reporte (M6) — cockpit de cartera

El módulo **M6** de Gold: el reporte con que Xe ve el estado de la agencia, leyendo la **verdad
exacta** del `registro` (CLAUDE.md §3.1). **Compone** `packages/registro` (su schema y su DB);
no lo reimplementa.

## Qué reporta hoy (real) vs pendiente
- ✅ **Cartera:** clientes por lente/tier/estado · proyectos por estado/plan_entrega · con filtro por lente.
- 🚧 **ROI** (ingresos, citas, conversión): `PENDIENTE-#23` — requiere datos de producto (Supabase de
  clinics, etc.) **y** definición humana de KPIs. **No se inventa** (GUARDA-003).

## Cómo cumple el contrato
- **inputs** → `{ periodo, lente?∈{Americas,EMEA,APAC} }`.
- **dry_run()** → lee el registro (`REGISTRO_DB`) y muestra el reporte agregado. No escribe ni envía.
- **execute()** → solo con `--confirm`: persiste el snapshot a `REPORTE_OUT`. **NUNCA lo envía al cliente** (GUARDA-001).
- **oracle** → sobre fixtures deterministas: cuentas por lente/tier/estado correctas, filtro por lente, ROI `PENDIENTE-#23`, lente inválida bloquea.

## Uso
```bash
python3 connector.py oracle
REGISTRO_DB=/tmp/reg.db python3 connector.py dry-run --json '{"periodo":"2026-W24","lente":"EMEA"}'
REGISTRO_DB=/tmp/reg.db REPORTE_OUT=/tmp/rep.md python3 connector.py execute --confirm
```

## Para cerrar M6 completo (no inventar)
1. **Conectar a datos de producto** (lectura de las DB de los productos, respetando GUARDA-002).
2. **Definir los KPIs de ROI** (hueco #23) — decisión humana.
