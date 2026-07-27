# Handoff — sesión 2026-07-26 (para retomar tras reiniciar la máquina)

## Lo que se hizo hoy (todo commiteado y pusheado a GitHub privado `Sad1mus/xe-mind`)
1. **Armonización de infra (P1–P5, 6/6 verificado contra la VPS)** — cola `.claude/goal-queue-armonizar.md`:
   - **P1** cap de memoria de `agente-juanasanchez` a 2 GiB (en vivo con `docker update`, sin reiniciar; persistido en su compose).
   - **P3** backup diario de `/data` (`backup-data.sh` + cron 03:15, rotación 14d, `integrity_check=ok`).
   - **P4** alerta de salud (`watch-health.sh` + cron cada 5min → Telegram al chat 19950645; **probada real, `ok:true`, llegó al celular**).
   - **P5** `classify.ts` ampliado (`ToolSearch`→read, MCP-pago→money; `unknown→baja` intacto; oráculo 15/15).
   - **P2** `.gitignore` endurecido + `RUNBOOK-armonizacion.md`.
2. **DEC-016** — Telegram = canal operativo de Xe; `/remote-control` = cockpit de dev, NO operación. (aceptada)
3. **DEC-017** — arquitectura de fulfillment por pago (regional, construcción automática, **entrega con visto humano**). (**propuesta** — ver huecos abajo)
4. **GitHub como respaldo:** integrados 6 commits remotos que este PC no tenía (M4 multicanal, Linear DEC-015, refactor identidad, RLS). Local ↔ GitHub sincronizados.

## Verdad incómoda confirmada hoy (para no auto-engañarnos)
- **Desde la VPS, Xe hoy NO puede crear/entregar un paquete.** El producto `agente-clinicas` NO está en la VPS; `/repo/packages` solo tiene `registro` + `reporte`; `CLINICS_REPO` vacío. Xe hoy solo **reporta estado** y **registra** (SQLite admin), gateado.
- Automatización real hoy = **los bots de cliente corriendo solos** (Juana, ZENKAI). El ciclo conseguir→entregar→cobrar sigue siendo mayormente manual.
- Techo de automatización ≈ 60% **por diseño** (dinero 0% para siempre — GUARDA-001; alto-toque Gold+ humano — DEC-014).

## Huecos abiertos (decisión/trabajo humano — NO inventar)
- **HUECO PRICING:** plazo de compromiso choca — ZENKAI v5 tiene calendario 3/6/12 meses (Trimestral −15%+fee−90%, Semestral −25%, Anual −27%); oficial etherlabx solo mensual/anual (~15%). DEC-006 supersede v5. **Definir:** ¿revivir el calendario o quedarse con mensual/anual? Bloquea la cotización del flujo.
- **DEC-017 colisiones a resolver antes de construir:** (1) webhook = endpoint inbound (choca con hardening cero-inbound → receptor separado y endurecido, firma+idempotencia); (2) residencia GUARDA-002 (no centralizar 3 continentes en 1 VPS → plano de datos regional + orquestación central).

## Próximos pasos (orden sugerido)
1. **Fase D — cablear la entrega a la VPS + al gate** (lo que más sube el % automatizado): desplegar `agente-clinicas` + packages de entrega a la VPS, setear `CLINICS_REPO`, y que Xe corra `onboarding` (dry-run+execute reversible) desde Telegram para Starter/Silver.
2. **Zanjar el hueco de pricing** (revivir calendario 3/6/12 o no) — necesario para cotizar.
3. **Diseñar el receptor de webhooks** de DEC-017 (regional, firmado, idempotente) — cuando el pricing esté claro.
4. Pendientes menores: **P6** (token de suscripción como punto único de falla — runbook de rotación + estado "Xe degradada"); reviºvir el MCP **RunPod-Comfy** (endpoint 404).

## Decisiones de cost/quality ya conversadas (para no re-litigar)
- Chat de bots = **API por token** (nunca GPU 24/7). Sacar los bots de OpenRouter `:free` → modelo pago chico confiable.
- Media/video = **RunPod serverless** (lo que Xe puede operar headless) para lote; **Higgsfield** = carril premium manual (es OAuth, NO headless → herramienta tuya, no de Xe).
- MCPs headless-compatibles para la VPS: Cloudflare (DNS/dashboards), GitHub (PAT), Supabase (service key). "Cero API key" era sobre la API de Anthropic, NO sobre tokens de terceros.

## Regla de trabajo activa
- Autorización durable de la sesión para commit+push de código/conocimiento. Frenos duros que NO se relajan: dinero/firma jamás; secretos jamás a git; nada destructivo ni sobre Juana/ZENKAI sin avisar.
