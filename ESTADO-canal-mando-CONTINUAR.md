# Xe operativa en la VPS — Estado y cómo continuar

**Última sesión:** 2026-07-24 · **Para retomar:** leé la sección 8 (Próximos pasos).

---

## 1. Resumen en 30 segundos

- **Xe está VIVA 24/7 en la VPS**, comandable desde Telegram (@Agenciazenkaibot), en modo **`reversible`**: ejecuta todo lo reversible; **dinero/firma/envío-al-cliente los REDACTA, no los ejecuta** (GUARDA-001).
- Autentica con **token de suscripción** (`claude setup-token`) — **cero API key**.
- El gate vive en **código** (`gate-hook` PreToolUse): cada tool-call de Xe pasa por `governance.gate()` antes de ejecutarse. Verificado end-to-end.
- **Quedan 2 tareas:** (8) confirmar la prueba desde el celular (reversible + dinero), (9) Fase D = automatizar los packages uno por uno con tu VEREDICTO.

---

## 2. Qué está corriendo ahora mismo (cómo hablarle)

- **Bot:** @Agenciazenkaibot. **Allowlist:** solo tu chat_id `19950645` (ignora a cualquier otro).
- Le escribís y **ejecuta de verdad**. Ejemplos:
  - `¿cómo va la agencia?` → estado del registro (fast-path, instantáneo).
  - `creá un archivo /tmp/hola.txt con "..."` → lo hace (reversible).
  - `cobrale 500 dólares a un cliente` → **se frena y te lo redacta** (dinero = humano).
- **Prueba parcial de hoy:** mandaste un mensaje, el audit registró `read | reporte_dry_run | allow` → el canal recibe (grammy pollea bien en la VPS), el gate autoriza, Xe corre el fast-path. **Falta confirmar** que te llegó la respuesta + probar la orden reversible y la de dinero.

---

## 3. Arquitectura (cómo funciona, de punta a punta)

```
Telegram (@Agenciazenkaibot, solo chat_id 19950645)
   │  long-poll (grammy)
   ▼
bridge.telegram.ts  →  bridge.ts (handleMessage: allowlist → fast-path o Xe)
   │                         │
   │  ¿es consulta de estado? → status.ts → connector reporte (read-only, <1s)
   │  si es orden operativa   ↓
   ▼
agent.ts (runXeSession) → `claude -p` (suscripción, EXEC_MODE=reversible, cwd=/repo)
   │  cada tool-call →  --settings settings.gate.json  →  gate-hook.ts:
   │     classify(tool) → governance.gate():
   │        read / write_reversible          → ALLOW (ejecuta)
   │        money / outbound (dinero/envío)   → DENY  → Xe REDACTA para el humano
   │        confianza baja / kill-switch      → DENY
   ▼
audit.ndjson (append-only, cada decisión)   ·   registro SQLite (verdad exacta)
```

**Principio que no se negocia:** el gate está en CÓDIGO, no en el prompt. Ninguna instrucción del system prompt lo salta.

---

## 4. Mapa de fases (megagoal)

Plan maestro: **`.claude/megagoal-canal-mando.md`**. Ejes: NORTE = Xe opera toda la agencia por Telegram; único límite = dinero (humano).

| Fase | Qué | Estado |
|---|---|---|
| **0** | Canal read-only (bot, gate, memoria, fast-path) | ✅ cerrada |
| **A** | "Xe con manos" (classify + gate-hook + agent operativo) | ✅ cerrada |
| **B** | Telegram opera con manos (bridge operativo, e2e) | ✅ cerrada |
| **C** | Deploy a la VPS 24/7 (`reversible`) | ✅ cerrada (7/9 del goal) |
| **8** | e2e desde el celular | ⏳ parcial (falta confirmar reversible + dinero) |
| **D** | Automatizar packages: registro→onboarding→reporte→multi-agente | ⏸ pendiente (VEREDICTO tuyo) |

Cola ejecutable de esta sesión: **`.claude/goal-queue-operativa.md`** (7 done, 2 pendientes de vos).

---

## 5. Dónde vive todo

**En la VPS (`root@2.25.183.178`, llave id_ed25519):**
- Código + compose + `.env`: `/srv/xe-mind/infra/canal-mando/`
- Repo (constitución + packages + vault, montado read-only en `/repo`): `/srv/xe-mind/`
- `.env` (600, secretos): `/srv/xe-mind/infra/canal-mando/.env`
- Imagen: `agencia/xe-canal-mando:0.1.0` · Contenedor: `xe-canal-mando`
- Volumen `/data` (`canal-mando_xe-canal-data`): `registro.db`, `audit.ndjson`, `KILL`
- **Convivencia:** `agente-juanasanchez` y `agente-zenkai` intactos (nunca se tocaron).

**En el PC (`~/Documentos/Agencia/xe-mind/infra/canal-mando/`):**
- `governance.ts` (el gate, núcleo) · `classify.ts` (tool→kind) · `gate-hook.ts` (PreToolUse) · `agent.ts` (claude -p, modo operativo) · `bridge.ts` (core) · `bridge.telegram.ts` (grammy) · `status.ts` (fast-path) · `audit.ts`
- Settings: `settings.gate.json` (contenedor) · `settings.gate.local.json` (PC)
- Oráculos/harness: `oracle.gate.ts`, `oracle.hook.ts`, `smoke.hands.ts`, `e2e.hands.ts`, `e2e.bridge.ts`
- `Dockerfile`, `compose.yml`, `.dockerignore`, `.env.example`
- **tsx local:** se reusa el de `grupojuana/agente-wa/node_modules/.bin/tsx` (este node no tiene TS nativo).

---

## 6. Operación (comandos útiles)

```bash
# ¿Está viva?
ssh root@2.25.183.178 'docker ps --filter name=xe-canal-mando'

# Logs
ssh root@2.25.183.178 'docker logs --tail 30 xe-canal-mando'

# Ver el audit (decisiones del gate)
ssh root@2.25.183.178 'docker exec xe-canal-mando tail -20 /data/audit.ndjson'

# KILL-SWITCH (frena TODA ejecución de Xe al instante)
ssh root@2.25.183.178 'docker exec xe-canal-mando touch /data/KILL'   # activar
ssh root@2.25.183.178 'docker exec xe-canal-mando rm -f /data/KILL'   # desactivar

# Reiniciar / apagar / actualizar
ssh root@2.25.183.178 'cd /srv/xe-mind/infra/canal-mando && docker compose restart'
ssh root@2.25.183.178 'cd /srv/xe-mind/infra/canal-mando && docker compose down'
# tras cambiar código: rsync al VPS + docker compose up -d --build
```

Panel/puerto: **ninguno** — Telegram es long-poll saliente (cero superficie inbound).

---

## 7. Secretos (NO están en este archivo)

- **Token de suscripción** (`CLAUDE_CODE_OAUTH_TOKEN`, `sk-ant-oat…`): solo en `/srv/xe-mind/infra/canal-mando/.env` (600). Es la llave de tu Max — rotable con `claude setup-token` de nuevo.
- **Token del bot** (`TELEGRAM_BOT_TOKEN`): en el mismo `.env`. Rotable con `/revoke` en @BotFather.
- Ninguno se commitea (`.env` está en `.gitignore`) ni se imprime en logs.

---

## 8. Próximos pasos (mañana, en orden)

1. **Cerrar la tarea 8** (5 min, vos): desde el celular a @Agenciazenkaibot —
   - `¿cómo va la agencia?` → confirmá que te llega la respuesta.
   - `creá un archivo /tmp/hola.txt con "Xe estuvo acá"` → debe ejecutarlo.
   - `cobrale 500 dólares a un cliente` → debe **frenarse y redactar**.
   - Yo reviso los logs y muestro `write→allow` y `money→deny` auditados.
2. **Fase D — automatizar packages** (goal nuevo, uno por vez con tu VEREDICTO):
   - Empezar por **registro**: que Xe, desde Telegram, dé de alta un cliente end-to-end (dry-run + execute reversible en la DB de la VPS).
   - Luego onboarding → reporte → multi-agente, mismo patrón.

---

## 9. Decisiones abiertas / pendientes de tu VEREDICTO

- **Ratificar DEC-012 + GUARDA-006** (hoy `propuesta`) — es lo que oficializa subir de fase.
- **Topes (GUARDA-006):** hoy los de tokens operativos están altos (2M/sesión) y los de dinero en 0 (dinero = humano). Definir los definitivos.
- **Substrato escribible:** hoy `/repo` (vault Obsidian + código) está montado **read-only** (Xe no puede reescribir su constitución ni el vault — es lo seguro). Si querés que Xe escriba memoria/handoffs en el vault, hay que montar una ruta escribible aparte. Decisión para Fase D+.
- **¿Fase money_double_gate?** Cuando le tengas confianza, se puede habilitar que Xe *ejecute* dinero tras tu doble-confirm por Telegram (hoy solo redacta). Va después, con topes definidos.
- **Orden de automatización de packages** (Fase D): propuesta = registro primero.

---

## 10. Gotchas cazados (para no repetirlos)

- `isStatusQuery` matcheaba "agencia" en cualquier parte → misruteaba órdenes al fast-path. **Corregido** (verbos de acción descartan el fast-path).
- `tsx` debía ser **runtime dependency** (estaba en devDeps + `NODE_ENV=production` → no se instalaba).
- `COPY *.ts` **no** copia `settings.gate.json` → hay `COPY settings.gate.json` explícito.
- Volumen `/data` nace **root-owned** → uid 10001 no podía escribir (registro/audit). Corregido con chown + `mkdir/chown /data` en el Dockerfile.
- `node:22-slim` **sin `procps`** → el healthcheck `pgrep` fallaba (unhealthy). Corregido agregando `procps`.
- Con topes en 0, `checkCaps` frena hasta lo reversible (0>=0) → los topes de **tokens operativos deben ser > 0** (los de dinero sí van en 0).
- El `fetch` de node (undici) da CONNECT_TIMEOUT en el sandbox local (no en la VPS) → los harness locales de Telegram usan `curl`.
- **Nada commiteado** todavía (gate duro: no commitear/pushear sin tu OK).
