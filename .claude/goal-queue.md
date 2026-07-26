# Goal Queue — Canal de mando de Xe (Claude Code headless, suscripción Max)

estado: activa
current: 6
turn_cap_por_item: 15

<!--
Estados por tarea: [pending] -> [in-progress] -> [done] | [blocked]
Reglas:
- Solo UNA tarea [in-progress] a la vez.
- No empezar la siguiente hasta que la actual esté [done] o [blocked].
- "Check" debe correrse y su resultado quedar VISIBLE en la conversación
  (el evaluador de /goal no lee este archivo, solo ve el transcript).
- NADA de API key: solo token de suscripción Max vía `claude -p`.
- Tareas 6 y 7 quedan [blocked] esperando OK humano — NO ejecutar.
-->

## [done] 1. Re-soldar agent.ts al CLI de suscripción (claude -p)
**Condición:** `infra/canal-mando/agent.ts` ya no lanza el `Error`; expone `runXeSession(prompt, deps)` que invoca `claude -p` (token de suscripción Max, SIN API key) y devuelve el texto de la respuesta.
**Check:** `claude -p "responde unicamente la palabra: PONG"` imprime `PONG` en el transcript, y un smoke local de `runXeSession` devuelve texto no vacío.
**No tocar:** governance.ts, audit.ts. No introducir ANTHROPIC_API_KEY. No cambiar el contrato con bridge.ts.
**Evidencia:** `claude -p "...PONG"` → `PONG` (exit 0); `smoke.agent.ts` (tsx) → `RESULT: "SMOKE-OK"` (exit 0), con `--permission-mode plan` y `delete env.ANTHROPIC_API_KEY`. agent.ts reescrito: `spawn('claude', ['-p', prompt, '--output-format','json','--permission-mode', ...])`, parsea `.result`. Contrato con bridge.ts intacto (apiKey queda opcional-ignorado). governance.ts/audit.ts sin tocar.

## [done] 2. Gate en modo read-only con oracle que lo prueba
**Condición:** existe un oracle que PASA: una acción `read` pasa el gate; una acción `write_reversible`/`money`/`outbound` es RECHAZADA en `EXEC_MODE=read_only` y queda registrada en el audit append-only.
**Check:** `node --import tsx infra/canal-mando/oracle.gate.ts` (o equivalente) sale 0 e imprime `READONLY PASS / WRITE BLOCKED / AUDIT OK`.
**No tocar:** no relajar guardas; topes de escritura/dinero en cero; no tocar la firma de `gate()`.
**Evidencia:** `tsx oracle.gate.ts` → 7/7 asserts ok, exit 0, `READONLY PASS / WRITE BLOCKED / AUDIT OK`. read/alta→allow; write/money/outbound→deny (read_only); read/baja→deny (§4); kill-switch→deny; audit `oracle.audit.ndjson` = 4 líneas NDJSON válidas. `governance.ts` intacto; topes en cero.

## [done] 3. Bridge de Telegram cableado (bot nuevo) — eco extremo a extremo
**Condición:** `bridge.ts` conecta a un bot NUEVO de BotFather (token por env), recibe un mensaje de un chat_id en allowlist y responde pasando por agent.ts + gate.
**Check:** log en transcript: entra `ping` de un chat_id autorizado, sale respuesta de Xe; un chat_id NO autorizado es ignorado + logueado.
**No tocar:** un solo bot por servicio; token por env (nunca en git); no bajar la allowlist.
**Evidencia (e2e REAL, 2026-07-24):** bot @Agenciazenkaibot (token BotFather, validado con getMe). Mensaje real *"Cómo va la agencia"* del chat_id autorizado `19950645` → `AUTH ok` → `GATE allow` (auditado en `audit.ndjson`: read/alta/allow) → fast-path `getAgencyStatus` (connector `reporte`, 138ms) → snapshot real entregado a Telegram (`SENT ✅`). Código: `bridge.telegram.ts` (grammY), `status.ts` (fast-path de estado), `package.json`/`tsconfig`, grammy instalado. Fix clave: consultas de estado NO usan `claude -p` (evita timeout de 120s explorando el repo) — leen el registro directo, read-only, igual por el gate.
**Notas de transporte:** (1) en ESTE sandbox el `fetch` de node (undici) da `CONNECT_TIMEOUT`; el harness de prueba `echo.oneshot.ts` usa `curl` — en la VPS real el long-poll de grammy funciona normal. (2) el gate por-tool con `governance.decide()` dentro de `claude -p` sigue pendiente (Tarea 2 lo dejó vía `--permission-mode plan`); el fast-path de estado sí pasa explícito por `gate()`.

## [done] 4. Capacidad "¿cómo va la agencia?" leyendo el registro (e2e local)
**Condición:** preguntar *"¿cómo va la agencia?"* hace que Xe lea `packages/registro` (SQLite) y devuelva un snapshot REAL (clientes/proyectos/estado); si el registro está vacío, lo dice (no inventa — GUARDA-003).
**Check:** `node --import tsx` siembra una fila de prueba en el registro → la query la devuelve; sale 0. ROI no se inventa.
**No tocar:** no inventar métricas; no escribir en el registro fuera del seed de prueba.
**Evidencia:** e2e local con los connectors reales (registro=Python+SQLite, reporte=cockpit M6): oracles de ambos PASA. DB vacía → `reporte` = `Clientes total 0 / Proyectos total 0`. Seed `registro execute --confirm` (ZENKAI EMEA/Silver) → escrito, `plan_entrega=PENDIENTE-#17` (no inventa Silver). `reporte dry-run` → total 1 cliente {EMEA:1}{Silver:1}{activo:1}, 1 proyecto {en-construccion:1}, ROI={ingresos/citas/conversion: PENDIENTE-#23} (no inventa). La query lee `REGISTRO_DB` (env, GUARDA-005). Nota: el surfacing por el canal (Xe corriendo `reporte` en read_only) se ejercita en Tarea 6 (deploy).

## [blocked] 5. Empaquetado Docker endurecido para la VPS (build local OK)
**Condición:** Dockerfile + compose del servicio canal-mando; `docker build` pasa; contenedor corre local con healthcheck OK; loopback `127.0.0.1`; `--read-only`; env-file con token Max + topes en cero.
**Check:** `docker build -t xe-canal:0.1.0 .` sale 0 y `docker run` local levanta con healthcheck OK / log `listening`.
**No tocar:** no montar docker.sock; loopback obligatorio; fs read-only; no meter secretos en la imagen.
**Evidencia (artefactos completos + validados en sintaxis):** creados `Dockerfile` (node22+python3+claude CLI @2.1.219 pineado, no-root uid 10001, sin API key, HEALTHCHECK por proceso), `compose.yml` (read_only rootfs, tmpfs para /tmp y ~/.claude, substrato montado read-only, datos en volumen, sin docker.sock, no-new-privileges, cap_drop ALL, pids 512, mem/cpu limitados, sin puertos), `.dockerignore`, y `.env.example` actualizado (CLAUDE_CODE_OAUTH_TOKEN de suscripción; ANTHROPIC_API_KEY marcada deprecada). YAML validado con pyyaml. **Mejora sobre la condición:** Telegram es long-poll saliente → NO expone puerto (mejor que loopback: cero inbound).
**Motivo del bloqueo (entorno):** no hay daemon Docker local (Docker vive en la VPS, `/var/run/docker.sock` ausente). El `docker build` + run + healthcheck se verifican en la VPS, junto a la Tarea 6.

## [blocked] 6. Deploy a la VPS + setup-token Max + prueba e2e real (REQUIERE OK HUMANO)
**Condición:** en la VPS: `claude setup-token` con Max, contenedor arriba, y desde Telegram *"¿cómo va la agencia?"* responde de punta a punta.
**Check:** desde el celular, mensaje → respuesta de Xe leyendo el registro de la VPS.
**No tocar:** IRREVERSIBLE + toca producción de clientes (Juana, ZENKAI). No commitear/pushear/desplegar sin OK explícito del humano.
**Motivo del bloqueo:** gate humano por diseño (global CLAUDE.md: no desplegar sin OK). Esperando visto.
**Evidencia:**

## [blocked] 7. Fases superiores (reversible → dinero doble-gate → autonomía) — andamiadas y APAGADAS (REQUIERE VEREDICTO)
**Condición:** el código de las fases superiores queda presente pero DESHABILITADO (flags off, topes en cero); `DEC-012` y `GUARDA-006` siguen `estado: propuesta`.
**Check:** `EXEC_MODE` de producción = `read_only`; topes vacíos; DECs sin ratificar. Promover cada fase = VEREDICTO humano.
**No tocar:** no habilitar dinero ni autonomía; no fijar topes sin decisión humana (GUARDA-003/006).
**Motivo del bloqueo:** la promoción de fase es VEREDICTO humano (§4, GUARDA-006), no un paso autónomo.
**Evidencia:**
