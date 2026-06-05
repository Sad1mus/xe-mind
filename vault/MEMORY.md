# Memoria — zenkai-mind (La Mente de la Agencia)

Índice del vault. Una línea por nota. El detalle vive en cada archivo, no aquí.

## Sistema
- [Convenciones del vault](00_System/conventions.md) — formato de DEC/GUARDA/VEREDICTO; reglas duras (falsabilidad, citar fuente, hueco≠invento)
- [Inventario del portafolio](00_System/inventario-portafolio.md) — capacidad×repo: qué existe vs gaps; Starter/Silver ~90% existe, Gold+ con gaps (video, multicanal, white-label)
- [Contrato de capacidades](00_System/contrato-capacidades.md) — interfaz manifest/inputs/dry_run/execute/oracle; habilita construcción paralela; lazo probado
- Lazo Starter (dry-run ejecutable): `loop/starter_loop_dryrun.py` — discovery→quote→payload→STOP en GUARDA-001

## Integraciones (conectores a productos externos)
- [clinics](../integrations/clinics/README.md) — conector a `agente-clinicas`; contrato cumplido (inputs/dry_run/execute/oracle); `oracle PASA`; execute tras OK humano + env CLINICS_REPO. Pendiente ejecución real (Supabase de HaxelGG → su OK)

## Decisiones (DEC)
- [DEC-008 Norte — agencia global](10_Decisions/DEC-008_Norte-agencia-global.md) — **aceptada (norte):** repo = cerebro orquestador de agencia global; portafolio = librería componible; tiers acumulativos; plantillas 10 nichos US (sin definir aún)
- [DEC-007 Arquitectura de marca — Xe](10_Decisions/DEC-007_Arquitectura-de-marca-Xe.md) — **aceptada (provisional):** Xe = mente paraguas (Jordy/Sad1mus + socio/HaxelGG); ZENKAI=Europa · EtherLabX=LATAM · Américas=por definir
- [DEC-010 Xe = orquestador que integra](10_Decisions/DEC-010_Arquitectura-monorepo-Xe.md) — **aceptada:** empresa compartida; Xe **integra los productos donde viven, NO los mueve**; monorepo (mind/packages/integrations/infra), local-first; migración al Team/Org trivial si no se hardcodea
- [DEC-009 Mapeo tier→plan](10_Decisions/DEC-009_Mapeo-tier-plan-entrega.md) — **aceptada (parcial):** Starter→`basic`; resto del mapeo pendiente
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

## Veredictos
- [VEREDICTO-001 Lazo Starter](40_Postmortems/VEREDICTO-001_lazo-starter.md) — **PASA:** Xe orquestó agente-clinicas y creó una clínica real en DB local de prueba (verificado REST+psql); cierra Fase 2→3; contrato validado

## Fundadores / lentes regionales
- [Lentes regionales](30_Founders/lentes-regionales.md) — ×8/×6/×3, roles, regla de discrepancia (escala, no promedia)
- [Preguntas de entrevista](30_Founders/preguntas-entrevista.md) — 23 huecos de criterio que la mente NO rellena
- [Nichos US candidatos](30_Founders/nichos-us-candidatos.md) — **deep research verificado** (26 fuentes, 11 confirmadas/14 refutadas): ranking por CAC; Tier A = dental/medspa/vet (proven) + auto-repair/HVAC; EVITAR legal/real-estate; ⚠️ LTV/churn todo refutado (solo lado CAC). Crudo: research/nichos-us-deep-research.json. Decisión humana pendiente
