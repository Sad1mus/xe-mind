---
id: VEREDICTO-007
titulo: Submódulo 4b · Multicanal (M4) — capa construida, ratificada con deuda de e2e
fecha: 2026-07-16
estado: PASA (ratificado por Jordy, asumiendo la deuda de abajo)
---

> **Ratificación humana:** Jordy, 2026-07-16. Cierra el submódulo 4b **asumiendo explícitamente**
> que el e2e real no se corrió (ver *Deuda*). El oracle es evidencia; el cierre lo dio el humano (§10.4).

## Hipótesis probada
La capacidad **M4 (N canales sobre UN cerebro)** se puede construir **componiendo** el conector
`integrations/clinics` ya validado ([[VEREDICTO-001]]) — sin reimplementar `agente-clinicas`,
sin inventar un canal y **bloqueando** los que no tienen credencial, en vez de fingirlos.

Es la simetría de [[VEREDICTO-002]]: **M3 compone N agentes por cliente; M4 compone N canales por agente.**

## Decisiones humanas que la habilitaron (2026-07-16, CLAUDE.md §9.6)
4b estaba bloqueado desde el 2026-06-13 por un **hueco de criterio**, no por dificultad técnica:
*"depende de qué canales sociales (Meta/n8n son aspiracionales, §9.4: validar antes de cablear)"*.
Jordy lo resolvió:
- **Canales:** `web · whatsapp[baileys|cloud_api] · instagram_dm · messenger`. Instagram DM y Messenger son **Meta Graph API**, la misma familia que WhatsApp Cloud API → **una aprobación cubre los tres**. TikTok fuera (otra API, otro trámite).
- **WhatsApp en convivencia:** clientes actuales → `baileys`; clientes nuevos → `cloud_api`.

## Evidencia (corrida 2026-07-16, verificada en sesión)
- `python3 packages/multicanal/connector.py oracle` → **PASA**. 8 casos de validación: juego válido ✓, canales vacío bloquea ✓, falta cliente bloquea ✓, **atomicidad** (canal inexistente bloquea el juego) ✓, whatsapp sin transporte bloquea ✓, transporte inválido bloquea ✓, **canal repetido** bloquea ✓, agente inválido contamina el juego ✓. Más: compone 3 canales sobre **1 solo cerebro** ✓; env por canal correcto (`web` libre · `baileys`→`CLINICS_REPO` · `cloud_api`/`instagram_dm`/`messenger`→`META_ACCESS_TOKEN`) ✓.
- `dry_run` **juego Gold** (demo, 4 canales, US) → **1/4 canales listos**. `web` listo; `whatsapp/cloud_api`, `instagram_dm` y `messenger` **BLOQUEADOS** nombrando el env que falta. No simula la aprobación de Meta.
- `dry_run` **juego convivencia** (`web` + `whatsapp/baileys`, `CLINICS_REPO` puesto) → **2/2 canales listos**. Cotizó LATAM como `CONFIRMAR (no publicado; FX en propuesta)` — [[GUARDA-003]] operando sola: no inventó el precio que [[DEC-006]] no publica.
- `execute` sin `--confirm` ni env → **NO ejecuta** ([[GUARDA-001]]), lista el env faltante por canal e imprime el comando del cerebro para correrlo a mano.
- Oracles de los 6 módulos del repo tras el cambio → **todos PASA** (no se rompió nada).

## Condición de cierre del submódulo (falsable) — verificación
1. `packages/multicanal/` con `manifest` + `inputs` validados → ✅
2. `dry_run()` corre sin efectos irreversibles → ✅
3. `execute()` solo con `--confirm` ([[GUARDA-001]]) y sin cuentas hardcodeadas ([[GUARDA-005]]) → ✅
4. `oracle` **PASA**, registrado aquí → ✅
5. Cero cambios en repos de producto → ✅ (`git status` de `nexus`, `ecommerce-ciclismo`, `smc-platform` = 0)
6. **VEREDICTO humano** → ✅ Jordy, 2026-07-16

## Reglas duras propias añadidas
- **Juego atómico** ([[GUARDA-003]]): un canal inválido bloquea el juego entero — no hay atado parcial.
- **Un canal por tipo**: dos bindings del mismo canal → BLOQUEO (un cerebro atiende un canal de cada).
- **Credencial ausente NO se finge**: el canal se marca `BLOQUEADO` nombrando su env. La licencia Meta está EN TRÁMITE y M4 **no simula su aprobación**.

## Alcance real de M4 — leer antes de venderlo
M4 es la **capa de composición, validación y bloqueo** del multicanal: decide qué canales son válidos, los ata a un único cerebro y bloquea los que no tienen credencial. **NO implementa la llamada al API de cada canal** (`PENDIENTE-M4-wiring`): eso se cablea cuando exista la credencial de cada uno, porque no se escribe contra un API que no se ha probado ([[GUARDA-003]]). Es exactamente el mismo alcance que [[VEREDICTO-002]] tiene para M3.

## Bloqueos conocidos (no se inventan)
- **`PENDIENTE-M4-meta`** — `cloud_api`, `instagram_dm` y `messenger` **no ejecutan hasta que Meta apruebe la licencia**. Verificado: 1/4 canales listos en un juego Gold. **Consecuencia comercial: Gold no es entregable aunque M4 esté construido, y eso no lo desbloquea escribir más código.** La ruta crítica de Gold es el expediente en Meta.
- **`PENDIENTE-M4-migracion`** — sin fecha para migrar al último cliente de `baileys` → `cloud_api`, la convivencia es permanente por omisión, y con ella la **GPL-3.0 de `libsignal`** en el árbol y el riesgo de baneo del número del cliente.
- **hueco #17** — precio del bundle Gold multicanal (no del canal suelto). Decisión humana pendiente.

## Deuda (lo que este VEREDICTO NO prueba)
**No se corrió ejecución real end-to-end.** No se creó ningún cerebro ni se ató ningún canal contra una
DB de prueba, así que **no iguala el rigor de [[VEREDICTO-001]]** (que verificó por REST + `psql`).
Motivo: `supabase` CLI y `psql` no están instalados en la máquina, y el e2e completo de M4 es además
**imposible hoy** para 3 de sus 4 canales hasta que Meta apruebe. El e2e posible hoy es el **juego de
convivencia** (`web` + `whatsapp/baileys`), y queda pendiente.

**Confianza: media-alta.** Alta en la lógica de la capa (oracle + dry_run en dos escenarios + execute
bloqueando). Media en el conjunto, porque la ejecución real no se ha visto correr ni una vez.

## Veredicto
La lógica de la capa **PASA** el oráculo y respeta todas las guardas. Jordy **ratifica el submódulo 4b**
el 2026-07-16 asumiendo la deuda de e2e con los ojos abiertos. **Fase 4 no cierra**: falta el VEREDICTO
de 4a (bloqueado por proveedor de video) y el de 4d.

**Relaciones:** realiza submódulo 4b de `.claude/megagoal.md` · compone [[VEREDICTO-001]] · simétrico a [[VEREDICTO-002]] · gobernado por [[GUARDA-001]], [[GUARDA-003]], [[GUARDA-005]] · habilitado por contrato de `contrato-capacidades` · desbloquea la vía de Gold de [[DEC-014]] (parcialmente: falta Meta + M5).
