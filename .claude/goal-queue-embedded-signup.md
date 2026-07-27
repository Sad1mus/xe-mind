# Goal Queue — Embedded Signup → Cloud API → provisioning, cableado al bot EtherLabX

estado: activa
current: 8 (COMPLETA — 8/8)
turn_cap_por_item: 15

<!--
NORTE: que un cliente NUEVO de EtherLabX (lente LATAM/Américas) conecte su WhatsApp en ~2 min
vía Embedded Signup (botón + login Meta + SMS), y que Xe construya el resto SOLA: cambia el `code`
por token, lee WABA/Phone Number ID, registra el número, apunta el webhook, y deja el bot listo
sobre Cloud API — SIN entregar al cliente hasta que un humano dé el OK (DEC-017 Dec.4, GUARDA-001).

REFRAMES CONFIRMADOS (leer antes de ejecutar):
- El bot hoy habla Baileys (agente-wa/src/whatsapp.ts). Embedded Signup entrega números por Cloud
  API → PRIMERO el transporte Cloud API (Fase 1), reutilizando el diseño de xenkaisystems/MIGRACION-cloud-api.md.
- Embedded Signup exige ser Meta Tech Provider + App Review del permiso avanzado. Eso NO es código:
  es Fase 0 [blocked-human]. El goal construye y testea TODO el código sin depender de ese gate;
  lo que necesita el token/app REAL de Meta queda [blocked] hasta que Fase 0 cierre.
- Embedded Signup abre superficie inbound (callback + webhook) → choca con el hardening cero-inbound
  y con GUARDA-002 (residencia). Se resuelve con receptor endurecido detrás de Caddy (Fase 3),
  patrón ya probado en orvex/smc-platform (firma + idempotencia).
- Convivencia, NO swap (DEC-006 §9.6 Dec.6): Baileys queda intacto; Cloud API entra por flag de env.

INVARIANTES DUROS (no se relajan):
- NADA a producción sin OK humano. NO reiniciar/recrear agente-juanasanchez ni agente-zenkai.
- El token de Meta es de terceros (permitido headless, como el PAT de GitHub) PERO jamás entra al
  repo ni a git; va por env 600 en la VPS. "Cero API key" = API de Anthropic, intacto.
- NO secretos a git (.env, *.db, *.ndjson, tokens, App Secret). NO inventar umbrales/pricing (GUARDA-003).
- Todo módulo nuevo cumple el contrato de capacidades (oracle/dry-run/execute --confirm). dry-run SIN red.
- DEC-017 sigue `propuesta`: el "abrir al público / enviar al cliente" queda como visto humano, no auto.
- Un [blocked] NO frena la cola: se marca con motivo y se sigue con lo que sí es construible.

CONTEXTO MÁQUINA/RUTAS:
- Molde del bot: xenkaisystems/agente-wa/ (el que MIGRACION-cloud-api.md ya blueprintea). Brain/prompts/
  tools/db/panel se REUSAN; solo cambia el transporte. tsx local:
  ~/Documentos/Agencia/grupojuana/agente-wa/node_modules/.bin/tsx
- Provisioning = paquete nuevo en xe-mind/packages/ (Python3 stdlib, patrón contrato-capacidades §10.2).
- Envs Cloud API (de MIGRACION): WHATSAPP_TOKEN, PHONE_NUMBER_ID, WEBHOOK_VERIFY_TOKEN,
  WHATSAPP_APP_SECRET, GRAPH_API_VERSION. Nuevo flag de transporte: WA_TRANSPORT=baileys|cloud.
- SI querés un repo etherlabx/agente-wa dedicado (clon del molde) en vez de tocar el molde, decilo:
  se agrega como tarea 0. Por defecto asumo: transporte en el molde (beneficia a las 3 marcas).
-->

## == FASE 0 — Gate externo de Meta (BLOQUEANTE humano, NO código) ==

## [done] 1. Requisitos Meta Tech Provider + Embedded Signup (documentar y pedir, no ejecutar)
**Evidencia:** creado `vault/00_System/onboarding-meta-tech-provider.md` (4056 B): checklist A–D (verificación negocio ⏳, app+WhatsApp, Tech Provider, App Review de `whatsapp_business_management`/`whatsapp_business_messaging`/`business_management`, Facebook Login for Business + `config_id`, dominio callback en URIs OAuth, verify token). Referencia doc oficial (`grep developers.facebook.com/docs/whatsapp` = 1). Lista los **5 datos de retorno** (`grep` = 5): META_APP_ID, META_APP_SECRET, EMBEDDED_SIGNUP_CONFIG_ID, GRAPH_API_VERSION, dominio callback. Índice `vault/MEMORY.md` actualizado (línea "GATE HUMANO"). Impreso el aviso "FASE 0 ES GATE HUMANO". El deliverable (doc del gate) es construible; la ACCIÓN humana (volverse Tech Provider) sigue pendiente de ti — NO se intentó automatizar.
**NOTA:** el flujo EN VIVO de Embedded Signup queda [blocked] hasta que entregues los 5 datos; Fases 1–5 se construyen igual con fakes/dry-run.

<!-- ORIGINAL: [blocked-human] 1. Requisitos Meta Tech Provider + Embedded Signup (documentar y pedir, no ejecutar) -->
**Condición:** existe `xe-mind/vault/00_System/onboarding-meta-tech-provider.md` que documenta, sin inventar, el checklist EXACTO que solo un humano puede completar en Meta para habilitar Embedded Signup: (a) verificación del negocio de la agencia; (b) app de Meta tipo Business con el producto WhatsApp; (c) rol/estatus de **Tech Provider (Solution Partner)**; (d) **App Review** para acceso avanzado a `whatsapp_business_management` + `whatsapp_business_messaging`; (e) configurar el flujo de Embedded Signup y obtener el **`config_id`**. Al final, la lista de datos que Xe necesita de vuelta para operar: `META_APP_ID`, `META_APP_SECRET`, `EMBEDDED_SIGNUP_CONFIG_ID`, `GRAPH_API_VERSION`, y el dominio del callback. Marca explícito qué de esto tarda por revisión de Meta (lead-time externo).
**Check:** el archivo existe, referencia la doc oficial (developers.facebook.com/docs/whatsapp) y lista los 5 datos de retorno. Imprimir en la conversación: "FASE 0 ES GATE HUMANO — Xe NO puede volverse Tech Provider; el código de Fases 1–5 se construye y testea igual, pero el flujo EN VIVO queda bloqueado hasta que entregues estos 5 datos."
**No tocar:** NO intentar automatizar el registro Tech Provider ni el App Review. NO poner datos reales de Meta en el repo.

## == FASE 1 — Transporte Cloud API en el molde del bot (código, 0 prod, Baileys intacto) ==

## [done] 2. Nuevo transporte `whatsapp-cloud.ts` con flag WA_TRANSPORT (convivencia con Baileys)
**Evidencia:** creado `xenkaisystems/agente-wa/src/whatsapp-cloud.ts` (11.1 KB) con funciones puras + DI (solo importa `node:crypto`/`node:http`, testeable sin `.env`/red/brain): `verifyWebhook` (GET handshake), `parseIncoming` (entry[].changes[].value.messages[], solo texto), `buildSendPayload`/`sendViaCloud` (POST Graph con fetch inyectado), `handleWebhookPost` (dispatch al `enqueue` existente, 200-fast), + `startCloudApi` (server loopback). `config.ts`: agregado `waTransport` (default `'baileys'`) + objeto `cloud` (vars opcionales `?? ''`) + `validateCloud()` (solo se llama en rama cloud) — **sin nuevos `required()`** (`grep required(` = 2 = def + el original). `index.ts`: rama `if cloud → startCloudApi` / `else → startSocket` (Baileys default intacto). Test `whatsapp-cloud.test.ts` corrido con tsx → **19/19 verde, exit 0**: GET correcto→challenge, GET malo→null, parseIncoming (waId/text/messageId, ignora imagen), buildSendPayload (normaliza `@s.whatsapp.net`), sendViaCloud (URL `v22.0/<pnid>/messages` + Bearer + body), y dispatch e2e (webhook firmado→enqueue(waId,text)→send callback envía por Cloud). `whatsapp.ts` (Baileys) NO tocado.
**No tocar respetado:** Baileys/`whatsapp.ts`/volumen `auth` intactos; nada desplegado; ningún contenedor tocado.

<!-- ORIGINAL: [pendiente] 2. Nuevo transporte whatsapp-cloud.ts con flag WA_TRANSPORT (convivencia con Baileys) -->
**Condición:** en `xenkaisystems/agente-wa/`, existe `src/whatsapp-cloud.ts` que implementa lo de MIGRACION §5: (a) **webhook GET** de verificación (compara `hub.verify_token` con `WEBHOOK_VERIFY_TOKEN`, responde `hub.challenge`); (b) **webhook POST** que parsea `entry[].changes[].value.messages[]` → `from` (wa_id) + `text.body` → llama al mismo `enqueue/handleMessage` que usa Baileys, y responde **200 rápido**; (c) **envío** por `POST graph.facebook.com/<GRAPH_API_VERSION>/<PHONE_NUMBER_ID>/messages` con `Bearer WHATSAPP_TOKEN`. `config.ts` gana `WA_TRANSPORT` (default `baileys`) y `index.ts` arranca Baileys **o** Cloud según el flag. **Baileys y `whatsapp.ts` NO se borran** (convivencia, DEC-006 Dec.6). Toda llamada de red está detrás de una función inyectable para poder testear sin Meta.
**Check:** `tsx` local compila el molde sin romper Baileys; existe `src/whatsapp-cloud.test.ts` (o harness) que: (1) simula el GET con verify_token correcto→devuelve el challenge, con uno incorrecto→403; (2) inyecta un POST de mensaje entrante de ejemplo → verifica que se llamó a `handleMessage` con el `wa_id` y texto correctos → captura el payload de envío (mock, SIN red) y confirma la forma `{messaging_product:"whatsapp",to,type:"text",text:{body}}`. Correr y mostrar exit 0.
**No tocar:** NO borrar `whatsapp.ts` ni el volumen `auth`. NO desplegar. NO tocar contenedores en la VPS.

## [done] 3. Endurecer el receptor: firma X-Hub-Signature-256, idempotencia y 200-fast
**Evidencia:** `whatsapp-cloud.ts` implementa `verifySignature` (HMAC-SHA256 del raw body con `WHATSAPP_APP_SECRET`, comparación `timingSafeEqual`), `SeenIds` (dedup por `message.id`, ventana 5000) y `handleWebhookPost` (rechaza sin firma válida ANTES de parsear/despachar, responde 200 sync mientras el cerebro sigue async). Test `whatsapp-cloud.hardening.test.ts` con tsx → **16/16 verde, exit 0**: firma correcta→true / body alterado→false / otro secreto→false / sin header→false; firma inválida y ausente → status 401 + `enqueue` NO llamado + dispatched 0; mismo `messageId` dos veces → dispatched 1 luego 0, `enqueue` llamado UNA sola vez, 2ª respuesta 200. `grep` de `console.*` con `appSecret`/`token` → **sin fuga** (el secreto nunca se imprime).
**No tocar respetado:** verificación real (secret de test inyectado, no relajada); App Secret leído de env/cfg, nunca hardcodeado ni logueado.

<!-- ORIGINAL: [pendiente] 3. Endurecer el receptor: firma X-Hub-Signature-256, idempotencia y 200-fast -->
**Condición:** `whatsapp-cloud.ts` valida la firma `X-Hub-Signature-256` (HMAC-SHA256 del raw body con `WHATSAPP_APP_SECRET`); descarta payloads sin firma válida; deduplica por `message.id` (idempotencia — un mismo evento reintentado por Meta no se procesa dos veces); responde 200 aunque el procesamiento posterior sea async. El App Secret se lee de env, nunca se loguea.
**Check:** el harness cubre: firma válida→procesa; firma inválida/ausente→rechaza (401/403) y NO llama handleMessage; mismo `message.id` dos veces→procesa una sola vez. Exit 0. `grep` del código confirma que el App Secret no se imprime.
**No tocar:** NO hardcodear el App Secret; NO relajar la verificación "para probar" (usar un secret de test inyectado).

## == FASE 2 — Receptor de Embedded Signup + provisioning (paquete Xe, dry-run sin red) ==

## [done] 4. Paquete `packages/onboarding-meta` (contrato de capacidades) — provisioning por `code`
**Evidencia:** creado `packages/onboarding-meta/` (connector.py + manifest.json + README.md). Cliente Graph inyectable: `FakeGraph` (determinista, sin red) y `RealGraph` (hueco `PENDIENTE-META-APP`, lanza hasta Fase 0). Reusa `registro.compose/execute`. **ORACLE: PASA** (13/13): validación bloquea sin code/marca, lente `LATAM` (hueco #26) y tier inválido; FakeGraph determinista + token `FAKE-`; los 5 pasos Meta corren; go-live NO está en `PASOS` (es humano); alta compone cliente en `onboarding`, Starter→basic (derivado por registro), proyecto `whatsapp-cloud`; RealGraph bloqueado con `PENDIENTE-META-APP`. **dry-run**: imprime los 6 pasos SIN red ni DB, termina en STOP go-live=humano. **execute sin --confirm**: frena (GUARDA-001). **execute --confirm + REGISTRO_DB desechable**: escribió el alta REAL, verificado con `registro list` (`clinica-sonrisa` · Americas · EtherLabX · estado `onboarding` · plan `basic`), pasos Meta rotulados SIMULADOS. Ningún token real en el repo.
**No tocar respetado:** no se llamó a Meta de verdad (FakeGraph); no se inventó config_id ni pricing; no se escribió en registro de producción (DB /tmp desechable, borrada).

<!-- ORIGINAL: [pendiente] 4. Paquete packages/onboarding-meta (contrato de capacidades) — provisioning por code -->
**Condición:** existe `xe-mind/packages/onboarding-meta/connector.py` (Python3 stdlib, patrón §10.2) con `oracle`, `dry-run`, `execute --confirm`, y `manifest.json`. Entrada: el `code` de Embedded Signup + `lente` (Americas|EMEA|APAC) + datos del cliente. Flujo (todo network detrás de un cliente HTTP inyectable, en dry-run un **fake determinista**): (1) intercambiar `code` por token de negocio en `oauth/access_token`; (2) leer `WABA_ID` + `PHONE_NUMBER_ID`; (3) suscribir la app a la WABA; (4) registrar el número; (5) apuntar el webhook; (6) escribir el alta en `packages/registro` (respetando `region_datos`/GUARDA-002 según `lente`). `dry-run` produce el plan completo SIN efectos ni red; `execute` exige `--confirm` + `REGISTRO_DB` por env (GUARDA-005). Ningún token real vive en el repo.
**Check:** `python3 packages/onboarding-meta/connector.py oracle` → **ORACLE: PASA** (usa el fake HTTP + un `REGISTRO_DB` desechable en /tmp). `dry-run --json '{...}'` imprime los 6 pasos y el registro que insertaría, sin tocar red ni DB real. `execute` sin `--confirm` → se detiene e informa el hueco. Mostrar las 3 corridas en la conversación.
**No tocar:** NO llamar a Meta de verdad (no hay app real hasta Fase 0). NO inventar el `config_id` ni el pricing/plazo del cliente (GUARDA-003). NO escribir en el registro de producción.

## [done] 5. Endpoint callback `/es-callback` + módulo cliente Graph API (interfaz + fake)
**Evidencia:** creado `packages/onboarding-meta/graph_client.py` (interfaz Graph: `exchange_code/subscribe_app/register_number/set_webhook`) con `FakeGraph` (determinista, sin red) + `RealGraph` (hueco `PENDIENTE-META-APP`, lanza hasta Fase 0); `connector.py` refactorizado para importarlo → **oracle sigue PASA** (sin regresión). Creado `callback.py`: `handle_callback` puro (recibe `code`, corre onboarding-meta en **dry-run** con FakeGraph, **encola** el ítem para visto humano, **NO ejecuta** alta real) + server loopback que sirve **solo** `/es-callback` (resto 404). `python3 callback.py selftest` (e2e real con http.server + urllib) → **SELFTEST: PASA** (8/8): POST→200, encolado, `ejecutado:false`, estado `pendiente-visto-humano`, plan dry-run con provisioning `SIMULADO`, siguiente paso = VISTO HUMANO, sin `code`→400, otro path→404. Impl real de Graph queda tras `PENDIENTE-META-APP`, no cableada.
**No tocar respetado:** el callback NO ejecuta el alta automáticamente (encola para humano, DEC-017 Dec.4); solo `/es-callback` expuesto; panel/loopback documentado en el header del archivo.

<!-- ORIGINAL: [pendiente] 5. Endpoint callback /es-callback + módulo cliente Graph API (interfaz + fake) -->
**Condición:** existe el receptor HTTP del callback de Embedded Signup (`/es-callback`) que recibe el `code`, invoca `onboarding-meta` en modo dry-run por defecto y encola el resultado para revisión (no ejecuta el alta real sin gate). Existe un módulo `graph_client` con la interfaz de las llamadas Graph usadas (oauth exchange, subscribed_apps, register, webhook) y una implementación **fake** para tests + un hueco marcado `PENDIENTE-META-APP` para la real (que solo se completa tras Fase 0). Documentado que el panel y todo lo demás siguen en loopback; solo `/webhook` y `/es-callback` serán públicos.
**Check:** test que postea un `code` de ejemplo a `/es-callback` → responde 200 → produce un plan de provisioning (dry-run) → lo deja encolado para visto humano (no ejecutado). Exit 0. `grep` confirma que la impl real de Graph está detrás del hueco `PENDIENTE-META-APP`, no cableada.
**No tocar:** el callback NO ejecuta el alta real automáticamente (DEC-017 Dec.4). NO exponer el panel.

## == FASE 3 — Superficie inbound endurecida (resuelve colisión cero-inbound de DEC-017) ==

## [done] 6. Caddyfile: exponer SOLO /webhook* y /es-callback*, resto 404 (config, sin aplicar)
**Evidencia:** creado `xenkaisystems/agente-wa/deploy/Caddyfile`. Caddy (no instalado local) → verificado por inspección: exactamente **2 `reverse_proxy`, ambos loopback** (`127.0.0.1:3001` para `/webhook*`, `127.0.0.1:3002` para `/es-callback*`), un `handle {}` catch-all con `respond "not found" 404`, y el panel `:3000` **no se proxya** (`grep` = 0; `/d/` aparece solo en comentarios, nunca como ruta). Pasos de deploy (DNS A→2.25.183.178, `ufw` 22/80/443, instalar Caddy, `caddy reload`) documentados como gate humano, **NO ejecutados**.
**No tocar respetado:** no se abrieron puertos ni se aplicó Caddy en la VPS; config versionada, deploy es gate humano aparte.

<!-- ORIGINAL: [pendiente] 6. Caddyfile: exponer SOLO /webhook* y /es-callback*, resto 404 (config, sin aplicar) -->
**Condición:** existe `xenkaisystems/agente-wa/deploy/Caddyfile` (o donde viva el deploy del bot) que hace reverse-proxy con TLS automático, exponiendo **únicamente** `/webhook*` y `/es-callback*` al contenedor en loopback, y responde 404 a todo lo demás (el panel `/d/` NO se expone: sigue por túnel SSH). Documentado el registro DNS necesario (A → 2.25.183.178) y `ufw` (80/443/22) como pasos de deploy, PERO no se aplican a la VPS en este goal.
**Check:** `caddy validate --config <Caddyfile>` pasa si Caddy está disponible; si no, verificar por inspección que solo esos dos paths tienen `handle` y el resto cae en `respond 404`. Imprimir el diff/archivo en la conversación. NO ejecutar `ufw` ni tocar la VPS.
**No tocar:** NO abrir puertos ni aplicar Caddy en producción en este goal (es config versionada; el deploy es un gate humano aparte).

## == FASE 4 — Atar al gate de Xe (DEC-017: construir auto, entregar humano) ==

## [done] 7. Clasificar onboarding-meta en el gate: provisioning=reversible, go-live=visto humano
**Evidencia:** en `classify.ts` agregado `GOLIVE_RE` (go-live/abrir-al-público/enviar-al-cliente/primer-envío/publicar-cliente) evaluado en la rama Bash ANTES de READ/write → mapea a `outbound`; la construcción (dry-run→read, execute→write_reversible) NO matchea. Oráculo del gate corrido → **19/19 verde, exit 0**: `onboarding-meta dry-run`→allow, `onboarding-meta execute`→allow, `go-live --abrir-al-publico`→deny, `enviar-al-cliente`→deny, + los 13 casos previos (money/outbound/desconocido/kill/MCP) intactos; audit 18 líneas (>=17). `governance.ts` **sin cambios** (git confirma); `unknown→baja` intacto (classify.ts:66).
**No tocar respetado:** governance.ts no tocado; default no abierto; el envío al cliente jamás se auto-aprueba (cae en outbound→deny).

<!-- ORIGINAL: [pendiente] 7. Clasificar onboarding-meta en el gate: provisioning=reversible, go-live=visto humano -->
**Condición:** en `infra/canal-mando/classify.ts`, las acciones de `onboarding-meta` de **construcción/provisioning** (dry-run, alta en registro, registrar número) mapean a `write_reversible` (Xe las ejecuta en modo reversible), pero la acción de **abrir al público / primer envío al cliente** mapea a una clase que exige **confirm humano** (como `outbound`), de modo que el gate la frena y pide el visto por Telegram. `unknown→baja` intacto; `governance.ts` sin tocar.
**Check:** correr el oráculo del gate (`tsx infra/canal-mando/oracle.hook.ts` o el harness de classify) con casos nuevos: `onboarding-meta provision`→allow/reversible (auditado); `onboarding-meta go-live/send`→deny "redactá/pedí visto humano". Todos los casos previos siguen verdes. Exit 0, mostrar el conteo.
**No tocar:** NO modificar `governance.ts`; NO abrir el default; el envío al cliente jamás se auto-aprueba (GUARDA-001).

## == FASE 5 — Documentación + DEC ==

## [done] 8. Runbook Embedded Signup + actualizar DEC-017 con el mecanismo concreto
**Evidencia:** creado `infra/RUNBOOK-embedded-signup.md` (5.2 KB): flujo punta a punta (cliente→popup→code→callback→dry-run→visto humano→go-live), tabla quién-hace-qué, orden de dependencias (Fase 0 desbloquea lo vivo), mapa de archivos construidos, bloqueos abiertos; referencia los archivos de Fases 1–5 (`grep` = 14). `DEC-017` actualizado: añade **Embedded Signup como mecanismo de provisioning** (3 menciones), marca **BLOQUEO Fase 0 (Tech Provider)** y **Hueco de pricing SIGUE ABIERTO** — pricing NO resuelto (GUARDA-003); `estado: propuesta` **sin cambiar** (no se ratificó). Escaneo de secretos en el diff staged → **sin tokens reales** (solo `FAKE-…`/placeholders); ningún `.env/.db/.ndjson/__pycache__` staged. Commit NO ejecutado (tu gate).
**No tocar respetado:** DEC-017 sigue `propuesta`; no se commiteó/pusheó; pricing no inventado.

<!-- ORIGINAL: [pendiente] 8. Runbook Embedded Signup + actualizar DEC-017 con el mecanismo concreto -->
**Condición:** existe `xe-mind/infra/RUNBOOK-embedded-signup.md` que documenta el flujo punta a punta (cliente→popup Meta→code→callback→provisioning dry-run→visto humano→go-live), quién hace qué (humano vs Xe), y el orden de dependencias (Fase 0 desbloquea el vivo). Se actualiza `DEC-017` añadiendo Embedded Signup como el **mecanismo de provisioning** de la construcción automática, marcando que queda **bloqueado en Fase 0 (Tech Provider)** y que el **hueco de pricing sigue abierto** (plazo de compromiso, GUARDA-003) — sin inventarlo. Índice del vault actualizado si toca.
**Check:** ambos archivos existen; el runbook referencia las Fases 1–4 y los archivos creados; `DEC-017` cita Embedded Signup + los dos bloqueos (Tech Provider, pricing) sin resolver el pricing. Staged sin secretos (el commit es tu gate).
**No tocar:** NO cambiar el estado de DEC-017 a `aceptada` (sigue `propuesta`, VEREDICTO humano). NO commitear/pushear sin tu OK. NO inventar el pricing.
