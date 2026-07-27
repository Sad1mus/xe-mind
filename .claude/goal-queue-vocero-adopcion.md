# Goal Queue — Adoptar vocero-crm como capa CRM per-cliente (fork + 2 fixes + spike)

estado: activa
current: 1
turn_cap_por_item: 15

<!--
NORTE: convertir vocero-crm (MIT) en la CAPA CRM/dashboard/inbox/pipeline/recordatorios de la agencia,
en un FORK propio, aceptando su modelo real (un deploy por cliente = lo que ya se hace con Juana/ZENKAI),
sobre el agente de la agencia (KB propia). Base: VEREDICTO-008 (auditado, apto CONDICIONADO).

REFRAMES CONFIRMADOS (VEREDICTO-008, con archivo:línea):
- NO es multi-tenant en la práctica: schema aísla por organizationId (scoped(), tenant.ts:16-21) pero el
  alta se niega a crear la 2ª org (on-signup.ts:33-36). => un deploy por cliente. N-en-1 = upgrade futuro.
- Firma de webhook OPCIONAL: isValidSignature devuelve true sin META_APP_SECRET (webhook.ts:31-33). FIX 1.
- El agente vive in-process (pipeline.ts); OpenRouter-compatible por env (OPENROUTER_BASE_URL). FIX 2 = KB propia.
- Bien construido: AES-256 del token (crypto/index.ts:26-48), 18 tests, Cloud API v25, cero GPL. MIT.

INVARIANTES DUROS (no se relajan):
- FORK propio (MIT; §8 plan B = ser dueño). NO push/fork a GitHub sin tu OK (outbound). NO deploy sin tu OK.
- NO tocar la copia de scratchpad (efímera); trabajar sobre una copia PERMANENTE.
- Fixes probados (test del repo o assertion mínima). NADA a producción. NO secretos a git (.env, tokens, App Secret).
- NO reiniciar/recrear Juana/ZENKAI. Cero API key de Anthropic. NO inventar (GUARDA-003).
- Un [blocked] NO frena la cola.

RUTAS:
- Copia de trabajo destino: ~/Documentos/Agencia/vocero-crm/ (fork/working copy).
- Clon efímero ya existente (solo referencia): scratchpad/vocero-crm.
- Node/tsx local: ~/Documentos/Agencia/grupojuana/agente-wa/node_modules/.bin/tsx (por si hace falta).
-->

## == FASE 0 — Fork y copia de trabajo ==

## [pendiente] 1. Establecer la copia de trabajo permanente + documentar el fork a GitHub
**Condición:** existe una copia de trabajo del repo en `~/Documentos/Agencia/vocero-crm/` (clon de `https://github.com/kevinrivm/vocero-crm.git`, historia completa o `--depth 1`, con su `.git`), lista para editar. El **fork a GitHub propio** (`gh repo fork kevinrivm/vocero-crm --clone=false` bajo la cuenta Sad1mus) se documenta como paso, PERO **no se ejecuta** (es outbound → tu OK). Se deja escrito el `git remote` que apuntaría al fork.
**Check:** `ls ~/Documentos/Agencia/vocero-crm/package.json` existe; `git -C ~/Documentos/Agencia/vocero-crm remote -v` muestra `origin → kevinrivm/vocero-crm` (upstream); imprimir "FORK A GITHUB PENDIENTE DE TU OK — no ejecuto `gh repo fork` ni `git push` sin autorización".
**No tocar:** NO `gh repo fork` ni `git push` (outbound, tu gate). NO borrar el clon de scratchpad hasta terminar.

## == FASE 1 — Fix 1: firma de webhook OBLIGATORIA (App Secret) ==

## [pendiente] 2. Exigir META_APP_SECRET: la firma del webhook deja de ser opcional
**Condición:** en la copia de trabajo, `isValidSignature` (webhook.ts:31-33) **ya NO devuelve `true` cuando falta `META_APP_SECRET`**: sin App Secret configurado, la verificación **falla cerrado** (rechaza el payload) y el handler del webhook (`webhooks/wa/[webhookToken]/route.ts:~48`) responde 401/403. El segmento secreto de la URL queda como defensa adicional, NO como sustituto. Se ajusta/añade el test unitario correspondiente (el repo ya testea el webhook). Se documenta en el `.env.example` que `META_APP_SECRET` es **obligatorio** en modo agencia (revirtiendo la sugerencia de dejarlo vacío, `.env.example:40-44`).
**Check:** mostrar el diff de `webhook.ts`; correr el test del webhook con la toolchain del repo si está disponible (`pnpm vitest run <archivo>`), o —si no hay pnpm/node_modules— una assertion mínima standalone que pruebe: sin secret → firma inválida → rechazo; con secret + firma correcta → acepta; firma alterada → rechaza. Exit 0.
**No tocar:** NO relajar la verificación "para probar"; NO loguear el App Secret; el cambio va en el fork, no en producción.

## == FASE 2 — Fix 2: el agente de Vocero con la KB de la agencia ==

## [pendiente] 3. Cargar la KB/persona de la agencia en el agente + apuntar el modelo por env
**Condición:** localizado el punto de configuración del system-prompt/persona del agente de Vocero (buscar en `src/**/ai/`, `pipeline.ts`, prompt/persona) y documentado CÓMO se inyecta la base de conocimiento de la agencia (la KB de un cliente concreto, p. ej. la de ZENKAI o una clínica) — vía archivo de config/env, sin reescribir el pipeline. El modelo LLM se apunta al gateway/modelo de la agencia por `OPENROUTER_BASE_URL` + `OPENROUTER_MODEL` (modelo pago confiable, NO `:free`), documentado en `.env.example`. Entregable: un `docs/kb-agencia.md` en el fork explicando el punto de inyección + un ejemplo de KB cargada (sin secretos).
**Check:** `grep` que muestre el archivo/línea donde se define el system-prompt del agente; el `docs/kb-agencia.md` existe y cita el punto de inyección concreto (archivo:línea); `.env.example` del fork lista `OPENROUTER_BASE_URL`/`OPENROUTER_MODEL`. Si es factible sin red, un dry-run del armado del prompt mostrando que toma la KB.
**No tocar:** NO cablear un segundo agente en paralelo (un solo agente por deploy, §6); NO poner keys reales; NO `:free` como modelo de producción (decisión de calidad ya conversada).

## == FASE 3 — Spike de deploy per-cliente (gate humano) ==

## [pendiente] 4. Documentar y preparar el spike de UN deploy de prueba por cliente (no ejecutar)
**Condición:** existe `~/Documentos/Agencia/vocero-crm/DEPLOY-SPIKE.md` que documenta el deploy de UNA instancia de prueba por cliente en la VPS: `docker-compose.yml` (Postgres + app), envs requeridas (`DATABASE_URL`, `BETTER_AUTH_SECRET`, `META_APP_SECRET` **obligatorio**, `WHATSAPP_TOKEN`, `OPENROUTER_*`), migración Drizzle (`drizzle/0000_*.sql`), Caddy exponiendo solo lo mínimo, puerto loopback dedicado por cliente (patrón multi-cliente de la VPS). Marca explícito qué necesita credenciales reales (Cloud API + Postgres) y que el deploy **NO se ejecuta** en este goal.
**Check:** el archivo existe y lista envs + puertos + el comando `docker compose up` que se correría; imprimir "DEPLOY SPIKE PENDIENTE DE TU OK Y DE CREDENCIALES — no toco la VPS". `docker compose -f <compose> config` valida el YAML del repo si docker está disponible (sin `up`).
**No tocar:** NO desplegar a la VPS; NO abrir puertos; NO usar credenciales reales de un cliente. Gate humano.

## == FASE 4 — DEC + integración con el flujo de Xe ==

## [pendiente] 5. DEC-018: adopción de vocero-crm como capa CRM per-cliente (propuesta) + atar a onboarding-meta
**Condición:** existe `vault/10_Decisions/DEC-018_Vocero-CRM-capa-per-cliente.md` (estado `propuesta`, con "qué la invalidaría" y fuente = [[VEREDICTO-008]]) que fija: Vocero = shell CRM/dashboard **por cliente** (no N-en-1 aún), sobre el agente de la agencia; retira el panel hand-rolled; se integra en [[DEC-017]] como la "cara" que `onboarding-meta` provisiona (una instancia por alta). Documenta el hueco N-en-1 (falta el flujo de provisioning de tenants) SIN inventar cuándo se hace. Índice del vault actualizado. Se referencia desde `infra/RUNBOOK-embedded-signup.md`.
**Check:** el archivo existe con frontmatter válido (`estado: propuesta`, campo "qué la invalidaría", fuente VEREDICTO-008); `vault/MEMORY.md` tiene la línea; `grep` confirma que NO se cambió a `aceptada`. Staged sin secretos (commit = tu gate).
**No tocar:** NO ratificar la DEC (sigue `propuesta`, VEREDICTO humano tuyo); NO commitear/pushear sin tu OK; NO inventar el pricing ni la fecha del upgrade N-en-1.
