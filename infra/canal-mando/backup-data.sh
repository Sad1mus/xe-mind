#!/usr/bin/env bash
# backup-data.sh — Respaldo consistente del volumen /data de xe-canal-mando (P3).
# Copia online de registro.db (SQLite backup API, consistente aunque la DB esté en uso)
# + audit.ndjson → host, con verificación de integridad y rotación por días.
# Idempotente. Pensado para cron diario. NO reinicia nada; sólo lee/copia.
set -euo pipefail

CONTAINER="xe-canal-mando"
DEST_ROOT="/srv/backups/xe-canal"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
STAMP="$(date +%F)"                 # YYYY-MM-DD
DEST="${DEST_ROOT}/${STAMP}"

mkdir -p "${DEST}"

# 1. Backup online de SQLite dentro del contenedor (python3 stdlib, sin sqlite3 CLI).
docker exec "${CONTAINER}" python3 -c \
  "import sqlite3; s=sqlite3.connect('/data/registro.db'); d=sqlite3.connect('/data/registro.bak.db'); s.backup(d); d.close(); s.close()"

# 2. Sacar la copia + el audit al host.
docker cp "${CONTAINER}:/data/registro.bak.db" "${DEST}/registro.bak.db"
docker cp "${CONTAINER}:/data/audit.ndjson" "${DEST}/audit.ndjson" 2>/dev/null || echo "(sin audit.ndjson aún)"

# 3. Limpiar el temporal dentro del contenedor (el volumen /data es escribible).
docker exec "${CONTAINER}" rm -f /data/registro.bak.db

# 4. Verificar integridad del backup recién hecho (python3 stdlib del host).
INTEG="$(python3 -c "import sqlite3; print(sqlite3.connect('${DEST}/registro.bak.db').execute('PRAGMA integrity_check').fetchone()[0])")"
echo "integrity_check=${INTEG}"
[ "${INTEG}" = "ok" ] || { echo "BACKUP CORRUPTO — integrity_check != ok"; exit 1; }

# 5. Rotación: borrar backups de directorios más viejos que RETENTION_DAYS.
find "${DEST_ROOT}" -mindepth 1 -maxdepth 1 -type d -name '20*' -mtime "+${RETENTION_DAYS}" -exec rm -rf {} \;

echo "backup OK → ${DEST} (registro.bak.db + audit.ndjson; retención ${RETENTION_DAYS}d)"
