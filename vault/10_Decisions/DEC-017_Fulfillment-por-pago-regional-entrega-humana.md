---
id: DEC-017
titulo: Arquitectura de fulfillment por pago — regional, construcción automática, entrega con visto humano
dueño: Jordy (Sad1mus)
fuente: asesoría 2026-07-26 (visión de fulfillment por webhooks de pago + revisión humana en dashboard/Drive)
estado: propuesta (el FLUJO lo decidió el humano; ratificación pendiente de resolver 2 colisiones de guarda + el hueco de pricing)
lente: global (ejecución regional)
---
**Decisión (el flujo):** Cada continente (Américas / EMEA / APAC) tiene su web con su **pasarela de pago local**. Un pago exitoso (webhook `200 OK` del procesador) dispara a Xe a **CONSTRUIR** automáticamente el paquete asignado a ese continente (provisión del agente + DB + dashboard) y a **destilar la data del cliente** vía el **agente de WhatsApp regional** (discovery por formulario / preguntas concretas, [[DEC-004]]). El resultado aterriza en **una superficie de revisión** — **dashboard para la DECISIÓN** (data destilada vs lo que promete el tier + región) + **Google Drive para los ARTEFACTOS** (boceto/PDF/assets) — donde el humano verifica alineación con el cliente y **da el OK explícito para enviar**.

**El reparto construcción / entrega (el corazón, no negociable):**
- **Automático (Xe sola):** recibir el evento de pago · construir/provisionar el paquete · correr el discovery · dejar todo en la superficie de revisión.
- **Humano (visto obligatorio):** revisar la alineación + **OK de envío al cliente**.
- El pago **dispara construcción, NUNCA entrega** (CLAUDE.md §9.6 Decisión 4). Entre "el cliente pagó" y "el cliente recibe" queda el visto humano.
- El `200 OK` **NO es Xe ejecutando dinero**: el procesador ya cobró; Xe reacciona a un evento cerrado → compatible con [[GUARDA-001]].

**Porqué:** sube la disponibilidad operativa 24/7 (follow-the-sun, §1) sin ceder el control del dinero ni de la marca: la parte repetitiva (construir) se automatiza; la parte de criterio y riesgo (entregar con nuestra marca y con el dinero ya cobrado) se queda en el humano.

**Colisiones a resolver ANTES de construir (esto NO está resuelto):**
1. **Superficie inbound.** Recibir webhooks exige un **endpoint HTTPS entrante**, que contradice el hardening actual de Xe (cero inbound; Telegram long-poll saliente). Requiere un **receptor de webhooks separado y endurecido** (verificación de firma del procesador + idempotencia por `event_id` + rate-limit), **fuera** del contenedor de Xe. Patrón ya probado en `orvex/smc-platform` (Stripe firmado + idempotencia por `stripe_event_id`).
2. **Residencia ([[GUARDA-002]]).** Una **sola** VPS NO puede centralizar datos de pago+cliente de los 3 continentes. Diseño correcto: **plano de datos regional + orquestación central** — la VPS orquesta, el dato regulado se queda en su región ([[DEC-010]]).

**Hueco de pricing (no inventar, [[GUARDA-003]]):** el **plazo de compromiso** y su descuento **chocan entre fuentes**:
- **ZENKAI v5** (`ventas/world/zenkai-pricing-v5-fee-descuentos.html`): calendario 3/6/12 meses, igual en los 3 continentes — Trimestral −15% (+fee −90%) · Semestral −25% (sin fee) · Anual −27% (sin fee).
- **Página oficial etherlabx** ([[DEC-006]]): solo mensual ↔ **anual (~15%)**; sin escalón trimestral/semestral.
- [[DEC-006]] supersede ZENKAI v5 → oficialmente el calendario está muerto, pero la oferta oficial quedó más flaca. **Decisión humana pendiente:** revivir el calendario de compromiso en el pricing oficial, o quedarse con mensual/anual. **El flujo no se puede cotizar hasta zanjar esto** (el discovery debe capturar el plazo, que cambia precio y fee).

**Qué la invalidaría:** que la entrega se vuelva automática (rompe §9.6 Dec.4 y [[GUARDA-001]]) · que no se pueda garantizar el webhook seguro (firma + idempotencia) · que la residencia obligue a un modelo que la orquestación central no pueda sostener.

**Relaciones:** concreta CLAUDE.md §9.6 Decisión 4 · deriva_de [[DEC-012]] (canal de mando de Xe) · restringida_por [[GUARDA-001]] (dinero/firma/envío) · restringida_por [[GUARDA-002]] (residencia) · restringida_por [[GUARDA-006]] (topes + kill-switch) · apoyada en [[DEC-010]] (datos por región) · discovery por [[DEC-004]] · pricing bloqueado por el choque [[DEC-006]] ↔ ZENKAI v5. Implementación de referencia del webhook: `orvex/smc-platform` (`app/api/webhooks/stripe/route.ts`).
