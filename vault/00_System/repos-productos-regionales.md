# Repos de productos regionales — el registro que Xe orquesta

> **Para qué:** que Xe **sepa qué productos existen y dónde viven**, para orquestarlos a través de los 3 continentes. Por [[DEC-010]], Xe **integra los productos donde viven (su propio repo), NO los absorbe** en `xe-mind`. Este archivo es el índice de esos repos.

## Patrón (el que escala a los 3 continentes)

Cada producto regional cumple lo mismo:
1. **Repo propio privado** en GitHub (`Sad1mus/*`) — respaldo off-local (no solo disco/VPS/zip).
2. **Referenciado por Xe** vía puntero de env (estilo `CLINICS_REPO`), resuelto headless con **PAT de GitHub** (token de terceros, permitido; no es API key de Anthropic).
3. **Secretos jamás al repo** (`.env`/`auth/`/`data/*.db` gitignored). El `.env` real vive 600 en la VPS.
4. Xe **orquesta y despliega**, no mueve el código a su propio árbol ([[DEC-010]]).

## Registro

| Producto | Lente / Marca | Repo | Estado |
|---|---|---|---|
| **agente-wa (ZENKAI)** | EMEA / ZENKAI | `github.com/Sad1mus/zenkai-agente-wa` (privado) | ✅ **versionado 2026-07-27** — molde Baileys + **transporte Cloud API** (`whatsapp-cloud.ts`, tests 19/19+16/16) + `deploy/Caddyfile` |
| **agente-wa (Juana Sánchez)** | EMEA / España | — (solo disco: `grupojuana/agente-wa`) | 🟡 **sin versionar** — mismo molde; falta repo propio |
| **agente-clinicas** (motor del catálogo) | transversal | — (Supabase; repo por confirmar) | 🟡 **sin versionar / sin puntero** — `CLINICS_REPO` vacío → Xe hoy NO crea/entrega paquetes desde la VPS |
| **vocero-crm** (capa CRM, candidato) | transversal | fork pendiente (`kevinrivm/vocero-crm`, MIT) | 🟡 evaluado ([[VEREDICTO-008]]); adopción en `goal-queue-vocero-adopcion.md` |
| Américas / APAC | Américas · APAC | — | ❓ por definir (marca Américas sin firmar, [[DEC-007]]) |

## Pendiente para "Xe gobierna los 3 continentes"

1. **Repo-ificar** los productos que siguen solo en disco (Juana, agente-clinicas) — mismo patrón que ZENKAI.
2. **Setear los punteros de env** en la VPS (`CLINICS_REPO` y equivalentes) + el **PAT de GitHub** para que Xe pueda `clone/pull/deploy` headless.
3. Cablear el flujo: [[DEC-017]] (pago→construye) + `onboarding-meta` provisiona una instancia por cliente, tomando el producto desde su repo.

**Relaciones:** realiza [[DEC-010]] (integrar donde viven) · habilita Fase D (Xe crea/entrega desde la VPS) · consume [[VEREDICTO-008]] (vocero como capa CRM) · restringido por GUARDA de secretos (nada de `.env`/sesión/PII al repo).
