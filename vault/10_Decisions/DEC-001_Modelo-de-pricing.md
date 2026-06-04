---
id: DEC-001
titulo: Modelo de pricing — costo × multiplicador regional + fee
dueño: Jordy + socios (pendiente VEREDICTO)
fuente: world/zenkai-pricing-v5-fee-descuentos.html
estado: superada
lente: global
---
> ⚠️ **SUPERADA por [[DEC-006]]** (pricing oficial EtherLabX, 2026-06-04). El modelo ZENKAI v5 (costo×multiplicador + fee=costo×1.5) queda como histórico. EtherLabX asigna **precios explícitos por plan/región**, no derivados de un multiplicador. Se conserva esta nota por trazabilidad.

**Decisión:** El precio standard de un plan = `costo USD × multiplicador regional` (Américas ×8 · EMEA ×6 · LATAM ×3, convertido a moneda local). El **fee único** = `costo × 1.5`. Tanto el fee como el precio mensual se **reducen con el compromiso** (ver DEC-003).

**Porqué:** El precio se deriva del costo real (herramientas + infra), no se inventa — es justificable ante el cliente. El multiplicador por región ajusta a mercado/poder adquisitivo.

**Supuestos:**
- Costos base de referencia (v5): Starter $50 · Silver $75 · Gold $205 · Enterprise $360 / mes.
- Costos fijos cubiertos por el fee: Claude Max $100 · VPS $30 · Dominios $30.
- FX al 3-jun-2026: USD/COP ≈ 3.570 · EUR/USD ≈ 1.16.

**Qué la invalidaría:** que el costo real de servir un plan supere su costo base de referencia (margen comprimido), o que un multiplicador deje el precio fuera de mercado en una región.

**Relaciones:** restringida_por [[GUARDA-004]] (suelo de costo) · deriva_de [[DEC-002]] · parametrizada por [[lentes-regionales]].
