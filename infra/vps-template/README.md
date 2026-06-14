# infra/vps-template — Plantilla de VPS (SPEC-001)

Tooling reusable para aprovisionar el **entorno del ingeniero** en un VPS nuevo.
Parte de `docs/specs/SPEC-001-plataforma-entrega-cliente.md` (fase `spec`).

> **Alcance:** solo herramientas de trabajo (tmux + lazygit + lazydocker + terminfo).
> **Fuera de alcance:** hardening (G-4), Docker/Coolify, deploy de apps de cliente.
> Eso se define en la fase `design` de SPEC-001 y NO está acá a propósito.

## `bootstrap.sh`

Instala, idempotente, en Debian/Ubuntu (default de Hetzner):

- **tmux** — sesiones persistentes que sobreviven al SSH.
- **lazygit** — TUI de git (última versión vía API de GitHub, sin versión fija).
- **lazydocker** — TUI de Docker/Coolify (necesita Docker corriendo para servir).
- **Fallback de terminfo** — si conectás desde Ghostty y el VPS no tiene
  `xterm-ghostty`, degrada `TERM` a `xterm-256color` para no romper teclas/colores.

### Uso

```bash
# opción A: con el repo clonado en el VPS
bash infra/vps-template/bootstrap.sh

# opción B: suelto
curl -fsSL <raw-url> -o bootstrap.sh && bash bootstrap.sh
```

### Terminfo nativo (recomendado, una sola vez desde tu Ghostty LOCAL)

El fallback evita que algo se rompa, pero para el terminfo real de Ghostty,
corré esto **desde tu máquina local** (no desde el VPS):

```bash
infocmp -x xterm-ghostty | ssh USER@IP-del-vps -- tic -x -
```

## Stack de capas (recordatorio)

`Ghostty` (ventana local) → `tmux` (sesión persistente en el VPS) → `lazygit`/`lazydocker` (TUIs adentro).
Son complementarios, no se reemplazan.
