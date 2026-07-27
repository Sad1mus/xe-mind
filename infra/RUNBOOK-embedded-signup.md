# RUNBOOK — Embedded Signup → Cloud API → provisioning (bot EtherLabX)

Camino de **mínima fricción** para conectar el WhatsApp de un cliente nuevo: el cliente aprieta un botón, autoriza en el popup de Meta (~2 min, sin tokens ni IDs), y Xe construye el resto **sola** hasta dejarlo en revisión para tu **visto humano**. Implementa el mecanismo de provisioning de [[DEC-017]].

> Construido por `goal-queue-embedded-signup.md` (Fases 1–5). El flujo **en vivo** depende de la **Fase 0** (gate humano): `vault/00_System/onboarding-meta-tech-provider.md`.

---

## Flujo punta a punta

```
 CLIENTE                         META                    XE (VPS)                     HUMANO (vos)
   │ 1. clic "Conectar WhatsApp"                            │                            │
   │───────────────────────────▶ popup Embedded Signup      │                            │
   │ 2. login FB + SMS + Permitir │                          │                            │
   │◀───────────────────────────┤ entrega `code`            │                            │
   │ 3. redirect con `code` ─────────────────────▶ /es-callback (receptor)               │
   │                              │                 4. dry-run provisioning (FakeGraph→Real)
   │                              │                 5. encola ítem "pendiente-visto-humano"
   │                              │                          │──── aviso Telegram ───────▶│
   │                              │                          │        6. revisás alineación
   │                              │                          │◀──── "dale" (OK envío) ────┤
   │                              │                 7. go-live (abrir al público)          │
   │◀─────────────────── el asistente ya atiende ───────────┤                            │
```

**Reparto (no negociable — DEC-017 Dec.4 / GUARDA-001):**
- **Automático (Xe):** recibir `code` · exchange→token · leer WABA/Phone IDs · subscribe · register · webhook · alta en `registro` (estado `onboarding`) · dejar el ítem en revisión.
- **Humano (vos):** revisar alineación + **OK de go-live**. El gate frena `go-live`/`enviar-al-cliente` (outbound→deny) hasta tu visto.

---

## Quién hace qué

| Paso | Vos (Meta/DNS/OK) | Xe (VPS/código) |
|---|---|---|
| Fase 0: Tech Provider + App Review + `config_id` | ✅ (gate, tarda por Meta) | — |
| Botón Embedded Signup en la web de la lente | ✅ (front) | — |
| DNS `wa.<region>` + `ufw` + Caddy | ✅ deploy | ✅ config (`deploy/Caddyfile`) |
| Recibir `code` → provisioning dry-run → encolar | — | ✅ `onboarding-meta` + `callback.py` |
| Revisar y dar OK de go-live | ✅ visto humano | — |
| Abrir al público tras el OK | — | ✅ (gateado) |

---

## Orden de dependencias

1. **Fase 0** (Tech Provider) — desbloquea TODO lo vivo. Sin esto, `RealGraph` lanza `PENDIENTE-META-APP` y solo corre el dry-run con `FakeGraph`.
2. **Transporte Cloud API** en el bot (`whatsapp-cloud.ts`, flag `WA_TRANSPORT=cloud`) — ya construido y testeado (19/19 + 16/16).
3. **Provisioning** (`packages/onboarding-meta`, `callback.py`) — ya construido (oracle PASA, selftest PASA).
4. **Superficie inbound** (`deploy/Caddyfile`, solo `/webhook` + `/es-callback`) — config lista, **deploy pendiente** (gate humano).
5. **Gate** (`classify.ts`: provisioning=reversible, go-live=visto humano) — ya cableado (oráculo 19/19).

---

## Componentes construidos (mapa de archivos)

| Pieza | Archivo | Estado |
|---|---|---|
| Transporte Cloud API | `xenkaisystems/agente-wa/src/whatsapp-cloud.ts` (+ tests) | ✅ 35/35 checks |
| Flag de transporte | `…/src/config.ts` (`WA_TRANSPORT`), `…/src/index.ts` | ✅ Baileys intacto |
| Provisioning | `xe-mind/packages/onboarding-meta/connector.py` | ✅ ORACLE PASA |
| Cliente Graph (fake/real) | `…/onboarding-meta/graph_client.py` | ✅ real = hueco |
| Receptor callback | `…/onboarding-meta/callback.py` | ✅ SELFTEST PASA |
| Superficie inbound | `xenkaisystems/agente-wa/deploy/Caddyfile` | 🟡 config, sin aplicar |
| Gate | `xe-mind/infra/canal-mando/classify.ts` | ✅ oráculo 19/19 |
| Gate humano Meta | `xe-mind/vault/00_System/onboarding-meta-tech-provider.md` | 🔴 acción humana |

---

## Bloqueos abiertos (no inventar — GUARDA-003)

- **Fase 0 (Tech Provider):** acción humana en Meta; entregar los 5 datos (App ID/Secret, `config_id`, Graph version, dominio callback).
- **Pricing:** el plazo de compromiso choca entre fuentes (ZENKAI v5 3/6/12 meses vs oficial etherlabx mensual/anual) — **decisión humana pendiente**; el discovery no puede cotizar hasta zanjarlo. Ver [[DEC-017]].
- **Residencia (GUARDA-002):** una sola VPS no centraliza los 3 continentes; plano de datos regional + orquestación central (diseño de despliegue, aparte).
- **DEC-017** sigue en estado `propuesta` (VEREDICTO humano pendiente).
