# SPEC-001 · Plataforma de entrega de software a clientes (VPS + capa de agente)

> **Estado:** `spec` (fase 1 de SDD — pendiente de aprobación humana antes de pasar a `design`).
> **Fecha:** 2026-06-14 · **Dueño:** Sad1mus · **Repo:** xe-mind
> Esta spec es la **fuente de verdad**. El código se generará a partir de ella, no al revés.
> Sigue el flujo SDD del CLAUDE.md: `spec → design → tasks → implement`, con gate humano en cada fase.

---

## 1 · Contexto y problema

La agencia (Xe / ZenKai / EtherLabX) necesita **entregar software a medida a clientes** de forma rápida y reusable, sin depender de una plataforma de terceros que introduzca tres riesgos ya identificados en conversación:

1. **Reventa de IA** — usar los modelos incluidos de un proveedor (ej. Abacus SuperComputer) bajo un plan barato choca con rate limits y posibles violaciones de ToS.
2. **Datos del cliente en infra ajena** — incompatible con la GUARDA de soberanía de datos por región (GDPR/EMEA, residencia por país en APAC).
3. **Lock-in** — acoplarse al box y al router de un proveedor encarece y traba la migración.

La hipótesis (DEC pendiente de registrar): **un VPS propio + una capa de agente open source da el mismo resultado funcional con control total, costo menor y sin esos tres riesgos**, a cambio de asumir el rol de sysadmin (hardening + operación).

## 2 · Objetivo

Una **plantilla reusable** que permita: (a) que el ingeniero acceda por SSH a una instancia con poderes de agente IA para construir/desplegar, y (b) que cada cliente acceda únicamente a *su* software (con IA integrada usando **keys propias de la agencia**), aislado de los demás.

> **Criterio de éxito (verificable):** dar de alta un cliente nuevo = un deploy, no un alquiler nuevo. Tiempo objetivo de provisión de un cliente nuevo: **< 30 min** desde plantilla.

## 3 · Requisitos funcionales (RF)

- **RF-1** — Acceso de ingeniero por SSH (solo clave, sin password) a la instancia.
- **RF-2** — Capa de agente IA en la instancia con poderes de shell/build/deploy (candidato: Claude Code headless; alternativas a evaluar en `design`: OpenHands, Aider).
- **RF-3** — PaaS self-hosted para deploy con SSL automático y **una app aislada por cliente** (candidato: Coolify; alternativa: Dokploy).
- **RF-4** — UI de IA de cara al cliente (candidato: LibreChat / Open WebUI), cableada a **API keys propias de la agencia**, nunca a las del proveedor de infra.
- **RF-5** — Cada cliente accede solo a su app, con su dominio/subdominio y su login.
- **RF-6** — Backups propios y restaurables (no dependientes del proveedor del VPS).

## 4 · GUARDAS / Requisitos no funcionales (solo restringen)

- **G-1 · Soberanía de datos** — datos de cliente con residencia obligatoria **no salen de su región**; el substrato global indexa referencias, no copia el dato regulado. (Hereda regla de gobierno multi-continente del CLAUDE.md.)
- **G-2 · Keys propias** — el consumo de IA es **medible y facturable por cliente**; prohibido revender la IA del proveedor de infra.
- **G-3 · Aislamiento** — datos y procesos de un cliente jamás accesibles desde la app de otro (contenedores/Docker por cliente).
- **G-4 · Hardening obligatorio** — firewall, SSH solo por clave, usuario no-root, fail2ban, antes de exponer cualquier app pública. Un agente con poder de shell en un host público es superficie de ataque.
- **G-5 · Portabilidad** — stack estándar (Docker + repo en GitHub + backups propios). Debe poder levantarse en otro VPS/cloud **sin reescribir**. Mide el lock-in: cero dependencias propietarias de un solo proveedor.
- **G-6 · SLA honesto** — el nivel de disponibilidad prometido al cliente debe estar respaldado por la infra elegida y declarado por contrato; nunca prometer uptime que no se controla.

## 5 · Fuera de alcance (de esta spec)

- Entrenamiento o inferencia de modelos propios en GPU local (requiere hardware GPU; otra spec).
- Multi-región activo-activo / failover entre continentes (futuro; aquí: single-VPS por región como base).
- Facturación automatizada al cliente (se asume proceso manual en v0).

## 6 · Decisión de arquitectura propuesta (a ratificar en `design`)

Stack base candidato (NO implementar hasta aprobar `design` + `tasks`):

1. **VPS** (candidato Hetzner, ~€5/mes, ≥2 vCPU / 8 GB / 40 GB) — más recurso que el box de $10 de Abacus y bajo control propio.
2. **Coolify** sobre el VPS → app aislada por cliente, dominio + SSL automáticos.
3. **Claude Code headless** en el VPS como "ingeniero IA" (acceso del ingeniero por SSH).
4. **App del cliente** + **LibreChat** con **API keys de la agencia** (Anthropic/OpenAI).

> El "cerebro" (modelo LLM) NO es open source: se paga por API. Open source es la **capa de agente/orquestación/hosting**, no el modelo.

## 7 · Riesgos

- **R-1** — Costo oculto de operación (hardening + mantenimiento) supera el ahorro vs. plataforma gestionada. *Mitigación:* plantilla de hardening reusable, hecha una vez.
- **R-2** — Un cliente que crece exige SLA/escala que el VPS base no da. *Mitigación:* G-5 (portabilidad) permite migrar sin reescribir.
- **R-3** — Fuga entre clientes por mala configuración de aislamiento. *Mitigación:* G-3, revisión de aislamiento como criterio de aceptación.

## 8 · Criterios de aceptación (verificables)

- [ ] Cliente nuevo aprovisionado desde plantilla en < 30 min (RF, §2).
- [ ] App del cliente A inaccesible (datos y red) desde el contenedor del cliente B (G-3).
- [ ] `nvidia-smi` / dependencia de modelos: el consumo de IA usa keys de la agencia, verificado en logs de facturación (G-2).
- [ ] La misma plantilla levanta en un segundo VPS distinto sin cambios de código (G-5).
- [ ] Checklist de hardening (firewall, SSH-key-only, no-root, fail2ban) pasa antes de exponer público (G-4).

## 9 · Fases siguientes (SDD — pendientes de tu aprobación)

1. **`design`** — elegir definitivamente VPS/PaaS/agente/UI entre candidatos; diagrama de red y aislamiento; plan de backups; checklist de hardening concreto.
2. **`tasks`** — descomponer en tasks chicas con sus tests/criterios.
3. **`implement`** — una task por vez, con verificación.

> **STOP.** Esta es la fase `spec`. Requiere tu revisión y aprobación explícita antes de pasar a `design`. Registrar la hipótesis del §1 como **DEC** al aprobar.
