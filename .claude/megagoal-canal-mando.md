# MEGAGOAL — Xe operando la agencia desde Telegram (canal de mando)

> **Cola, no monolito.** Un solo goal activo a la vez; cada condición de cierre es **falsable y citada**; no se sube de fase sin **VEREDICTO humano**. Destilado del vault ([[DEC-012]], [[GUARDA-001]], [[GUARDA-006]], CLAUDE.md §4/§5); lo no firmado va como 🚧, no se inventa ([[GUARDA-003]]).
>
> **Eje:** este megagoal es el **OPERADOR** (Xe gobernando la agencia), distinto de `megagoal.md` que es el **PRODUCTO** (portafolio Gold). Se tocan, no se pisan.
>
> **Regla de honestidad:** `oracle PASA` ≠ fase cerrada. Solo un VEREDICTO humano cierra (CLAUDE.md §0/§8).

---

## 🥇 NORTE — Xe hace TODO lo operativo de la agencia, comandada por vos vía Telegram

Xe vive 24/7 en la VPS, con su memoria (Obsidian/vault + SQLite/registro), y **ejecuta**: da de alta clientes, mueve proyectos, corre los `packages` (registro·onboarding·reporte·multi-agente), orquesta agentes de clientes, toca código y substrato. Vos le hablás por Telegram y ella opera.

**La única frontera (tu [[GUARDA-001]]): el DINERO y sus hermanos.** Xe NO cobra, NO firma, NO envía-al-cliente por su cuenta. Todo eso lo **redacta y te lo pasa con dry-run**; el toque final (cobrar/firmar/enviar) lo das **vos, humano**. Todo lo demás (reversible, hacia-adentro) lo hace sola.

**Nivel de ejecución elegido por el humano (2026-07-24): `reversible`.** Xe autónoma en lo reversible; `money`+`outbound` → confirm humano por Telegram. Autonomía total sin confirmar = NO se prende hoy (§5, va al final).

---

## ✅ CERRADA — Fase 0: Canal read-only probado de punta a punta

- Transporte por **suscripción** (`claude -p`, sin API key); `agent.ts` re-soldado; smoke verde.
- Gate `governance.ts` en `read_only`: oracle 7/7 (read→allow, write/money/outbound→deny, kill/baja→deny, audit NDJSON).
- Bridge Telegram real: bot **@Agenciazenkaibot**, allowlist (chat_id `19950645`), **eco e2e verificado** — mensaje real → gate read/allow (auditado) → fast-path `status.ts` (lee registro vía connector `reporte`, 138ms) → respuesta entregada.
- Docker endurecido escrito (no-root, read-only, sin puertos, sin docker.sock).
- **Es el PISO, no el techo.** Prueba que el canal + gate + memoria funcionan.

---

## ▶️ GOAL ACTIVO — Fase A: "Cerebro con manos" (el gate por-cada-tool)

**El corazón del megagoal.** Hoy el freno es grueso (`--permission-mode plan` = Xe no escribe). Para que Xe **ejecute** con seguridad, cada tool-call de `claude -p` debe pasar por `governance.decide()` **antes** de correr — el principio no-negociable de [[DEC-012]] ("el gate vive en código, no en el prompt").

**Qué construir:** enganchar `governance.gate()` al mecanismo de permisos por-tool del CLI (`--permission-prompt-tool` vía un MCP mínimo, o un hook `PreToolUse` en `--settings`). El adaptador `classify(tool,input)→Action` (ya declarado en `agent.ts`) traduce cada tool a su `kind` (read/write_reversible/outbound/money).

**Condición de cierre (falsable):** un oracle e2e con `EXEC_MODE=reversible` donde Xe (claude -p, tools habilitadas) enfrenta 3 caminos y el gate actúa por-tool:
1. acción reversible (ej. escribir en el registro de prueba) → `ALLOW` → ejecuta → verificable en la DB;
2. acción de dinero/outbound → `NEEDS_CONFIRM` → **NO ejecuta** sin el 2º OK; queda el dry-run;
3. confianza baja / kill-switch → `DENY`.
Todo auditado en NDJSON. Check: correr el harness, ver los 3 caminos + el audit.

**🚧 Bloqueo técnico a resolver primero:** fijar el mecanismo exacto contra el CLI instalado (`--permission-prompt-tool` vs hook `PreToolUse`) — verificar, no asumir.

---

## ⏸ EN COLA (cada una con cierre falsable y VEREDICTO humano)

- **Fase B — Telegram de comando real.** El bridge resuelve `needs_confirm` mostrando el dry-run y esperando tu SÍ (el esqueleto `askConfirm` ya existe; se cablea al gate real). *Cierre:* desde Telegram, una orden reversible se ejecuta; una que toca dinero/envío te muestra el dry-run y espera tu SÍ; sin SÍ, no corre.
- **Fase C — Deploy operativo a la VPS (`EXEC_MODE=reversible`).** token + `.env` reversible + topes + build + contenedor 24/7. *Cierre:* contenedor Up; desde el celular una orden reversible se ejecuta y una de dinero pide confirm; Juana/ZENKAI intactos.
- **Fase D — Automatizar los packages (progresivo, "poco a poco").** Cada package invocable por Xe desde el chat, con su oracle, **uno por vez** con tu VEREDICTO: `registro` → `onboarding` → `reporte` → `multi-agente`. *Cierre por package:* Xe, comandada por chat, corre el package end-to-end (dry-run + execute reversible) sin que toques la terminal; lo irreversible/dinero sigue pidiendo tu OK.

---

## 🚧 Decisiones humanas que condicionan TODO

- **Token de suscripción (`claude setup-token`) — EL MOTOR, obligatorio.** Sin él Xe no piensa ni actúa. Gate de arranque de las Fases C+.
- **Topes de dinero/tokens/acciones ([[GUARDA-006]])** — hoy vacíos a propósito. Necesarios antes de que `money`/`outbound` puedan confirmarse. Los números los ponés vos, no se inventan.
- **Ratificar [[DEC-012]] + [[GUARDA-006]]** (hoy `propuesta`) — el VEREDICTO que habilita subir de `read_only`.
- **Orden de automatización de packages (Fase D)** — cuál primero (propuesta: registro).

---

## Reglas duras (de la constitución, innegociables)

- El gate vive en CÓDIGO, no en el prompt. Ningún system prompt lo salta.
- CERO API key: solo token de suscripción.
- Dinero/firma/envío-al-cliente = SIEMPRE humano ([[GUARDA-001]]). Xe redacta, vos ejecutás.
- No subir de fase sin VEREDICTO humano; autonomía sin-confirm va al final (§5), no ahora.
- No tocar producción de clientes (Juana/ZENKAI) sin OK; secretos por env 600; kill-switch siempre disponible ([[GUARDA-006]]).
