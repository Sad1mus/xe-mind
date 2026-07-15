# Inventario del portafolio — qué existe vs qué falta

> Mapa capacidad-por-capacidad sobre repos REALES (verificado 2026-06-04). El portafolio = librería componible ([[DEC-008]]); cada tier de [[DEC-006]] = un bundle.
> Repos: `agente-clinicas` (clínicas), `ecommerce-ciclismo` (ecommerce), `smc-platform`/orvex (markets + 18 skills).

| Capacidad | Existe en | Estado | Tier mínimo |
|---|---|---|---|
| Agente IA conversacional (texto) | clinics (Baileys + OpenRouter + Supabase, multi-tenant) | ✅ | Starter |
| Canal WhatsApp | clinics | ✅ | Starter |
| Canal Telegram (texto + voz) | ecommerce-ciclismo | ✅ | extra |
| Voz / transcripción (Whisper) | ecommerce (Fase 3, plan) | ⚠️ planeado | Gold |
| Panel/dashboard de cliente | clinics | ✅ | Starter |
| Agendar citas + reminders | clinics | ✅ | Starter |
| Storefront / web Next.js | ecommerce, orvex | ✅ | Silver |
| Ecommerce backend (MedusaJS, Postgres/Redis) | ecommerce-ciclismo | ✅ | vertical ecommerce |
| Pagos Stripe | orvex/smc-platform | ✅ | — |
| Pagos Wompi / ePayco (LATAM) | ecommerce-ciclismo | ✅ | — |
| Diseño/frontend production-grade | orvex `impeccable` + 17 skills | ✅ fuerte | todos |
| Deploy (Vercel / VPS / Docker) | orvex skills + ecommerce docker | ✅ | — |
| Anti-alucinación (datos = verdad, LLM solo interpreta) | clinics + ecommerce (patrón compartido) | ✅ transversal | — |
| Multicanal unificado (web+WhatsApp+social, un cerebro) | — | ❌ **gap** | Gold |
| Multi-agente ilimitado por cliente | clinics (multi-tenant, pero 1 agente/cliente) | ⚠️ parcial | Gold |
| Video IA / cloning | — | ❌ **gap** (no cableado; necesita HeyGen/Higgsfield) | Gold |
| Campañas (voz/email/Meta Ads) | dapta (llamadas/WhatsApp en clinics) | ⚠️ parcial | Gold |
| Analytics / ROI dashboards | clinics (reporte básico) | ⚠️ parcial | Gold |
| Capa inferencia barata (LiteLLM/Ollama "JARVIS") | ecommerce (diseñada, diferida) | ⚠️ diferida | infra/margen |
| SLA / account manager / white-glove | — | ❌ ops humano | Enterprise |
| White-label | — | ❌ **gap** | Partner |
| Markets / TradingView viz | orvex/smc-platform | ✅ (nicho fintech, fuera del core agencia) | — |

## Verticales que existen (todos tuneados a LATAM, no US)
Veterinaria · Dental · Estética (clinics) · Ecommerce ciclismo (ecommerce-ciclismo).

## Repos del socio (HaxelGG) y plataformas adicionales
- `GrupoJuanaSanchez` + `shopify-store-juana-sanchez` — cliente Shopify real → **capacidad Shopify** (alterna a MedusaJS). ✅
- `Portafolio-Landing-Demos` — landings de demo → capacidad de **landing/marketing**.
- `zenkai-super-brain` ("Super Brain made by Zenkai", HTML) — ⚠️ **el socio ya tiene un "cerebro" propio. Riesgo de divergencia con Xe** → reconciliar (hueco #24): ¿se funde en Xe o es separado?
- **Fintech/cripto (fuera del core agencia):** `smc-platform` (markets/TradingView), `ZAT` (fondo de inversión), `midas`/`midas-engine` (trading). Se anotan como adyacentes; **no entran al portafolio agencia sin criterio humano** — su dominio es trading/fintech, no la agencia.

## Veredicto del inventario
- **Starter / Silver: ~80-90% existe** (agente + canal + panel + booking + web + pagos + diseño). Falta orquestación por la mente + tunear a US.
- **Gold/Enterprise/Partner: gaps reales** — multicanal unificado, multi-agente, **video IA**, white-label. Varias "features Gold" (predicción/Jarvis/SuperBrain) eran marketing → verificar antes de venderlas.
- **Reparto sugerido socios:** cada gap = un módulo componible que enchufa al contrato (`contrato-capacidades.md`). Jordy/HaxelGG se reparten módulos; la mente los compone por tier/nicho.

**Relaciones:** realiza [[DEC-008]] · capacidades se entregan bajo [[DEC-005]] · cada módulo cumple el contrato de `contrato-capacidades`.
