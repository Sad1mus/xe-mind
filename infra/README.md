# infra/ — Plantillas de despliegue replicables

"Replicable en VPS" se hace aquí: estampas una plantilla por cliente/app, **no** un VPS compartido para todo.

## Topología (híbrida por necesidad)
- **Agentes persistentes** (WhatsApp/Baileys, Telegram bot) → **VPS + Docker** (necesitan proceso vivo 24/7; no serverless).
- **Web / paneles / storefronts** (Next.js) → **Vercel** (serverless, global, barato).
- **Datos** → Supabase **por región** (residencia, GUARDA-002).

## Por construir
- `docker-compose.template.yml` — runtime de agentes (parametrizado por cliente/región).
- `vercel/` — config de despliegue web.
- `regions.md` — mapa de residencia por cliente (EU → eu-central-1, etc.).

> Local-first: el mismo compose corre en tu máquina y en el VPS (DEC-010). Lo que pruebas local ES lo que despliegas.
