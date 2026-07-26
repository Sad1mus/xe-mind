# RUNBOOK — Armonización de infra (VPS 2.25.183.178)

**Fecha:** 2026-07-26 · **Host:** `srv1777083` · Ubuntu 24.04.4 LTS · Docker 29.6.2 · 15 GiB RAM · disco 7% usado.
Cierra las 5 deudas técnicas del reporte de infra del 2026-07-26. Todo lo aplicado es reversible.

---

## 1. Los tres servicios bajo un mismo estándar

| Contenedor | Rol | Puerto | mem_limit | restart | Compose |
|---|---|---|---|---|---|
| `xe-canal-mando` | Mente de Xe (Telegram → Claude Code) | ninguno (long-poll saliente) | 2 GiB | unless-stopped | `/srv/xe-mind/infra/canal-mando/compose.yml` |
| `agente-zenkai` | Cliente WhatsApp ZENKAI | `127.0.0.1:3001` | 2 GiB | unless-stopped | `/home/sadimus/agencia/agente-zenkai/docker-compose.yml` |
| `agente-juanasanchez` | Cliente WhatsApp Juana Sánchez | `127.0.0.1:3000` | 2 GiB *(P1)* | unless-stopped | `/home/sadimus/agencia/agente-juanasanchez/docker-compose.yml` |

**Estándar común:** memoria capada a 2 GiB (ningún cliente puede OOM-ear el host), `restart: unless-stopped`,
logging `json-file` con rotación, puertos sólo en loopback (los clientes) o sin puerto (Xe, long-poll saliente).

---

## 2. Estado de las deudas (P1–P5)

| # | Deuda | Estado | Verificar | Revertir |
|---|---|---|---|---|
| **P1** | Juana sin límite de memoria (podía OOM-ear el host) | ✅ 2 GiB en vivo + persistido | `docker inspect agente-juanasanchez --format '{{.HostConfig.Memory}}'` → `2147483648` | `docker update --memory 0 --memory-swap -1 agente-juanasanchez` + restaurar `docker-compose.yml.bak-premem` |
| **P2** | Código de infra sin versionar | ✅ staged sin secretos (commit = gate humano) | `git -C /home/sadimus/Documentos/Agencia/xe-mind status --short` | `git reset` (des-stagea) |
| **P3** | Volumen `/data` sin backup | ✅ backup diario + rotación 14d | `ls /srv/backups/xe-canal/` · `crontab -l \| grep backup-data` | quitar la línea del `crontab -e` |
| **P4** | Sin alerta si un contenedor cae | ✅ vigía cada 5 min → Telegram | `watch-health.sh --dry-run` · `crontab -l \| grep watch-health` | quitar la línea del `crontab -e` |
| **P5** | `classify.ts` no cubría MCP/ToolSearch (bloqueaba de más) | ✅ `ToolSearch`→read, MCP-pago→money, default `baja` intacto | `TSX_BIN=<tsx> <tsx> oracle.hook.ts` → 15/15, exit 0 | revertir el commit de `classify.ts` |

---

## 3. Operación

### Backup (`P3`) — `backup-data.sh`
- **Qué hace:** copia online (consistente) de `registro.db` vía SQLite backup API dentro del contenedor + saca `registro.bak.db` y `audit.ndjson` al host, verifica `PRAGMA integrity_check=ok`, rota 14 días.
- **Cron:** `15 3 * * *` → `/var/log/xe-backup.log`. **Manual:** `/srv/xe-mind/infra/canal-mando/backup-data.sh`.
- **Destino:** `/srv/backups/xe-canal/AAAA-MM-DD/`.
- **Restaurar:** parar Xe, copiar el `registro.bak.db` elegido al volumen `/data/registro.db`, levantar Xe.

### Alerta de salud (`P4`) — `watch-health.sh`
- **Qué hace:** revisa `xe-canal-mando` (por healthcheck) y los dos clientes (por `State.Running`); si alguno no está sano, avisa por Telegram **sólo al chat 19950645** (token leído del `.env`, nunca impreso). **Nunca reinicia nada.**
- **Cron:** `*/5 * * * *` → `/var/log/xe-watch.log`. **Probar:** `watch-health.sh --dry-run` (sano → "todo sano"; `--dry-run <nombre>` fuerza el camino de alerta).

### Kill-switch de Xe (freno duro, GUARDA-006)
```bash
ssh root@2.25.183.178 'docker exec xe-canal-mando touch /data/KILL'   # frena TODA ejecución de Xe
ssh root@2.25.183.178 'docker exec xe-canal-mando rm -f /data/KILL'   # reactiva
```

### Chequeo rápido de todo
```bash
ssh root@2.25.183.178 'docker ps --format "table {{.Names}}\t{{.Status}}"'
ssh root@2.25.183.178 'docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"'
ssh root@2.25.183.178 '/srv/xe-mind/infra/canal-mando/watch-health.sh --dry-run'
```

---

## 4. Invariantes respetados en esta armonización
- Juana y ZENKAI **nunca se reiniciaron** (P1 se aplicó en vivo con `docker update`; `StartedAt` sin cambios).
- **Cero secretos** versionados; el `git commit` es gate humano (no se ejecutó).
- Las alertas van **sólo** al chat autorizado; ningún script escribe a clientes ni ejecuta dinero.
- Cero API key (Xe sigue autenticando por token de suscripción).
