---
id: VEREDICTO-008
titulo: Evaluación de vocero-crm (open-source MIT) como capa CRM/dashboard para la agencia
fecha: 2026-07-27
estado: AUDITADO — apto CONDICIONADO (per-cliente, con 2 fixes). VEREDICTO humano de ADOPCIÓN pendiente.
lente: global
---

> **Naturaleza:** esto NO es el oracle de un módulo propio; es una **auditoría de solo-lectura** de un repo de tercero que el humano propuso anexar (`github.com/kevinrivm/vocero-crm`, MIT, Kevin Belier 2026). "Se probó así → salió esto → con esta confianza". La **decisión de adoptar** es una DEC aparte (propuesta), no la cierra este VEREDICTO.

## Hipótesis probada
`vocero-crm` puede ser la **capa CRM/dashboard/inbox/pipeline/recordatorios** que los planes growth/scale prometen ([[DEC-014]]) y que hoy está hand-rolled — de forma **legal** (Cloud API, no Baileys), **fácil** (features ya construidas) y **multi-cliente** para una agencia.

## Método
Fork clonado (`--depth 1`) a scratchpad; **solo lectura, sin ejecución** (no `npm install`, no docker, no correr el Laboratorio). Auditoría por subagente sobre 6 dimensiones con evidencia `archivo:línea`.

## Evidencia (auditoría 2026-07-27)

| Dimensión | Veredicto | Evidencia |
|---|---|---|
| **Multi-tenancy** | **RIESGO** (bloqueante para N-en-1) | Schema multi-tenant real: `organizationId NOT NULL` + índice org-first en toda tabla (`schema.ts:107-378`), helper `scoped()` que revienta sin tenant (`tenant.ts:16-21`), rutas con `withAuth`+`scoped`. PERO el alta es single-org: `onUserCreated` **se niega a crear la 2ª organización** (`on-signup.ts:33-36`), registro público cierra tras la 1ª (`registration.ts:11-15`), y el alta de equipo mete al nuevo en la MISMA org (`settings/team/route.ts:76-84`). **No hay flujo para provisionar el cliente #2.** |
| **Secretos** | **BIEN** | Token WhatsApp cifrado AES-256-GCM en reposo (`crypto/index.ts:26-48`), guardado cipher/iv/tag (`credentials.ts:83-96`), nunca logueado (solo `tokenLast4` a la UI). OpenRouter key solo en header. Cero secretos hardcodeados; `.env.example` todo `REEMPLAZA_`. |
| **Seguridad web** | **BIEN** (1 reserva) | `withAuth` fuerza sesión en cada handler (`lib/api.ts:20-40`); Drizzle parametrizado (sin concatenación SQL); rutas mock 404 fuera de dev. Reserva: firma de webhook opcional (ver hallazgo #2). |
| **WhatsApp Cloud API** | **BIEN** | Graph API oficial `v25.0` (no Baileys), frontera única `graphRequest` (`meta/client.ts:37-88`); idempotencia por `waMessageId UNIQUE`+`onConflictDoNothing` (`ingest.ts:154-171`); ventana 24h antes de enviar (`send.ts:70-76`). |
| **Licencias sub-deps** | **BIEN** | Directas todas permisivas (MIT/Apache/ISC): better-auth, drizzle, next, react, zod, playwright. **Cero GPL/AGPL/MPL** (contraste con la GPL-3.0 de libsignal que arrastra Baileys). Árbol transitivo profundo no auditado. |
| **Madurez/calidad** | **BIEN** | 18 archivos de test (~962 líneas) sobre lo crítico (crypto, webhook, tenant, credentials, judge, rate-limit); migración versionada (`drizzle/0000_*.sql`); cero TODO/stub reales. **SDD disciplinado, NO una pasada de IA** (corrige la sospecha inicial). |

## Los 3 hallazgos más graves (con evidencia)
1. **Single-tenant disfrazado de multi-tenant.** El schema aísla por `organizationId` (mejor que `agente-clinicas`), pero no existe alta del cliente #2 (`on-signup.ts:33-36`, `registration.ts:11-15`, `settings/team/route.ts:76`). **Consecuencia: un deploy por cliente** — no el dashboard único N-clientes.
2. **Firma del webhook OPCIONAL.** `isValidSignature` devuelve `true` si no hay `META_APP_SECRET` (`webhook.ts:31-33`), y `.env.example:40-44` lo sugiere vacío en "modo agencia", confiando solo en el segmento secreto de la URL. Para PII de clientes finales, el App Secret debe **exigirse**.
3. **Laboratorio acoplado al agente interno.** `lab/runner.ts:6,235` llama `runAgentTurn(convId)` directo al pipeline interno. No hay punto de inyección para un agente HTTP externo; evaluar el agente de la agencia con el Lab exige modificar código.

## Reuso vs choque con el stack
- **Encaja:** Cloud API oficial (igual que `agente-clinicas`), OpenRouter (ya usado; apuntable a gateway propio por `OPENROUTER_BASE_URL` sin tocar código), Caddy+Docker (idéntico a la VPS).
- **Fricción:** mete un **4º patrón de datos** (Postgres+Drizzle+Next.js+Better Auth). Agente **in-process** (`pipeline.ts:29-46`), monolito de una instancia, sin colas → no escala horizontal.

## Condiciones para adoptarlo (falsables)
1. Fork propio (MIT lo permite; §8 plan B = ser dueño del fork).
2. **Exigir `META_APP_SECRET`** (webhook firmado) antes de tocar PII.
3. Aceptar el modelo real: **un deploy por cliente** (= lo que ya se hace con Juana/ZENKAI), con Vocero como shell y el agente cargado con la KB de la agencia.
4. N-clientes-en-uno queda como upgrade futuro: la base `scoped()` aguanta; solo falta escribir el provisioning de tenants (crear org+owner+seed) — que es lo que `onboarding-meta` ya empezó.

## Confianza
**Media-alta.** Alta en la calidad del código auditado (cifrado, tests, aislamiento a nivel query, Cloud API correcta). Media en el conjunto operativo, porque **no se ejecutó** (ni el Laboratorio ni un deploy real): es auditoría estática, no e2e — misma deuda de rigor que [[VEREDICTO-007]] declaró.

## Veredicto
**Apto CONDICIONADO como capa CRM per-cliente, no como dashboard multi-cliente tal cual.** Bien construido, legal y MIT; el "multi-tenant" del schema es una promesa que el aprovisionamiento no cumple. Sirve con **fork + 2 fixes** aceptando un deploy por cliente. **La adopción es decisión humana** (DEC pendiente); este VEREDICTO solo aporta la evidencia.

**Relaciones:** evalúa un candidato para la capa CRM de [[DEC-014]] (planes growth/scale) · encaja como "cara" en el flujo de [[DEC-017]] (Xe provisiona una instancia por cliente) · restringido por [[GUARDA-002]] (residencia: un deploy por región/cliente ayuda) y §8 (dependencia comercial → fork) · el goal de adopción vive en `.claude/goal-queue-vocero-adopcion.md`.
