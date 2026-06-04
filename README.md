# Xe — La Mente de la Agencia Global

**Xe es el cerebro que opera y gobierna una agencia de IA global.** Es la **fusión total de las agencias de tres continentes** —ZENKAI (Europa), EtherLabX (LATAM) y Américas— unificadas y orquestadas por una sola mente que decide, cotiza, entrega y rinde cuentas con el criterio de sus fundadores. Todo el desarrollo de la agencia vive aquí.

No es un asistente que responde. Es un sistema que **decide con acertación**: trae el conocimiento relevante, mide su coherencia y actúa solo cuando ese criterio lo respalda — o se detiene y pregunta cuando no. La confianza es un número que calcula, no una sensación.

## Qué hace
- **Discovery → cotización → onboarding** de clientes en las tres regiones, con pricing y criterio propios.
- **Orquesta el portafolio** (asistentes de WhatsApp, ecommerce, web, automatización, video…) como una **librería de capacidades componible**: cada plan comercial es un bundle, cada nicho una plantilla.
- **Crece en paralelo**: los socios construyen capacidades; un contrato común deja que la mente las absorba sin que se pisen.

## Cómo piensa (lo que la hace seria, no un chatbot)
1. **No inventa.** Si le falta criterio, se **bloquea y lo pide**. La que adivina deja de ser fiable.
2. **Tres lentes regionales** bajo un núcleo de método compartido; si dos chocan, **escala — no promedia**.
3. **Nunca toca dinero sin un humano.** Redacta cotizaciones, contratos y mensajes; cobrar, firmar y enviar exige OK humano.
4. **Datos = verdad.** Stock, precios y métricas salen de la base, nunca de una alucinación.

## Estructura (orquestador Xe — empresa compartida, ver `vault/10_Decisions/DEC-010`)
Xe **integra los productos donde viven; NO los mueve ni los absorbe.** El cerebro y los conectores viven aquí; los productos quedan en sus repos.
```
xe-mind/
├── CLAUDE.md · vault/ · loop/ · .claude/   # 🧠 el cerebro (criterio + plan + lazos)
├── packages/      # librería de capacidades componible (módulos reusables al contrato)
├── integrations/  # conectores a los productos externos (clinics, ecommerce, gjs…) — no los productos
└── infra/         # plantillas de deploy replicables (docker agentes + vercel web + residencia)
```
- **`CLAUDE.md`** — la constitución operativa (gana sobre cualquier impulso del modelo).
- **`vault/`** — criterio humano enlazado: decisiones (`10_Decisions`), guardas (`20_Guardas`), fundadores (`30_Founders`), sistema/contrato (`00_System`).
- **`.claude/megagoal.md`** — el plan por fases (norte = Gold) con condiciones falsables.
- **`packages/` · `integrations/` · `infra/`** — el orquestador, local-first y replicable. Nada de cuentas hardcodeado (GUARDA-005) → migrar al Team/Org es trivial.

## Principios irrenunciables
**No destruir** (la red son tests + guardas) · **No inventar** (hueco → bloqueo) · **No mentir** (reporta el estado real).

## Estado
**Fase 2** — el lazo Starter (discovery → cotización → entrega) probado en dry-run; consolidando el portafolio en capacidades componibles. Construcción por fases: criterio → contrato → producción → autonomía supervisada. *Guardrails primero, autonomía al final.*

---
*El método epistémico (decisiones falsables, guardas, veredictos) está probado en otros dominios; Xe lo aplica como proyecto propio para gobernar la agencia global.*
