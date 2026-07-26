# Goal Queue — Armonizar infra + saldar deudas técnicas (VPS 2.25.183.178)

estado: activa
current: 6
turn_cap_por_item: 15

<!--
NORTE: cerrar las 5 deudas técnicas del reporte de infra (2026-07-26) SIN romper producción.
Orden por riesgo creciente: primero código local (0 impacto prod), luego higiene de infra que
NO toca los clientes, luego el cap de memoria de Juana (en vivo, sin reiniciar), y por último git
(el commit es TU gate). Cierra con un RUNBOOK que documenta el estado armonizado.
Invariantes duros: NO reiniciar/recrear agente-juanasanchez ni agente-zenkai (solo cambios en vivo
y reversibles); NO commitear/pushear sin OK humano; NO subir secretos (.env, *.db, *.ndjson, KILL);
cero API key; todo cambio en la VPS debe ser reversible. Un [blocked] NO frena la cola.
Contexto máquina: Ubuntu 24.04, Docker 29.6.2, 15GiB RAM (14 libre), disco 7% usado.
tsx local: ~/Documentos/Agencia/grupojuana/agente-wa/node_modules/.bin/tsx (este node no tiene TS nativo).
-->

## == FASE 1 — Código (P5): 0 impacto en producción ==

## [done] 1. Ampliar classify.ts para tools de descubrimiento/MCP (sin abrir el default)
**Condición:** en `infra/canal-mando/classify.ts`, las tools de descubrimiento read-only (`ToolSearch`) se mapean a `kind: "read"` (hoy caen en desconocido→confianza baja→deny, como se vio en el audit del 2026-07-26); las tools MCP de pago (regex tipo `stripe|payment|ramp|payout|charge|cobro`) se mapean a `money`; el resto de `mcp__*` sigue en `write_reversible`; y **toda tool no reconocida SIGUE cayendo en confianza `baja`** (fail-closed §4 intacto — el default NO se abre).
**Check:** correr el oráculo del gate con casos nuevos y ver el resultado en la conversación: `~/Documentos/Agencia/grupojuana/agente-wa/node_modules/.bin/tsx infra/canal-mando/oracle.gate.ts` (o el harness de classify existente) → `ToolSearch`→read/allow, una tool MCP de pago→money/deny, una tool inventada (`Frobnicate`)→baja/deny. Exit 0, todos los casos verdes.
**No tocar:** NO modificar `governance.ts`; NO cambiar el caso `unknown→baja`; NO tocar producción (tarea 100% local).
**Evidencia:** `classify.ts` → `ToolSearch` agregado a `READ_TOOLS`; nuevo `MCP_MONEY_RE` (añade `ramp|billing` a proveedores) aplicado sólo a `mcp__*`; `unknown→read/baja` INTACTO; `governance.ts` sin tocar. `oracle.hook.ts` extendido (+5 casos). Corrido con tsx local → **15/15 ok, exit 0**: `ToolSearch→allow`, `mcp__stripe__charge→deny`, `mcp__Ramp_Data__pay→deny`, `mcp__apify__search→allow`, `Frobnicate→deny`, y los 8 casos previos + kill-switch + audit (14 líneas NDJSON válidas) siguen verdes.

## == FASE 2 — Higiene de infra que NO toca los clientes ==

## [done] 2. Backup automático del volumen /data (P3): registro.db + audit, con rotación
**Condición:** existe en la VPS un script `/srv/xe-mind/infra/canal-mando/backup-data.sh` que: (a) hace copia consistente de `registro.db` usando el backup online de SQLite vía python3 stdlib dentro del contenedor (`docker exec xe-canal-mando python3 -c "import sqlite3; s=sqlite3.connect('/data/registro.db'); d=sqlite3.connect('/data/registro.bak.db'); s.backup(d); d.close()"`), (b) saca la copia + `audit.ndjson` al host en `/srv/backups/xe-canal/AAAA-MM-DD/` vía `docker cp`, (c) rota conservando los últimos 14 días. Está instalado en cron (diario). Corrido una vez a mano, deja un backup válido.
**Check:** en la conversación: correr el script una vez; `ls -la /srv/backups/xe-canal/` muestra un directorio con `registro.bak.db` y `audit.ndjson`; verificar integridad del backup: `sqlite3` no está en el contenedor, así que usar python3 en el host o en el contenedor sobre la copia → `PRAGMA integrity_check` = `ok`; `crontab -l | grep backup-data` muestra la entrada.
**No tocar:** NO tocar la DB viva (solo lectura/backup online); NO borrar `/data`; el `.bak.db` temporal en `/data` se elimina tras copiarlo.
**Evidencia:** `backup-data.sh` creado (versionado en `infra/canal-mando/`) y subido a la VPS (`chmod +x`). Corrida real → `integrity_check=ok`, `backup OK → /srv/backups/xe-canal/2026-07-26`. `ls` del destino muestra `registro.bak.db` (20KB) + `audit.ndjson` (461B). Cron instalado (idempotente, borra duplicados antes de reinsertar): `15 3 * * * .../backup-data.sh >> /var/log/xe-backup.log`. Rotación 14d vía `find -mtime +14`; temporal `/data/registro.bak.db` borrado tras copiar.

## [done] 3. Alerta de caída de contenedores (P4): healthcheck saliente a Telegram
**Condición:** existe en la VPS un script `/srv/xe-mind/infra/canal-mando/watch-health.sh` que revisa el estado de los 3 contenedores (`xe-canal-mando` por `.State.Health.Status`, `agente-juanasanchez`/`agente-zenkai` por `.State.Running`) y, si alguno NO está sano, envía un mensaje por Telegram **solo al chat autorizado 19950645** (lee el `TELEGRAM_BOT_TOKEN` del `.env` 600, no lo imprime). Instalado en cron cada 5 min. Modo dry-run probado.
**Check:** en la conversación: correr `watch-health.sh --dry-run` con los 3 contenedores sanos → imprime "todo sano, no alerta"; correr con un nombre de contenedor de prueba inexistente/forzado como caído → imprime el payload de alerta que ENVIARÍA (sin enviar en dry-run), citando el contenedor caído; `crontab -l | grep watch-health` muestra la entrada.
**No tocar:** la alerta va SOLO al chat 19950645 (nunca a clientes); NO reiniciar contenedores desde el script (solo observa y avisa); el token nunca se imprime en logs.
**Evidencia:** `watch-health.sh` creado (versionado) y subido (`chmod +x`). Dry-run [1] con los 3 reales → `todo sano, no alerta`. Dry-run [2] `--dry-run contenedor-de-prueba-xyz` → imprime el payload `⚠️ Xe/VPS — contenedor(es) con problema: • contenedor-de-prueba-xyz: no existe / caído` (sin enviar). Token leído del `.env` sólo en el envío real, nunca impreso; alerta cableada SOLO a `chat_id=19950645`. Cron: `*/5 * * * * .../watch-health.sh >> /var/log/xe-watch.log`. El script NO reinicia nada.

## == FASE 3 — Cambio en vivo sobre un cliente (reversible, sin reiniciar) ==

## [done] 4. Cap de memoria de agente-juanasanchez (P1): armonizar a 2 GiB, en vivo
**Condición:** `agente-juanasanchez` queda limitado a 2 GiB (igual que zenkai y Xe), aplicado **en vivo con `docker update --memory 2g --memory-swap 2g agente-juanasanchez` (SIN recrear ni reiniciar el contenedor)**, y persistido para el futuro editando `/home/sadimus/agencia/agente-juanasanchez/docker-compose.yml` con `mem_limit: 2g` + `memswap_limit: 2g`.
**Check:** en la conversación: `docker inspect agente-juanasanchez --format '{{.State.Running}} mem={{.HostConfig.Memory}}'` → `true mem=2147483648`; el contenedor sigue con el mismo uptime (no se reinició) y responde en `127.0.0.1:3000`; `grep -A1 mem_limit /home/sadimus/agencia/agente-juanasanchez/docker-compose.yml` muestra el límite persistido.
**No tocar:** PROHIBIDO reiniciar/recrear Juana. Si por cualquier razón el cambio exigiera recrear el contenedor, NO hacerlo: marcar la tarea [blocked] con el motivo y seguir. Reversible con `docker update --memory 0`.
**Evidencia:** `docker update --memory 2g --memory-swap 2g` aplicado EN VIVO → `mem` 0→`2147483648`, `Running=true`. Prueba de no-reinicio: `StartedAt=2026-07-23T18:43:02.852019971Z` IDÉNTICO antes, después y tras persistir el compose. Juana responde en :3000 (`http_code=404` = servidor arriba). Compose persistido (`mem_limit: 2g`+`memswap_limit: 2g`, líneas 7-8), `docker compose config` valida el YAML; original guardado en `docker-compose.yml.bak-premem`. NO se corrió `docker compose up` (solo `config`, sin efecto en runtime). Reversible con `docker update --memory 0`.

## == FASE 4 — Versionado (P2): commit = gate humano ==

## [done] 5. Endurecer .gitignore y dejar staged el canal (sin secretos), listo para tu commit
**Condición:** en el repo `xe-mind`, el `.gitignore` cubre `**/.env`, `*.db`, `*.ndjson`, `KILL`, `node_modules/`, `**/sandbox/`; el código del canal (`infra/canal-mando/*.ts`, `settings.gate.json`, `Dockerfile`, `compose.yml`, `package.json`, `.env.example`) + `packages/` quedan **staged** y VERIFICADO que NINGÚN secreto está en el índice. El commit en sí NO se hace (es tu gate duro).
**Check:** en la conversación: `git -C ~/Documentos/Agencia/xe-mind add -A` seguido de `git status --short` y `git diff --cached --name-only | grep -E '(\.env$|registro\.db|audit\.ndjson|/KILL$)'` → **vacío** (cero secretos staged); `git diff --cached --stat` muestra los archivos del canal listos. Imprimir explícitamente: "COMMIT PENDIENTE DE TU OK — no ejecuto `git commit` sin autorización".
**No tocar:** NO ejecutar `git commit` ni `git push` (gate duro humano); NO stagear `.env`, `*.db`, `*.ndjson`, `KILL`.
**Evidencia:** `.gitignore` endurecido (+`**/.env`, `*.ndjson`, `*.db/.sqlite`, `KILL`, `*.local.json`, `**/__pycache__/`, `**/sandbox/`, `ORACLE*_KILL`). `git add -A` → **31 files, 2337++/55--**. Verificación archivo-secreto (excluyendo `.env.example` que es plantilla vacía): **vacío**. `check-ignore` confirma `.env`, `audit.ndjson`, `settings.gate.local.json`, `__pycache__` IGNORADOS. Escaneo de contenido: sólo formas **redactadas** (`sk-ant-oat01-…`) en docs, `grep 'sk-ant-oat[0-9]{2}-[A-Za-z0-9]{20,}'` (token real) → vacío. `git ls-files | grep -iE '\.env$|\.ndjson$|\.db$|KILL$'` → nada secreto trackeado. Impreso el gate "COMMIT PENDIENTE DE TU OK". `git commit`/`push` NO ejecutados.

## == FASE 5 — Armonización documentada ==

## [done] 6. RUNBOOK de armonización: los 3 servicios bajo un mismo estándar
**Condición:** existe `infra/RUNBOOK-armonizacion.md` que documenta el estado armonizado de los 3 contenedores (`xe-canal-mando`, `agente-zenkai`, `agente-juanasanchez`): tabla con límites de memoria (todos 2 GiB), política de restart, logging, y el estado de cada deuda saldada (P1–P5) con el comando de verificación de cada una y el de reversa. Incluye la operación de backup y de la alerta.
**Check:** en la conversación: `ls -la infra/RUNBOOK-armonizacion.md` y `grep -cE 'xe-canal-mando|agente-zenkai|agente-juanasanchez' infra/RUNBOOK-armonizacion.md` ≥ 3; el archivo referencia P1–P5 y los scripts `backup-data.sh` y `watch-health.sh`.
**No tocar:** solo documentación (0 impacto en runtime).
**Evidencia:** `infra/RUNBOOK-armonizacion.md` creado (4290 B). `grep -c` de los 3 contenedores → **7** (≥3). Referencia `P1 P2 P3 P4 P5 backup-data.sh watch-health.sh`. Incluye tabla de estándar común (2 GiB/restart/logging/puertos), tabla P1–P5 con verificar+revertir, operación de backup/alerta/kill-switch, e invariantes respetados. Staged (re-verificado sin secretos).
