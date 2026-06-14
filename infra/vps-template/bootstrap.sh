#!/usr/bin/env bash
#
# bootstrap.sh — tooling del ingeniero para un VPS nuevo (plantilla SPEC-001)
#
# Instala, de forma idempotente: tmux + lazygit + lazydocker + arreglo del
# terminfo de Ghostty para SSH. NO hace hardening ni instala Docker/Coolify:
# eso es otra fase (ver G-4 y design en docs/specs/SPEC-001).
#
# Uso (en el VPS, como tu usuario con sudo):
#   curl -fsSL <raw-url-de-este-archivo> -o bootstrap.sh && bash bootstrap.sh
#   # o, si ya clonaste el repo:  bash infra/vps-template/bootstrap.sh
#
# Probado para Debian/Ubuntu (default de Hetzner). Releases vía API de GitHub:
# NO fija versiones a mano (toma siempre la última estable).

set -euo pipefail

# --- helpers ---------------------------------------------------------------
log()  { printf '\033[1;32m[bootstrap]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[bootstrap]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[bootstrap]\033[0m %s\n' "$*" >&2; exit 1; }

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  command -v sudo >/dev/null 2>&1 || die "No sos root y no hay sudo. Corré como root o instalá sudo."
  SUDO="sudo"
fi

# Mapea uname -m al nombre de arch que usan los releases de los lazy*.
case "$(uname -m)" in
  x86_64|amd64)  LAZY_ARCH="x86_64" ;;
  aarch64|arm64) LAZY_ARCH="arm64"  ;;
  *) die "Arquitectura no soportada por este script: $(uname -m)" ;;
esac

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
BIN_DIR="/usr/local/bin"

need() { command -v "$1" >/dev/null 2>&1; }

# Instala desde el último release de GitHub un binario empaquetado en .tar.gz.
#   $1 repo (owner/name)  $2 nombre del binario  $3 patrón del asset con {ver}
install_from_release() {
  local repo="$1" bin="$2" asset_tpl="$3"
  local ver asset url
  ver="$(curl -fsSL "https://api.github.com/repos/${repo}/releases/latest" \
        | grep -oP '"tag_name":\s*"v?\K[^"]+')" || die "No pude leer la última versión de ${repo}"
  [ -n "$ver" ] || die "Versión vacía para ${repo} (¿rate limit de la API de GitHub?)"
  asset="${asset_tpl//\{ver\}/$ver}"
  url="https://github.com/${repo}/releases/download/v${ver}/${asset}"
  log "Instalando ${bin} v${ver} (${LAZY_ARCH})..."
  curl -fsSL "$url" -o "${TMP}/${bin}.tar.gz" || die "Descarga falló: $url"
  tar -xzf "${TMP}/${bin}.tar.gz" -C "$TMP" "$bin"
  $SUDO install -m 0755 "${TMP}/${bin}" "${BIN_DIR}/${bin}"
}

# --- 1) paquetes base via apt ----------------------------------------------
if need apt-get; then
  log "Actualizando índice de apt e instalando base (tmux, git, curl, tar, ncurses)..."
  $SUDO apt-get update -qq
  $SUDO apt-get install -y -qq tmux git curl ca-certificates tar ncurses-bin
else
  warn "No hay apt-get. Instalá manualmente: tmux git curl tar (ncurses con 'tic')."
fi

# --- 2) lazygit -------------------------------------------------------------
# Asset oficial p.ej.: lazygit_0.44.2_Linux_x86_64.tar.gz
install_from_release "jesseduffield/lazygit"    "lazygit"    "lazygit_{ver}_Linux_${LAZY_ARCH}.tar.gz"

# --- 3) lazydocker ----------------------------------------------------------
# Asset oficial p.ej.: lazydocker_0.24.1_Linux_x86_64.tar.gz
install_from_release "jesseduffield/lazydocker" "lazydocker" "lazydocker_{ver}_Linux_${LAZY_ARCH}.tar.gz"
warn "lazydocker necesita Docker corriendo para servir de algo (lo provee Coolify en la fase de infra)."

# --- 4) terminfo de Ghostty para SSH ---------------------------------------
# Lo correcto y recomendado por Ghostty es exportar el terminfo DESDE tu máquina
# local hacia el VPS (una sola vez, desde tu terminal Ghostty local):
#
#     infocmp -x xterm-ghostty | ssh USER@HOST -- tic -x -
#
# Este script no puede hacer eso (corre en el VPS, no tiene tu terminfo local),
# así que deja un fallback que NO puede fallar: si el TERM entrante no tiene
# terminfo instalado acá, lo degrada a xterm-256color para no romper teclas/colores.
RC="${HOME}/.bashrc"
MARKER="# >>> ghostty/term fallback (bootstrap SPEC-001) >>>"
if ! grep -qF "$MARKER" "$RC" 2>/dev/null; then
  log "Agregando fallback de TERM a ${RC}"
  {
    printf '\n%s\n' "$MARKER"
    printf 'if ! infocmp "$TERM" >/dev/null 2>&1; then export TERM=xterm-256color; fi\n'
    printf '%s\n' "# <<< ghostty/term fallback (bootstrap SPEC-001) <<<"
  } >> "$RC"
else
  log "Fallback de TERM ya presente en ${RC} (idempotente, no toco nada)."
fi

# --- resumen ----------------------------------------------------------------
log "Listo. Versiones instaladas:"
printf '  tmux       : %s\n' "$(tmux -V 2>/dev/null || echo 'NO')"
printf '  lazygit    : %s\n' "$(lazygit --version 2>/dev/null | head -n1 || echo 'NO')"
printf '  lazydocker : %s\n' "$(lazydocker --version 2>/dev/null | head -n1 || echo 'NO')"
echo
log "Recomendado (corré ESTO desde tu Ghostty LOCAL para terminfo nativo):"
echo "    infocmp -x xterm-ghostty | ssh ${USER}@<IP-del-vps> -- tic -x -"
log "Recordá: el hardening (firewall/SSH-key-only/no-root/fail2ban, G-4) es aparte."
