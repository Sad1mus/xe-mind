---
id: DEC-010
titulo: Arquitectura unificada — monorepo Xe (empresa compartida), local-first
dueño: Jordy (Sad1mus) + HaxelGG — empresa compartida
fuente: decisión humana directa (2026-06-04)
estado: aceptada
lente: global
---
**Decisión:** Jordy y HaxelGG son **empresa compartida**. Todo se unifica en **un proyecto, "Xe"** (nombre provisional, [[DEC-007]]), como **monorepo con fronteras internas** (workspaces), NO un bloque indiferenciado:

```
xe/
├── mind/      # cerebro: vault (DEC/GUARDAS), CLAUDE.md, loop
├── packages/  # librería de capacidades componible (módulos reusables)
├── apps/      # productos, anexados UNO A UNO (strangler-fig)
└── infra/     # plantillas de deploy replicables (docker agentes + vercel web + residencia)
```

**Construcción local primero**, como **plantilla replicable desde el día 1** (Docker + config por entorno). El deploy y la consolidación de cuentas se concretan después.

**Propiedad (empresa compartida):** org compartida en los tres planos — GitHub Org + Supabase org **"Zenkai"** (mover el proyecto personal ahí) + Vercel **Team**. Ambos socios = admin. Resuelve el enredo `Sad1mus`/`HaxelGG`/`jordycapital`.

**Porqué:** empresa compartida elimina el riesgo de propiedad; el monorepo con workspaces da unidad **sin acoplar** (cada app despliega independiente); local-first es reversible.

**Qué la invalidaría:** que el monorepo acople productos (un cambio rompe a otros) → volver a multi-repo; o que la residencia obligue a separar despliegues (sí obliga: ver abajo).

**Guardas que NO cambian aunque el código se unifique:**
- **Residencia por región** ([[GUARDA-002]]): el panel EU (`eu-central-1`) NO se mueve a US. Código unificado ≠ datos unificados.
- **Anexión incremental** (strangler-fig, [[DEC-008]]): los productos que facturan (clinics, ecommerce, GJS) entran uno a uno con su oráculo, **no big-bang**.
- **No romper lo que factura.**

**Relaciones:** unifica bajo [[DEC-007]] (Xe paraguas) · realiza [[DEC-008]] (portafolio componible) · gobernada por [[GUARDA-002]].
