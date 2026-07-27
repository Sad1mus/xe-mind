# Memoria — Xe (La Mente de la Agencia)

Índice del vault. Una línea por nota. El detalle vive en cada archivo, no aquí.

## Sistema
- [Handoff de franja](00_System/handoff.md) — **estado vivo (2026-06-13):** hecho/espera-humano/bloqueado/próximo paso. Leer al despertar (§7)
- [Convenciones del vault](00_System/conventions.md) — formato de DEC/GUARDA/VEREDICTO; reglas duras (falsabilidad, citar fuente, hueco≠invento)
- [Inventario del portafolio](00_System/inventario-portafolio.md) — capacidad×repo: qué existe vs gaps; Starter/Silver ~90% existe, Gold+ con gaps (video, multicanal, white-label)
- [Contrato de capacidades](00_System/contrato-capacidades.md) — interfaz manifest/inputs/dry_run/execute/oracle; habilita construcción paralela; lazo probado
- [Repos de productos regionales](00_System/repos-productos-regionales.md) — registro que Xe orquesta (DEC-010: integra donde viven). **3 productos versionados en repos privados** (2026-07-27): `Sad1mus/zenkai-agente-wa` (con transporte Cloud API), `Sad1mus/juana-agente-wa`, `Sad1mus/agente-clinicas` (ya existía, es nuestro no de HaxelGG). **Falta (gate humano):** setear `ZENKAI_REPO`/`JUANA_REPO`/`CLINICS_REPO` + `GITHUB_PAT` en la VPS para que Xe orqueste headless. ⚠️ teléfono real quedó en historial de zenkai/juana (HEAD limpio; purga = decisión humana)
- [Onboarding Meta Tech Provider](00_System/onboarding-meta-tech-provider.md) — **GATE HUMANO:** checklist para habilitar Embedded Signup (Tech Provider + App Review); Xe no puede, requiere 5 datos de vuelta (App ID/Secret, config_id, Graph version, dominio callback). Desbloquea `goal-queue-embedded-signup.md`
- [SMC — qué falta para entregar](00_System/SMC-entrega-pendientes.md) — **auditoría 2026-06-20:** NO está "próximo a entregar" (es demo técnica). Ingeniería sólida (RLS, webhooks firmados, CI/tests); bloqueantes: Stripe en TEST forzado (no factura live), sin páginas legales, sin panel admin, bug pago único duplica filas
- [SMC — estructura en Linear](00_System/SMC-linear-estructura.md) — **2026-06-21:** volcado a Linear (team Zenkai, Project SMC) bajo DEC-015; 7 issues ZEN-5..11 (4 bloqueantes + 3 deseables). Linear = coordinación, no fuente de verdad
- Lazo Starter (dry-run ejecutable): `loop/starter_loop_dryrun.py` — discovery→quote→payload→STOP en GUARDA-001

## Integraciones (conectores a productos externos)
- [clinics](../integrations/clinics/README.md) — conector a `agente-clinicas`; contrato cumplido (inputs/dry_run/execute/oracle); `oracle PASA`; execute tras OK humano + env CLINICS_REPO. Pendiente ejecución real (Supabase de HaxelGG → su OK)

## Decisiones (DEC)
- [DEC-008 Norte — agencia global](10_Decisions/DEC-008_Norte-agencia-global.md) — **aceptada (norte):** repo = cerebro orquestador de agencia global; portafolio = librería componible; tiers acumulativos; plantillas 10 nichos US (sin definir aún)
- [DEC-007 Arquitectura de marca — Xe](10_Decisions/DEC-007_Arquitectura-de-marca-Xe.md) — **aceptada (provisional):** Xe = mente paraguas (Jordy/Sad1mus + socio/HaxelGG); ZENKAI=Europa · EtherLabX=LATAM · Américas=por definir
- [DEC-010 Xe = orquestador que integra](10_Decisions/DEC-010_Arquitectura-monorepo-Xe.md) — **aceptada:** empresa compartida; Xe **integra los productos donde viven, NO los mueve**; monorepo (mind/packages/integrations/infra), local-first; migración al Team/Org trivial si no se hardcodea
- [DEC-019 Fase D — entrega desde la VPS](10_Decisions/DEC-019_Fase-D-entrega-desde-VPS.md) — **propuesta:** Xe trae el producto desde su repo (`repo_fetch`+PAT) y arma la entrega en **dry-run** (`entrega_dryrun`: Starter→basic, Gold→PENDIENTE); el INSERT en Supabase + envío = **visto humano** (`nueva_clinica`→gate deny). Construido+probado (oracles PASA, gate 20 casos). Falta (gate humano): setear `CLINICS_REPO`+`GITHUB_PAT` en VPS + Supabase prod + OK por entrega
- [DEC-015 Linear = capa de coordinación](10_Decisions/DEC-015_Linear-capa-de-coordinacion.md) — **propuesta (pendiente ratificación HaxelGG):** issues/ciclos/roadmap en Linear vía MCP oficial (`mcp.linear.app/mcp`); git sigue siendo fuente de verdad (DEC/GUARDA/VEREDICTO no se mueven); descarta Huly; restringida_por [[GUARDA-002]]; contextualiza [[DEC-010]]
- [DEC-009 Mapeo tier→plan](10_Decisions/DEC-009_Mapeo-tier-plan-entrega.md) — **aceptada (parcial):** Starter→`basic`; resto del mapeo pendiente
- [DEC-013 Esquema del registro](10_Decisions/DEC-013_Esquema-registro-clientes-proyectos.md) — **propuesta (pendiente VEREDICTO):** esquema cliente/proyecto (lente, marca, tier, region_datos, estado) de `packages/registro/`; campos contrato/precio/ROI sin fijar; probada por [[VEREDICTO-004]]
- [DEC-014 Mapeo tier→plan completo](10_Decisions/DEC-014_Mapeo-tier-plan-completo.md) — **propuesta (pendiente VEREDICTO):** completa #17 con planes reales del producto (basic⊂growth⊂scale); Silver→basic×3 (M3); Gold/Enterprise/Partner 🚧 BLOQUEO (faltan M4/M5/white-label); extiende [[DEC-009]]
- [DEC-012 Canal de mando de Xe](10_Decisions/DEC-012_Canal-de-mando-Xe.md) — **propuesta (pendiente VEREDICTO):** operar Xe por Telegram (chat_id allowlist) → Claude Code headless en infra propia; dinero con DOBLE GATE; gate en código; rollout por fases. Ref: `infra/canal-mando/`
- [DEC-006 Pricing oficial EtherLabX](10_Decisions/DEC-006_Pricing-oficial-EtherLabX.md) — **AUTORITATIVA (aceptada)**: 5 planes (Starter $399/Silver $699/Gold $1,749/Enterprise $2,999/Partner desde $5,000) + onboarding por hitos + add-ons + Gold por región
- [DEC-001 Modelo de pricing](10_Decisions/DEC-001_Modelo-de-pricing.md) — ⚠️ SUPERADA por DEC-006 (modelo ZENKAI ×8/×6/×3, histórico)
- [DEC-002 Filosofía de cobro](10_Decisions/DEC-002_Filosofia-de-cobro.md) — ✅ aceptada (corroborada por DEC-006): suelo, por valor/ROI, MRR/LTV
- [DEC-003 Cap de fundadores](10_Decisions/DEC-003_Cap-fundadores-lanzamiento.md) — 🚫 RETIRADA (VEREDICTO): lanzamiento ZENKAI, no aplica
- [DEC-004 Flujo de discovery](10_Decisions/DEC-004_Flujo-de-discovery.md) — ✅ aceptada: cuestionario mínimo (patrón 10 preguntas clínicas), time-to-value
- [DEC-005 Estándar de entrega](10_Decisions/DEC-005_Estandar-de-entrega.md) — ✅ aceptada: production-grade, impeccable como criterio de calidad

## Guardas
- [GUARDA-001 Dinero y firma](20_Guardas/GUARDA-001_Dinero-y-firma.md) — redacta sí, cobrar/firmar/enviar requiere OK humano
- [GUARDA-002 Residencia regional](20_Guardas/GUARDA-002_Residencia-regional.md) — datos regulados no salen de su región
- [GUARDA-003 No inventar](20_Guardas/GUARDA-003_No-inventar.md) — hueco → bloqueo + preguntas-entrevista
- [GUARDA-004 Suelo de costo](20_Guardas/GUARDA-004_Suelo-de-costo.md) — nunca cotizar bajo el costo base
- [GUARDA-005 Sin hardcodeo de cuentas](20_Guardas/GUARDA-005_Sin-hardcodeo-de-cuentas.md) — IDs/refs/keys solo en env/config → Xe portable, migración trivial
- [GUARDA-006 Topes y kill switch del canal de mando](20_Guardas/GUARDA-006_Topes-y-kill-switch-canal-mando.md) — **propuesta:** topes duros ($/tokens/acciones), confirm-en-código, kill switch, log append-only; endurece GUARDA-001 para el canal automatizado

## Veredictos
- [VEREDICTO-001 Lazo Starter](40_Postmortems/VEREDICTO-001_lazo-starter.md) — **PASA:** Xe orquestó agente-clinicas y creó una clínica real en DB local de prueba (verificado REST+psql); cierra Fase 2→3; contrato validado
- [VEREDICTO-002 Multi-agente (M3)](40_Postmortems/VEREDICTO-002_multi-agente.md) — **PASA — ratificado por Jordy 2026-07-16** (cierra 4c): `packages/multi-agente/` compone clinics para N agentes/cliente (lote atómico + sesión única); producto intacto. **Desbloquea Silver** ([[DEC-014]] Silver=basic×3), **sin precondición técnica**. **Deuda asumida:** sin e2e real (no iguala rigor de [[VEREDICTO-001]]). ⚠️ Corregido el mismo día: la 1ª redacción declaraba el RLS de agente-clinicas como precondición de Silver — falso (`service_role` bypassea RLS; el patrón de nexus no porta); ver CLAUDE.md §9.6 Decisión 7
- [VEREDICTO-004 Registro](40_Postmortems/VEREDICTO-004_registro.md) — **PASA (oracle + e2e local)** pendiente ratificación: `packages/registro/` = verdad exacta §3.1 de clientes/proyectos en 3 lentes con residencia (GUARDA-002); cliente+proyecto creados en sqlite local verificados por SELECT; backbone de Fase 5/6; propone [[DEC-013]]
- [VEREDICTO-005 Onboarding](40_Postmortems/VEREDICTO-005_onboarding.md) — **PASA (oracle + e2e local)** pendiente ratificación: `packages/onboarding/` realiza el norte v1 (§9.2) discovery→cotización→alta→entrega componiendo registro+clinics; no cobra/firma/envía (GUARDA-001); cotización no inventa (huecos #14/#17); base de Fase 5
- [VEREDICTO-006 Reporte (M6)](40_Postmortems/VEREDICTO-006_reporte.md) — **PASA (oracle + e2e local)** pendiente ratificación: `packages/reporte/` = cockpit de cartera; agrega clientes/proyectos por lente/tier/estado leyendo el registro; snapshot persistido no enviado (GUARDA-001); ROI=PENDIENTE-#23 (no inventa); cierra lado cartera de M6
- [VEREDICTO-007 Multicanal (M4)](40_Postmortems/VEREDICTO-007_multicanal.md) — **PASA — ratificado por Jordy 2026-07-16** (cierra 4b): `packages/multicanal/` compone clinics para N canales sobre UN cerebro (juego atómico + un canal por tipo); canales `web·whatsapp[baileys\|cloud_api]·instagram_dm·messenger` (CLAUDE.md §9.6); credencial ausente se BLOQUEA, no se finge. **🚧 Gold NO es entregable aunque M4 exista: 3/4 canales esperan aprobación de Meta** (`PENDIENTE-M4-meta`) — la ruta crítica es el trámite, no el código. **Deuda asumida:** sin e2e real. Alcance: compone y bloquea; el atado por canal es `PENDIENTE-M4-wiring`
- [VEREDICTO-008 vocero-crm (eval)](40_Postmortems/VEREDICTO-008_vocero-crm-evaluacion.md) — **AUDITADO, apto CONDICIONADO** (adopción = DEC humana pendiente): CRM WhatsApp MIT, bien construido (AES-256, 18 tests, Cloud API v25, cero GPL). **Clave: single-tenant disfrazado — un deploy por cliente** (`on-signup.ts:33-36`), no dashboard N-en-1. Fixes antes de PII: exigir `META_APP_SECRET` (firma webhook opcional). Encaja como shell CRM per-cliente sobre el agente; goal `.claude/goal-queue-vocero-adopcion.md`

## Fundadores / lentes regionales
- [Lentes regionales](30_Founders/lentes-regionales.md) — ×8/×6/×3, roles, regla de discrepancia (escala, no promedia)
- [Preguntas de entrevista](30_Founders/preguntas-entrevista.md) — 23 huecos de criterio que la mente NO rellena
- [Nichos US candidatos](30_Founders/nichos-us-candidatos.md) — **deep research verificado** (26 fuentes, 11 confirmadas/14 refutadas): ranking por CAC; Tier A = dental/medspa/vet (proven) + auto-repair/HVAC; EVITAR legal/real-estate; ⚠️ LTV/churn todo refutado (solo lado CAC). Crudo: research/nichos-us-deep-research.json. Decisión humana pendiente
