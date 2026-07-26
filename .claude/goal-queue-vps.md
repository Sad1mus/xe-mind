# Goal Queue — Deploy del canal de mando de Xe a la VPS (Fase 1 read-only, 24/7)

estado: activa
current: 3
turn_cap_por_item: 15

<!--
Estados: [pending] -> [in-progress] -> [done] | [blocked]
Invariantes (de CLAUDE.md global + RUNBOOK + DEC-012/GUARDA-006):
- NO tocar los contenedores de Juana (agente-juanasanchez) ni ZENKAI (agente-zenkai).
- UN solo bot por servicio: apagar cualquier listener local del canal antes de desplegar.
- CERO API key: solo token de suscripción (CLAUDE_CODE_OAUTH_TOKEN de `claude setup-token`).
- EXEC_MODE=read_only. NADA de dinero ni autonomía (siguen apagados, VEREDICTO pendiente).
- Secretos por env con permisos 600, NUNCA en git ni impresos completos en el transcript.
- No montar docker.sock. Contenedor read-only, sin puertos (Telegram long-poll saliente).
- VPS: root@2.25.183.178 (llave id_ed25519). Repo en /srv/xe-mind; env+datos en /srv/clientes/xe-canal.
-->

## [done] 1. Pre-flight VPS (sin tocar nada de producción)
**Condición:** SSH a la VPS funciona, el daemon Docker responde, y los contenedores de Juana y ZENKAI siguen arriba (se listan, NO se tocan).
**Check:** `ssh root@2.25.183.178 'docker version --format "{{.Server.Version}}" && docker ps --format "{{.Names}} {{.Status}}"'` imprime la versión y muestra `agente-juanasanchez` + `agente-zenkai`.
**No tocar:** ningún contenedor existente; no reiniciar servicios ajenos.
**Evidencia:** SSH OK (host `srv1777083`), Docker server 29.6.2, `docker ps` → `agente-zenkai Up 27h` + `agente-juanasanchez Up 28h` (ambos intactos, no tocados). exit 0.

## [done] 2. Transferir el código a la VPS (rsync, sin secretos)
**Condición:** en `/srv/xe-mind/` están: `infra/canal-mando/` (código, Dockerfile, compose — SIN node_modules, SIN .env, SIN *.ndjson), `packages/reporte/`, `packages/registro/`, y `CLAUDE.md`.
**Check:** `ssh root@2.25.183.178 'ls /srv/xe-mind/infra/canal-mando/Dockerfile /srv/xe-mind/packages/reporte/connector.py /srv/xe-mind/packages/registro/connector.py /srv/xe-mind/CLAUDE.md'` los lista sin error.
**No tocar:** no subir `.env`, `node_modules`, `audit.ndjson`, `KILL` (excluir en rsync).
**Evidencia:** rsync (excluyendo node_modules/.env/*.ndjson/KILL/*.db/dist/*.log) → los 4 archivos clave presentes en `/srv/xe-mind`; verificado `sin .env` y `sin node_modules` en el destino. exit 0.

## [blocked] 3. setup-token de suscripción (REQUIERE ACCIÓN HUMANA)
**Condición:** existe un `CLAUDE_CODE_OAUTH_TOKEN` de `claude setup-token` (plan Max), listo para el `.env` de la VPS. Sin él, el contenedor no autentica `claude` (los mensajes de estado igual responden por el fast-path, pero las consultas abiertas no).
**Check:** el token está cargado en `/srv/clientes/xe-canal/.env` (verificado por presencia de la clave, sin imprimir el valor).
**No tocar:** NO usar API key. El token va por env 600, nunca en git ni en el transcript.
**Motivo del bloqueo:** requiere tu login de Anthropic. Corré `claude setup-token` (en tu equipo o la VPS) y pasame el token. Desbloquea la tarea 4.
**Evidencia:**

## [blocked] 4. .env de producción en la VPS (600)
**Condición:** `/srv/clientes/xe-canal/.env` (permisos 600) con: TELEGRAM_BOT_TOKEN, TELEGRAM_ALLOWED_CHAT_IDS=19950645, CLAUDE_CODE_OAUTH_TOKEN (de tarea 3), EXEC_MODE=read_only, XE_REPO_HOST_PATH=/srv/xe-mind, REGISTRO_DB=/data/registro.db, AUDIT_LOG_PATH=/data/audit.ndjson, KILL_SWITCH_PATH=/data/KILL, y los topes CAP_* vacíos.
**Check:** `ssh root@2.25.183.178 'stat -c %a /srv/clientes/xe-canal/.env && grep -cE "^(TELEGRAM_BOT_TOKEN|TELEGRAM_ALLOWED_CHAT_IDS|CLAUDE_CODE_OAUTH_TOKEN|EXEC_MODE)=" /srv/clientes/xe-canal/.env'` imprime `600` y `4`.
**No tocar:** no imprimir el contenido del .env (solo perms + conteo de claves).
**Motivo del bloqueo:** depende del `CLAUDE_CODE_OAUTH_TOKEN` de la tarea 3 (input humano). Se destraba apenas me pases el token.
**Evidencia:**

## [blocked] 5. Build imagen + init registro + levantar contenedor (endurecido)
**Condición:** imagen `agencia/xe-canal-mando:0.1.0` construida en la VPS; `/data/registro.db` inicializado con el esquema (vacío o con seed real); contenedor `xe-canal-mando` corriendo (red propia, sin puertos, read-only, límites mem/pids, no docker.sock).
**Check:** `ssh root@2.25.183.178 'docker ps --filter name=xe-canal-mando --format "{{.Names}} {{.Status}}"'` muestra `xe-canal-mando Up`; `docker logs xe-canal-mando` contiene `escuchando en Telegram`.
**No tocar:** no publicar puertos; no montar docker.sock; no tocar redes/volúmenes de Juana/ZENKAI.
**Motivo del bloqueo:** depende de la tarea 4 (.env con el token). Se destraba en cadena tras la tarea 3.
**Evidencia:**

## [blocked] 6. Prueba e2e desde el celular (REQUIERE ACCIÓN HUMANA)
**Condición:** desde tu Telegram, *"¿cómo va la agencia?"* a @Agenciazenkaibot → llega la respuesta generada DESDE la VPS (no local).
**Check:** recibís el snapshot en el chat; `ssh root@2.25.183.178 'docker logs --tail 20 xe-canal-mando'` muestra el mensaje procesado y el audit `read/allow`.
**No tocar:** un solo bot activo (el de la VPS); no dejar listener local corriendo en paralelo.
**Motivo del bloqueo:** requiere que vos mandes el mensaje desde el celular.
**Evidencia:**
