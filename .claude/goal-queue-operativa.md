# Goal Queue — Xe operativa 24/7 en la VPS (Fases B + C + D, de corrido)

estado: activa
current: 8
turn_cap_por_item: 15

<!--
NORTE (megagoal-canal-mando.md): Xe hace TODO lo operativo comandada por Telegram;
único límite = dinero/firma/envío-al-cliente (humano, GUARDA-001). Nivel: reversible.
Base ya construida: Fase 0 (read-only) ✅ + Fase A (Xe con manos: classify+gate-hook+agent operativo) ✅.
Este goal recorre B (Telegram opera con manos) → C (deploy VPS 24/7) → D (automatizar packages).
Solo se detiene en gates HUMANOS reales (setup-token, mensaje desde el celular, VEREDICTO); todo lo
demás fluye. Un blocked NO frena la cola: la siguiente tarea igual procede.
Invariantes: gate en código; cada tool-call por governance.gate(); reversible ejecuta, dinero se
REDACTA (no se ejecuta); no tocar Juana/ZENKAI; secretos 600; cero API key; kill-switch siempre.
-->

## == FASE B — Telegram opera con manos (local, autónomo) ==

## [done] 1. bridge.ts en modo operativo + settings de producción
**Condición:** `bridge.ts` invoca a Xe en modo operativo (`runXeSession` con `settingsPath`=gate-hook + `permissionMode:"default"` + `EXEC_MODE=reversible`), manteniendo el fast-path de estado; para dinero/envío, relaya el dry-run que Xe redacta (no ejecuta). Existe `settings.gate.json` (producción) con el gate-hook por ruta de contenedor.
**Check:** `tsx` typecheck/carga de `bridge.ts` sin error; `settings.gate.json` válido (JSON) apuntando al gate-hook; el fast-path de estado sigue intacto.
**No tocar:** no romper el fast-path ni la allowlist; el default sin settings sigue siendo read-only.
**Evidencia:** `bridge.ts` edita la llamada a `runXeSession` → `permissionMode: env.GATE_SETTINGS ? "default" : "plan"` + `settingsPath: env.GATE_SETTINGS` (dinero lo frena el gate-hook y Xe lo redacta; su respuesta se relaya). `settings.gate.json` (producción, `/app/node_modules/.bin/tsx /app/gate-hook.ts`) JSON válido. Load-check: `bridge.ts` carga vía tsx, `handleMessage` = function. Fast-path (isStatusQuery/getAgencyStatus) intacto (3 refs).

## [done] 2. e2e local del bridge operativo (reversible ejecuta · dinero se redacta)
**Condición:** por el pipeline del bridge (allowlist→gate→Xe), un comando reversible EJECUTA y uno de dinero/envío queda BLOQUEADO y Xe lo REDACTA; todo auditado.
**Check:** un harness local (tipo `echo.oneshot`) procesa 2 órdenes: una reversible (efecto verificable) y una de dinero (`permission_denials`/audit deny + Xe redacta). Sale 0.
**No tocar:** 0 ejecuciones de dinero; cupo acotado.
**Evidencia:** `tsx e2e.bridge.ts` (pipeline real `handleMessage`, EXEC_MODE=reversible) → 4/4, exit 0: orden reversible ejecutada (archivo creado), orden `stripe charge` → audit deny (money) + el bridge relayó la redacción de Xe ("Bloqueado... No reintento"). BUG DE PRODUCTO cazado: `isStatusQuery` matcheaba "agencia" en cualquier lado (misruteo de órdenes al fast-path) → endurecido (verbos de acción descartan el fast-path); 8/8 casos (preguntas→true, órdenes→false).

## == FASE C — Deploy a la VPS (EXEC_MODE=reversible, 24/7) ==

## [done] 3. Transferir el código actualizado a la VPS (rsync)
**Condición:** en `/srv/xe-mind/infra/canal-mando/` está el código nuevo (classify.ts, gate-hook.ts, settings de producción, bridge operativo) + `packages/` + `CLAUDE.md`, sin secretos ni node_modules.
**Check:** `ssh root@2.25.183.178 'ls /srv/xe-mind/infra/canal-mando/gate-hook.ts /srv/xe-mind/infra/canal-mando/classify.ts'` los lista.
**No tocar:** no subir `.env`, `node_modules`, `*.ndjson`, `KILL`.
**Evidencia:** rsync (excluyendo node_modules/.env/*.ndjson/KILL/*.db/*.log/sandbox) → en `/srv/xe-mind/infra/canal-mando/` están `gate-hook.ts`, `classify.ts`, `status.ts`, `settings.gate.json`; verificado sin `.env`. exit 0.

## [done] 4. Dockerfile/compose: el gate-hook corre en el contenedor + reversible
**Condición:** la imagen instala `tsx`; el `settings.gate.json` del contenedor apunta al gate-hook con el `tsx` del contenedor; `compose`/env fija `EXEC_MODE=reversible`, `CAP_TOKENS_*`>0 (presupuesto operativo), `CAP_USD_*`=0 (dinero humano), `KILL_SWITCH_PATH`.
**Check:** `docker build` (en la VPS) pasa; `settings.gate.json` válido; sin secretos en la imagen. (build real puede ir junto a la tarea 7.)
**No tocar:** no montar docker.sock; read-only rootfs; sin puertos.
**Evidencia:** `package.json` → `tsx` movido a dependencies (runtime); `Dockerfile` → `npm install --omit=dev` + `COPY settings.gate.json ./` (el `COPY *.ts` no traía el json); `compose.yml` → `EXEC_MODE: reversible` + `GATE_SETTINGS=/app/settings.gate.json` + topes (CAP_TOKENS_PER_SESSION=2M, CAP_USD_*=0). YAML/JSON validados; read_only True, sin puertos. Subido a la VPS. Build real → tarea 7.

## [done] 5. setup-token de suscripción (REQUIERE ACCIÓN HUMANA)
**Condición:** `CLAUDE_CODE_OAUTH_TOKEN` de `claude setup-token` (Max), listo para el `.env` de la VPS.
**Check:** el token cargado en `/srv/clientes/xe-canal/.env` (por presencia de la clave, sin imprimir valor).
**Motivo del bloqueo:** requiere tu login de Anthropic. Corré `claude setup-token`, pasame el token. Es el motor de Xe pensante en la VPS.
**Evidencia:** token de suscripción (`sk-ant-oat01-…`) recibido del humano 2026-07-24; cargado en el `.env` de la VPS (600, vía stdin, no impreso).

## [blocked] 6. .env de producción reversible en la VPS (600)
**Condición:** `/srv/clientes/xe-canal/.env` (600) con: TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_CHAT_IDS=19950645, CLAUDE_CODE_OAUTH_TOKEN (tarea 5), EXEC_MODE=reversible, CAP_TOKENS_PER_SESSION/DAY>0, CAP_USD_*=0, XE_REPO_HOST_PATH=/srv/xe-mind, GATE_SETTINGS, REGISTRO_DB, AUDIT_LOG_PATH, KILL_SWITCH_PATH.
**Check:** `ssh ... 'stat -c %a .env && grep -cE "^(TELEGRAM_BOT_TOKEN|CLAUDE_CODE_OAUTH_TOKEN|EXEC_MODE|CAP_TOKENS_PER_SESSION)=" .env'` → `600` y `4`.
**Motivo (dependencia):** necesita el token de la tarea 5. Se destraba con él.
**Evidencia:** `.env` en `/srv/xe-mind/infra/canal-mando/.env` (600, escrito por stdin — no en logs de la VPS). Verificado: `perms=600`, 4 claves-clave (TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_CHAT_IDS, CLAUDE_CODE_OAUTH_TOKEN, EXEC_MODE), 14 vars. EXEC_MODE=reversible, CAP_TOKENS>0, CAP_USD=0.

## [done] 7. Build imagen + init registro + levantar contenedor 24/7
**Condición:** imagen construida en la VPS; `/data/registro.db` con esquema; contenedor `xe-canal-mando` Up (red propia, sin puertos, read-only, límites, sin docker.sock); Juana/ZENKAI intactos.
**Check:** `ssh ... 'docker ps --filter name=xe-canal-mando'` → Up; `docker logs` contiene `escuchando en Telegram`; `docker ps` sigue mostrando Juana+ZENKAI.
**Evidencia:** imagen `agencia/xe-canal-mando:0.1.0` construida (con `procps` para el healthcheck; `/data` pre-chowneado a app en el Dockerfile). `/data` (volumen) chowneado a uid 10001 + registro init (`registro.db` 20KB, reporte lee "total 0"). `docker compose up -d` → contenedor **Up (healthy)**, log `escuchando en Telegram (EXEC_MODE=reversible)`. Auth verificada: `docker exec … claude -p` → `PONG` con el token de suscripción (cero API key). Juana/ZENKAI intactos (30h/29h). GOTCHA: volumen `/data` nace root-owned → uid 10001 no podía escribir; corregido (chown + Dockerfile).

## [blocked] 8. e2e operativo desde el celular (REQUIERE ACCIÓN HUMANA)
**Condición:** desde tu Telegram: (a) una orden reversible (ej. "dá de alta un cliente de prueba en el registro") la EJECUTA Xe en la VPS; (b) una orden de dinero/envío → Xe la REDACTA y NO la ejecuta.
**Check:** recibís ambas respuestas; `ssh ... 'docker logs --tail 30 xe-canal-mando'` muestra el gate (allow del reversible, deny+redacción del dinero) auditado.
**Motivo del bloqueo:** requiere que mandes los mensajes desde el celular.
**Evidencia (PARCIAL, 2026-07-24):** ✅ (a-status) el humano escribió al bot desde la VPS y el audit registró `read | reporte_dry_run | allow` → el canal recibe (grammy pollea OK en la VPS real), el gate autoriza la lectura, Xe corre el fast-path de estado. FALTA confirmar: recepción de la respuesta en el celular, la orden reversible (write→allow+ejecuta) y la de dinero (money→deny+redacta). Retomar aquí mañana.

## == FASE D — Automatizar los packages (progresivo, uno por vez con VEREDICTO) ==

## [blocked] 9. registro: alta de cliente por Xe desde Telegram (primer package)
**Condición:** comandada por chat, Xe corre el connector de `registro` end-to-end (dry-run + execute reversible en la DB de la VPS) sin que toques la terminal; el alta queda en el registro. Es el patrón que luego repiten onboarding→reporte→multi-agente (goals siguientes).
**Check:** desde Telegram, "dá de alta al cliente X (lente/tier)"; Xe lo escribe en `registro`; `reporte` lo muestra. Auditado.
**Motivo del bloqueo:** depende de la VPS viva (tareas 6-7) + tu VEREDICTO de que el package se automatice ([[GUARDA-006]]/DEC-012).
**Evidencia:**
