# MEGAGOAL — Xe: portafolio GOLD activo y funcional

> **Cola, no monolito.** El NORTE es Gold; **un solo goal activo** a la vez; cada condición de cierre es **falsable y citada**; no se avanza sin **VEREDICTO humano**. A Gold se llega por **composición de módulos** al contrato — los tiers son acumulativos (Starter⊂Silver⊂**Gold**), ver [[DEC-008]]. Destilado del vault; lo no firmado va como 🚧 BLOQUEO, no se inventa ([[GUARDA-003]]).
>
> **Regla de honestidad:** `oracle PASA` ≠ submódulo cerrado. Solo un **VEREDICTO humano** cierra (CLAUDE.md §0/§8). Última regeneración: 2026-06-13.

---

## 🥇 NORTE — Gold ([[DEC-006]], $1,749/mo), en las 3 lentes, orquestado por Xe
Gold = **agentes ilimitados · multicanal (web+WhatsApp+social) · video IA · reporte semanal · soporte prioritario + optimización continua**. Plan estrella y de mayor margen.

**Gold = bundle de módulos** (estado leído de `inventario-portafolio.md` + `packages/` + `integrations/`):

| Módulo | Estado | Para Gold |
|---|---|---|
| M1 Agente + WhatsApp + panel + booking | ✅ existe · **validado [[VEREDICTO-001]]** (`integrations/clinics/`) | base |
| M2 Web/storefront + diseño production-grade | ✅ existe (orvex/ecommerce) | base |
| M3 Multi-agente / ilimitado por cliente | ✅ **construido, oracle PASA** ([[VEREDICTO-002]], `packages/multi-agente/`) · ⏳ pendiente ratificación + e2e | era gap → 4c |
| M4 Multicanal unificado (web+social, un cerebro) | ❌ gap | **gap** → 4b |
| M5 Video IA (HeyGen/Higgsfield) | ❌ gap · 🚧 bloqueado (proveedor+costo) | **gap** → 4a |
| M6 Reporte semanal / analytics ROI | ⚠️ parcial (clinics) | **gap** → 4d |
| M7 Optimización continua (priority) | ⚠️ ops + criterio sin definir (hueco #23) | **gap** |

---

## ✅ CERRADAS (no se re-abren)

- **Fase 1 — Fundación + criterio.** VEREDICTO humano 2026-06-04: DEC-002/004/005/006/007/008/009/010 aceptadas; GUARDA-001..005; identidad Xe; arquitectura monorepo-orquestador.
- **Fase 2→3 — Contrato validado en ejecución real.** [[VEREDICTO-001]]: el conector `integrations/clinics/` orquestó `nueva_clinica.ts` y creó la clínica "Sunrise Vet Clinic" en DB Supabase local de prueba (verificado REST+psql); guardas respetadas. **El contrato de capacidades es real** → habilita construcción paralela.

---

## ▶️ GOAL ACTIVO — Fase 4: construir los módulos-gap de Gold

**Objetivo:** convertir los gaps (M3, M4, M5, M6) en **módulos que cumplen el contrato** (`contrato-capacidades.md`: manifest·inputs·dry_run·execute·oracle), construibles **en paralelo** por Jordy y HaxelGG, **sin tocar/mover los productos** ni romper lo que factura.

**Estado real por submódulo (2026-06-13):**

| Submódulo | Módulo | Estado |
|---|---|---|
| **4a · Video IA** | M5 | 🚧 **BLOQUEADO** — proveedor + costo es decisión humana (afecta [[GUARDA-004]] suelo de costo). No se arranca hasta firmar la DEC. |
| **4b · Multicanal unificado** | M4 | ⬜ **pendiente** — web + social sobre el mismo cerebro. Depende de qué canales sociales (Meta/n8n son "aspiracionales" CLAUDE.md §9.4: validar antes de cablear). |
| **4c · Multi-agente / ilimitado** | M3 | ✅ **construido, ORACLE PASA** ([[VEREDICTO-002]], `packages/multi-agente/`, compone `integrations/clinics`) · ⏳ **pendiente ratificación humana + ejecución real e2e** (N agentes contra DB de prueba, al rigor de [[VEREDICTO-001]]). |
| **4d · Reporte + analytics ROI** | M6 | ⬜ **pendiente** — clinics tiene reporte básico; "optimización continua" sin definir (hueco #23). |

**Condición de cierre de CADA submódulo (falsable):**
1. Existe `packages/<modulo>/` con `manifest` + `inputs` validados.
2. `dry_run()` corre y produce su salida **sin efectos irreversibles**.
3. `execute()` corre **solo con `--confirm`** ([[GUARDA-001]]) y **sin cuentas hardcodeadas** ([[GUARDA-005]]).
4. `oracle` **PASA** (registrado en `vault/40_Postmortems/`).
5. Cero cambios en los repos de producto (verificable por `git status` de cada producto).
6. **VEREDICTO humano** que ratifica el submódulo. *(El oracle es evidencia; el cierre lo da el humano.)*

**Fase 4 cierra cuando:** los 4 submódulos tienen su VEREDICTO humano `PASA`.

### 📍 Próximo paso ejecutable (no bloqueado)
1. **Cerrar 4c** — ejecución real e2e de `packages/multi-agente/` (crear N agentes contra una DB de prueba, como hizo VEREDICTO-001 con 1) + ratificación humana. Es lo más cerca de cerrar.
2. **Arrancar 4b (Multicanal) o 4d (Reporte)** — ninguno depende de proveedor externo; 4a sigue bloqueado.
3. **NO arrancar 4a** hasta que se firme proveedor+costo de Video IA.

---

## 🧱 BACKBONE — registro de clientes y proyectos (transversal)

La capa "verdad exacta" (CLAUDE.md §3.1) con la que Xe **administra** cada cliente/proyecto en las 3 lentes, con residencia (GUARDA-002). **Construida 2026-06-13** ([[VEREDICTO-004]], `packages/registro/`): oracle PASA + e2e local (cliente+proyecto creados, verificado por SELECT). ⏳ pendiente VEREDICTO humano + ratificar esquema ([[DEC-013]], propuesta). **Es precondición de Fase 5 y Fase 6** — no se gestiona Gold en 3 continentes sin esto.

## ⏸ EN COLA (no empezar sin cerrar la anterior)

- **Fase 5 — Componer y vender Gold.** Bundle Gold completo (M1–M7) + **un onboarding Gold real** con OK humano. **Depende del backbone `registro`** (alta de cliente/proyecto, residencia).
  - **Condición de cierre (falsable):** la mente onboardea 1 cliente Gold real (discovery→cotización Gold→entrega multi-módulo), un humano aprueba el cobro sin corregir el número, replicable en las 3 lentes.
  - **🚧 Bloqueo:** extender el mapeo tier→plan a **Gold** (hoy [[DEC-009]] solo cubre Starter→basic; hueco #17 parcial); inventario oficial de "optimización continua" (hueco #23).

- **Fase 6 — Escala y autonomía supervisada.** Replicar Gold **por nicho** (los 10 US) y **por lente** (USA/EU/LATAM); autonomía graduada bajo guardas.
  - **Condición de cierre (falsable):** Gold corriendo en ≥2 nichos y ≥2 lentes, con residencia respetada ([[GUARDA-002]]).
  - **🚧 Bloqueo:** elegir los **10 nichos US** (candidatos con datos en `nichos-us-candidatos.md`, hueco #21); **consolidar cuentas** en la org compartida + plan Pro (deuda de [[VEREDICTO-001]]: el límite de 2 proyectos free de "Zenkai" ya lo exige).

---

## 🚧 Decisiones humanas que condicionan TODO el camino (resumen)
1. **Proveedor + costo de Video IA** (Fase 4a) — sin esto, 4a se bloquea ([[GUARDA-004]]).
2. **¿predicción/Jarvis/SuperBrain reales o marketing?** (gate Fase 4) — la mente no vende lo que no existe.
3. **`zenkai-super-brain` → funde en Xe** (hueco #24): dirección dada (Jordy: "todo en Xe"); ⏳ pendiente que HaxelGG confirme y migre su repo.
4. **Mapeo tier→plan para Silver/Gold** (hueco #17, parcial — Fase 5): los planes de entrega son 3 y los tiers 5, no es 1:1.
5. **Inventario oficial de "optimización continua" Gold** (hueco #23 — Fase 5).
6. **Los 10 nichos US definitivos** (hueco #21 — Fase 6): candidatos investigados, falta que el humano elija.
7. **Consolidar cuentas/plan Pro** en org compartida (deuda VEREDICTO-001 — Fase 6).

*Refinar con `/goal` (skill goal-queue). Una fase = un VEREDICTO humano que la cierra. Gold se gana módulo a módulo, no de un salto. El plan es autoría: la mente NO se auto-aprueba el contenido — el VEREDICTO del plan lo da el humano.*
