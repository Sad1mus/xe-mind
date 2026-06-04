# apps/ — Productos (anexados uno a uno, strangler-fig)

Cada producto es una app independiente que **compone** módulos de `packages/` y se **despliega por separado** (no se acopla a las demás).

> Vacío por ahora. Los productos que ya facturan se anexan **incrementalmente** (DEC-010), con su oráculo, **sin romper lo que factura** (DEC-008). NO mover todo de golpe.

Cola de anexión (candidata): `clinics/` (agente-clinicas) · `ecommerce/` (ecommerce-ciclismo) · `gjs/` (Grupo Juana Sanchez). Cada anexión: copiar → cumplir contrato → oráculo confirma paridad → cambiar el flujo.

**Residencia:** cada app declara su región; los datos regulados no cruzan (GUARDA-002). El panel GJS vive en EU.
