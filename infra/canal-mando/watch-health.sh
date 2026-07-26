#!/usr/bin/env bash
# watch-health.sh — Vigía de salud de contenedores (P4).
# Si algún contenedor no está sano, avisa por Telegram SOLO al chat autorizado.
# NUNCA reinicia nada: sólo observa y alerta. El token se lee del .env (600) y no se imprime.
#
# Uso:
#   watch-health.sh              -> chequea y, si hay problema, ENVÍA la alerta
#   watch-health.sh --dry-run    -> chequea e IMPRIME lo que enviaría (no envía)
#   watch-health.sh --dry-run X   -> fuerza chequear el contenedor X (para probar el camino "caído")
set -uo pipefail

ENV_FILE="/srv/xe-mind/infra/canal-mando/.env"
ALLOWED_CHAT_ID="19950645"
DRY=0
OVERRIDE=()

for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    *) OVERRIDE+=("$a") ;;
  esac
done

# contenedor:modo  (health = por healthcheck; running = por State.Running)
DEFAULTS=("xe-canal-mando:health" "agente-juanasanchez:running" "agente-zenkai:running")

status_of() { # name mode  -> stdout: OK | motivo ; return 0 si sano, 1 si no
  local name="$1" mode="$2" val
  if ! docker inspect "$name" >/dev/null 2>&1; then
    echo "no existe / caído"; return 1
  fi
  if [ "$mode" = "health" ]; then
    val="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$name")"
    if [ "$val" = "healthy" ]; then echo OK; return 0; else echo "health=$val"; return 1; fi
  else
    val="$(docker inspect --format '{{.State.Running}}' "$name")"
    if [ "$val" = "true" ]; then echo OK; return 0; else echo "running=$val"; return 1; fi
  fi
}

if [ "${#OVERRIDE[@]}" -gt 0 ]; then
  LIST=(); for n in "${OVERRIDE[@]}"; do LIST+=("$n:running"); done
else
  LIST=("${DEFAULTS[@]}")
fi

PROBLEMS=()
for entry in "${LIST[@]}"; do
  name="${entry%%:*}"; mode="${entry##*:}"
  reason="$(status_of "$name" "$mode")" || PROBLEMS+=("${name}: ${reason}")
done

if [ "${#PROBLEMS[@]}" -eq 0 ]; then
  echo "todo sano, no alerta"
  exit 0
fi

MSG="⚠️ Xe/VPS — contenedor(es) con problema:"$'\n'"$(printf '• %s\n' "${PROBLEMS[@]}")"

if [ "$DRY" -eq 1 ]; then
  echo "[DRY-RUN] enviaría a chat ${ALLOWED_CHAT_ID}:"
  printf '%s\n' "$MSG"
  exit 0
fi

TOKEN="$(grep -E '^TELEGRAM_BOT_TOKEN=' "$ENV_FILE" | head -1 | cut -d= -f2- | sed -e 's/^[[:space:]"'\'']*//' -e 's/[[:space:]"'\'']*$//')"
if [ -z "$TOKEN" ]; then echo "sin TELEGRAM_BOT_TOKEN en ${ENV_FILE}"; exit 1; fi
RESP="$(curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${ALLOWED_CHAT_ID}" \
  --data-urlencode "text=${MSG}")"
if printf '%s' "$RESP" | grep -q '"ok":true'; then
  echo "alerta enviada a ${ALLOWED_CHAT_ID} (Telegram ok)"
else
  echo "FALLO al enviar: $(printf '%s' "$RESP" | head -c 200)"
  exit 1
fi
