# Canal de mando de Xe — Claude Code headless (suscripción) + connectors del substrato.
# Imagen: node (bridge grammY + tsx) + python3 (registro/reporte, SQLite stdlib) + claude CLI.
# AUTENTICACIÓN por suscripción: el token de `claude setup-token` entra por env
# (CLAUDE_CODE_OAUTH_TOKEN), NUNCA se hornea en la imagen.
FROM node:22-bookworm-slim

# python3 para los connectors del registro/reporte (sqlite3 es stdlib); procps para el healthcheck (pgrep).
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 ca-certificates procps \
 && rm -rf /var/lib/apt/lists/*

# Claude Code CLI, versión PINEADA (GUARDA: nada de tags flotantes).
RUN npm install -g @anthropic-ai/claude-code@2.1.219

WORKDIR /app

# Deps del canal (grammy + tsx, ambas runtime). Manifiesto primero (cache de capa).
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

# Código del canal (.ts) + settings del gate-hook (.json). `COPY *.ts` NO trae el json.
COPY *.ts ./
COPY settings.gate.json ./

# Usuario no-root (mínimo privilegio). HOME propio para el token/cache de claude.
# /data pre-creado y de app: en un volumen NUEVO hereda esta propiedad (evita el trap root-owned).
RUN useradd --create-home --uid 10001 app \
 && mkdir -p /data \
 && chown -R app:app /app /data
ENV HOME=/home/app
USER app

# Fase 1: solo lectura. Se puede pisar por env-file en runtime.
ENV EXEC_MODE=read_only \
    NODE_ENV=production

# Healthcheck por proceso: el bridge de Telegram es long-poll SALIENTE (no expone puerto).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD pgrep -f "bridge.telegram" >/dev/null || exit 1

# tsx corre el .ts directo (sin build step). El bridge arranca el long-poll.
CMD ["npx", "tsx", "bridge.telegram.ts"]
