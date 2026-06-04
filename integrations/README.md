# integrations/ — Conectores a los productos externos

Xe es un **orquestador**: integra los productos **donde viven** (sus repos quedan intactos). Aquí van los **conectores** —no los productos— que dejan a la mente hablar con cada uno por su API/MCP/contrato.

> ⚠️ Xe **NO absorbe ni mueve** los productos existentes (clinics, ecommerce-ciclismo, GJS, smc…). Quedan en sus repos. Aquí solo vive el adaptador que cumple el `contrato-capacidades` y traduce hacia el producto externo.

Cada conector:
- **NO hardcodea** credenciales/refs/IDs de cuenta → todo en `env`/config (GUARDA-005). Así la migración al Team/Org es trivial.
- Cumple el contrato: `manifest · inputs · dry_run() · execute() · oracle`.
- Declara la **región** del producto (residencia, GUARDA-002).

Conectores candidatos: `clinics/` (→ agente-clinicas/Supabase) · `ecommerce/` (→ Medusa) · `gjs/` (→ Shopify) · `web/` (→ Vercel).
