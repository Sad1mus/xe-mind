---
id: DEC-016
titulo: Telegram es el canal por el que Xe OPERA; /remote-control queda como cockpit de dev del humano, no como operación
dueño: Jordy (Sad1mus)
fuente: asesoría 2026-07-26 (fork "operar la agencia por Telegram vs dejar un remote-control de Claude desde el móvil")
estado: aceptada (VEREDICTO humano 2026-07-26)
lente: global
---
**Decisión:** Xe **opera** la agencia por el **canal de mando de Telegram** ([[DEC-012]], allowlist al `chat_id` del fundador, gate en código). El **`/remote-control` (`/rc`) de Claude Code NO se usa para operar la agencia**: queda reservado —si acaso— como **cockpit de desarrollo interactivo del humano** sobre el VPS (Jordy programando a mano desde el celular), nunca como sustrato por el que Xe ejecuta. Se separan dos cosas que la pregunta confundía: **"Xe opera"** (Telegram, gateado, autónomo, auditado) vs **"yo programo"** (`/rc`, interactivo, sin gobierno de Xe).

**Porqué:** el valor operativo de Xe vive en el **gate en código** (`governance.gate` por hook `PreToolUse`) + **auditoría** (`audit.ndjson`) + **autonomía async 24/7** + **cero superficie inbound** (long-poll saliente). `/rc` **no tiene nada de eso**: es un teclado remoto a una terminal Claude Code, así que la seguridad revierte a los prompts de permiso del propio Claude Code (que en el móvil se aprueban a ciegas o se corren en `auto`/`bypass`), es **beta/preview** de Anthropic, y **abre una URL web que maneja la terminal del VPS** (superficie que hoy no existe). Mover la operación a `/rc` = **tirar el gate en código** = recaer en el anti-patrón "`sudo NOPASSWD` + `/rc` beta" que Xe ya había superado por diseño.

**Supuestos (de qué depende que sea válida):**
- El gate/topes/kill-switch siguen en **código** ([[GUARDA-006]]), no en el prompt — es lo que Telegram respeta y `/rc` no.
- La frontera se mantiene: si se usa `/rc`, es **el humano operando conscientemente**, jamás Xe ejecutando por `/rc` sin pasar por `governance.gate`.
- La fricción de Telegram (interfaz estrecha, comandos cortos) se resuelve **mejorando su UX** (respuestas ricas, botones), NO abandonando el gate.

**Qué la invalidaría:** que Anthropic dote a `/rc` de un **gate en código equivalente y auditable** (hooks server-side + registro de decisiones) que iguale la garantía de Telegram → se reevalúa · o que Telegram deje de poder sostener el gate/auditoría/allowlist (p. ej. cambio de API que rompa el modelo) → habría que buscar otro sustrato con las mismas garantías, no bajar la vara.

**Guardas:** restringida_por [[GUARDA-006]] (topes + kill-switch + confirm-en-código: `/rc` no puede cumplirla) · restringida_por [[GUARDA-001]] (dinero/firma/envío: sólo se redactan, nunca se ejecutan autónomamente).

**Relaciones:** refina/consolida [[DEC-012]] (que fijó Telegram como v1 del canal; esta descarta explícitamente `/rc` como sustituto de la operación) · se apoya en [[DEC-010]] (infra propia / soberanía: `/rc` beta y su URL contradicen ese principio) · implementación de referencia: `infra/canal-mando/`.
