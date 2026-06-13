---
id: DEC-012
titulo: Canal de mando de Xe — Telegram → Claude Code headless (infra propia), dinero con doble gate humano
dueño: Jordy (Sad1mus) + HaxelGG
fuente: asesoría 2026-06-11 (sesión sobre operar Xe por chat); decisión humana vía AskUserQuestion
estado: propuesta (pendiente VEREDICTO humano)
lente: global
---
**Decisión:** Xe es operable por un **canal de mando humano** — v1 = **Telegram, restringido al `chat_id` del/los fundador(es)** — que dispara **Claude Code headless vía Claude Agent SDK en infra propia** ([[DEC-010]], no Managed Agents → soberanía y residencia). El canal tiene **autoridad sobre dinero bajo DOBLE GATE**: la mente puede *iniciar* un cobro/payout, pero **cada uno** exige (a) el `confirm` humano de [[GUARDA-001]] y (b) un segundo OK explícito entregado por el propio canal, dentro de los topes de [[GUARDA-006]].

**Porqué:** la operación es follow-the-sun 24/7 (§1) y el operador es humano; un canal de chat sube la **disponibilidad y autonomía operativa** (disparar a Xe desde el celular, a cualquier hora, en cualquier teatro) **sin ceder soberanía** — el cerebro y los datos quedan en infra propia. El canal NO mejora la inteligencia de Xe (eso son los músculos 🧪 del CLAUDE.md §3); es la puerta, no el IQ.

**Supuestos (de qué depende que sea válida):**
- El confirm-gate y los topes viven en **CÓDIGO** ([[GUARDA-006]]), no en el system prompt — imposibles de saltar por alucinación/inyección.
- El bot **solo obedece** al `chat_id` allowlist; el token del bot se trata como llave maestra (secreto crítico, rotable, fuera del repo por [[GUARDA-005]]).
- Rollout **por fases, sin saltos**: (1) solo lectura → (2) escritura reversible con confirm → (3) **dinero con doble gate + topes** (esta etapa) → (4) autonomía graduada (§5, Fase 6 del megagoal). Cada fase la cierra un VEREDICTO humano.
- El ruteo por teatro respeta residencia ([[GUARDA-002]]): un mensaje que toca dato regulado se ejecuta en su región, no en cualquier nodo.

**Qué la invalidaría:** que el canal **no pueda garantizar el gate en código** — p. ej. se demuestra (VEREDICTO) que un prompt-injection logra ejecutar dinero sin el doble confirm → **se apaga el canal** hasta resolver. También: que el costo/riesgo operacional del canal supere el valor de la disponibilidad que aporta.

**Relaciones:** deriva_de [[DEC-010]] (infra propia / local-first / no hardcodeo) · restringida_por [[GUARDA-001]] (dinero/firma/envío) · restringida_por [[GUARDA-006]] (topes + kill switch + confirm-en-código) · gobernada por [[GUARDA-002]] (residencia) y [[GUARDA-005]] (sin hardcodeo) · realiza la "autonomía graduada" (§5) y la cadencia de handoff escrito al substrato (§7). Implementación de referencia: `infra/canal-mando/`.
