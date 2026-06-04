---
id: DEC-010
titulo: Xe = orquestador nuevo que INTEGRA (no absorbe); monorepo, empresa compartida, local-first
dueño: Jordy (Sad1mus) + HaxelGG — empresa compartida
fuente: decisión humana directa (2026-06-04)
estado: aceptada
lente: global
---
**Decisión:** Jordy y HaxelGG son **empresa compartida**. **Xe es un orquestador NUEVO que integra los productos existentes donde viven — NO los mueve ni los absorbe.** Lo que ya está creado (agente-clinicas, ecommerce-ciclismo, GJS, smc…) **se queda en su repo, intacto.** Xe se construye como **un proyecto local conectado a GitHub** (`xe-mind`), monorepo con fronteras internas:

```
xe-mind/
├── mind/ (raíz: vault, CLAUDE.md, loop)  # cerebro: criterio + plan + lazos
├── packages/      # librería de capacidades componible (módulos reusables)
├── integrations/  # CONECTORES a los productos externos (no los productos)
└── infra/         # plantillas de deploy replicables (docker agentes + vercel web + residencia)
```

**Construcción local primero**, como plantilla replicable desde el día 1 (Docker + config por entorno).

**Migración futura al Team/Org = barata** por diseño: transferir repo (GitHub) + transferir proyectos (Supabase/Vercel, el `ref` no cambia) + cambiar `env`. **Condición:** nada de cuentas/refs hardcodeado ([[GUARDA-005]]).

**Propiedad (empresa compartida):** org compartida — GitHub Org + Supabase org **"Zenkai"** + Vercel **Team**, ambos socios admin. Resuelve el enredo `Sad1mus`/`HaxelGG`/`jordycapital`.

**Porqué:** Xe orquestando-en-su-sitio evita el big-bang de mover repos que facturan; el monorepo da unidad al orquestador sin acoplar los productos (viven afuera).

**Qué la invalidaría:** que integrar-en-su-sitio resulte más frágil que absorber (poco probable); que la residencia obligue a separar despliegues (sí obliga).

**Guardas:** residencia por región ([[GUARDA-002]]) · sin hardcodeo de cuentas ([[GUARDA-005]]) · no romper lo que factura · no mover lo creado.

**Relaciones:** unifica bajo [[DEC-007]] · realiza [[DEC-008]] (portafolio componible) · gobernada por [[GUARDA-002]] y [[GUARDA-005]].
