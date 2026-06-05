# MEGAGOAL — Xe: portafolio GOLD activo y funcional

> **Cola, no monolito.** El NORTE es Gold; **un solo goal activo** a la vez; cada condición de cierre es **falsable y citada**; no se avanza sin **VEREDICTO humano**. A Gold se llega por **composición de módulos** al contrato — los tiers son acumulativos (Starter⊂Silver⊂**Gold**), ver [[DEC-008]]. Destilado del vault; lo no firmado va como 🚧 BLOQUEO, no se inventa ([[GUARDA-003]]).

---

## 🥇 NORTE — Gold ([[DEC-006]], $1,749/mo), en las 3 lentes, orquestado por Xe
Gold = **agentes ilimitados · multicanal (web+WhatsApp+social) · video IA · reporte semanal · soporte prioritario + optimización continua**. Plan estrella y de mayor margen.

**Gold = bundle de módulos** (estado del `inventario-portafolio.md`):

| Módulo | Estado | Para Gold |
|---|---|---|
| M1 Agente + WhatsApp + panel + booking | ✅ existe · **validado VEREDICTO-001** | base |
| M2 Web/storefront + diseño production-grade | ✅ existe (orvex/ecommerce) | base |
| M3 Multi-agente / ilimitado por cliente | ⚠️ parcial (clinics: 1 agente/cliente) | **gap** |
| M4 Multicanal unificado (web+social, un cerebro) | ❌ gap | **gap** |
| M5 Video IA (HeyGen/Higgsfield) | ❌ gap | **gap** |
| M6 Reporte semanal / analytics ROI | ⚠️ parcial (clinics) | **gap** |
| M7 Optimización continua (priority) | ⚠️ ops + criterio sin definir | **gap** |

---

## ✅ CERRADAS (no se re-abren)

- **Fase 1 — Fundación + criterio.** VEREDICTO humano 2026-06-04: DEC-002/004/005/006/007/008/009/010 aceptadas; GUARDA-001..005; identidad Xe; arquitectura monorepo-orquestador.
- **Fase 2→3 — Contrato validado en ejecución real.** [[VEREDICTO-001]]: el conector `integrations/clinics/` orquestó `nueva_clinica.ts` y creó una clínica en DB local de prueba (verificado REST+psql); guardas respetadas. **El contrato de capacidades es real** → habilita construcción paralela.

---

## ▶️ GOAL ACTIVO — Fase 4: construir los módulos-gap de Gold

**Objetivo:** convertir los gaps (M3, M4, M5, M6) en **módulos que cumplen el contrato** (`contrato-capacidades.md`: manifest·inputs·dry_run·execute·oracle), construibles **en paralelo** por Jordy y HaxelGG, **sin tocar/mover los productos** ni romper lo que factura.

**Submódulos (cada uno cierra solo):**
- **4a · Video IA (M5)** — el gap más visible y caro de Gold.
- **4b · Multicanal unificado (M4)** — web + social sobre el mismo cerebro del agente.
- **4c · Multi-agente / ilimitado (M3)** — de 1-agente-por-cliente a N.
- **4d · Reporte semanal + analytics ROI (M6)**.

**Condición de cierre de CADA submódulo (falsable):**
1. Existe `packages/<modulo>/` con `manifest` + `inputs` validados.
2. `dry_run()` corre y produce su salida **sin efectos irreversibles**.
3. `execute()` corre **solo con `--confirm`** ([[GUARDA-001]]) y **sin cuentas hardcodeadas** ([[GUARDA-005]]).
4. `oracle` **PASA** (registrado en `vault/40_Postmortems/`).
5. Cero cambios en los repos de producto (verificable por `git status` de cada producto).

**Fase 4 cierra cuando:** los 4 submódulos tienen su VEREDICTO `PASA`.

### 📍 Estado del portafolio (hallazgo 2026-06-04)
Gold está **~50% construido**: la base (M1 ✅ validado + M2 ✅) y M6/M7 a medias **ya están**; faltan los tres que **definen Gold y justifican su precio** — **M5 Video IA, M4 Multicanal, M3 Multi-agente**. Por nicho: **Starter = ~100%** para dental/med-spa/vet (verticales probados); **Gold = ~mitad**. → No vender Gold por ads hasta cerrar M5+M4 (la mitad premium que falta). Ver `nichos-us-candidatos.md`.

### ▶️ ARRANQUE MAÑANA (2026-06-05) — terminación del portafolio
Orden propuesto, de mayor a menor impacto en "Gold real":
1. **M5 Video IA** — el gap que más diferencia Gold. ⚠️ **bloqueado** hasta decidir proveedor+costo (ver abajo). Si no hay decisión, empezar por →
2. **M4 Multicanal unificado** o **M3 Multi-agente** — no dependen de proveedor externo; se pueden arrancar al contrato ya.
3. **M6 Reporte/analytics** — el más cercano a "listo" (clinics ya tiene base).

🔀 **Decisión que abre mañana (la mente NO la toma):** ¿**construir Gold completo antes de vender** (camino 2), o **vender Starter/Silver ya en paralelo** sobre los verticales probados mientras se construye Gold (camino 1)? Recomendación previa: camino 1 para caja+datos CAC:LTV, camino 2 en paralelo.

**🚧 Bloqueos humanos de Fase 4 (la mente NO los inventa):**
- **Proveedor de Video IA + costo** (M5) — afecta el suelo de costo ([[GUARDA-004]]). Sin esto, 4a se bloquea.
- **Gate de honestidad:** ¿"predicción / Jarvis / SuperBrain" existen como tecnología o eran marketing ZENKAI? Si no existen, se definen como módulo o **no se venden** (la mente no vende lo que no existe).
- **`zenkai-super-brain` (HaxelGG)** → ¿se funde en Xe? (hueco #24) — condiciona quién construye qué.

---

## ⏸ EN COLA (no empezar sin cerrar la anterior)

- **Fase 5 — Componer y vender Gold.** Bundle Gold completo (M1–M7) + **un onboarding Gold real** con OK humano.
  - **Condición de cierre (falsable):** la mente onboardea 1 cliente Gold real (discovery→cotización Gold→entrega multi-módulo), un humano aprueba el cobro sin corregir el número, replicable en las 3 lentes.
  - **🚧 Bloqueo:** extender el mapeo tier→plan a **Gold** (hoy [[DEC-009]] solo cubre Starter→basic; hueco #17); inventario oficial de "optimización continua" (hueco #23).

- **Fase 6 — Escala y autonomía supervisada.** Replicar Gold **por nicho** (los 10 US) y **por lente** (USA/EU/LATAM); autonomía graduada bajo guardas.
  - **Condición de cierre (falsable):** Gold corriendo en ≥2 nichos y ≥2 lentes, con residencia respetada ([[GUARDA-002]]).
  - **🚧 Bloqueo:** elegir los **10 nichos US** (candidatos con datos en `nichos-us-candidatos.md`, hueco #21); **consolidar cuentas** en la org compartida + plan Pro (el límite de 2 proyectos free de "Zenkai" ya lo exige — deuda de [[VEREDICTO-001]]).

---

## 🚧 Decisiones humanas que condicionan TODO el camino (resumen)
1. Proveedor + costo de Video IA (Fase 4a).
2. ¿predicción/Jarvis/SuperBrain reales o marketing? (gate Fase 4).
3. `zenkai-super-brain` → ¿funde en Xe? (hueco #24).
4. Mapeo tier→plan para Silver/Gold (hueco #17 — Fase 5).
5. Inventario oficial de "optimización continua" Gold (hueco #23 — Fase 5).
6. Los 10 nichos US definitivos (hueco #21 — Fase 6).
7. Consolidar cuentas/plan Pro en org compartida (deuda VEREDICTO-001 — Fase 6).

*Refinar con `/goal-queue`. Una fase = un VEREDICTO humano que la cierra. Gold se gana módulo a módulo, no de un salto.*
