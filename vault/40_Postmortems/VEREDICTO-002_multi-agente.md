# VEREDICTO-002 — Submódulo 4c · Multi-agente (M3)

> **Estado: PASA — ratificado por Jordy el 2026-07-16**, asumiendo la deuda de e2e (ver *Veredicto*).
> Fecha de construcción: 2026-06-13 · Construido por Xe (Fase 4, goal activo) · Repo: `packages/multi-agente/`
>
> **Por qué importa esta ratificación:** [[DEC-014]] mapea **Silver ($699) = `basic`×3 vía M3**. Al cerrar 4c,
> Silver deja de estar bloqueado por producto y pasa a depender solo del RLS de `agente-clinicas`
> (0 policies hoy — ver megagoal, paso 3). Era la acción más barata del tablero: una firma, no una construcción.

## Hipótesis probada
La capacidad **M3 (N agentes por cliente)** se puede construir **componiendo** el conector
`integrations/clinics` ya validado ([[VEREDICTO-001]]) — sin reimplementar `agente-clinicas`,
sin proveedor externo y sin rellenar ningún hueco de criterio humano.

## Por qué se eligió 4c y no 4a/4b/4d (protocolo §4)
- **4a Video IA (M5):** 🚧 bloqueado — proveedor + costo es decisión humana ([[GUARDA-004]]). Confianza = CONFLICTO. No se tocó.
- **4b Multicanal (M4):** depende de canales sociales marcados "aspiracionales" (§9.4) + hueco de criterio. Confianza MEDIA-BAJA.
- **4d Reporte (M6):** "optimización continua" sin definir (hueco #23). Confianza MEDIA con hueco.
- **4c Multi-agente (M3):** pura orquestación sobre clinics validado; sin proveedor; sin hueco nuevo. **Confianza ALTA → se ejecuta.**

## Evidencia (corrida 2026-06-13)
- `python3 connector.py oracle` → **PASA**. Casos: lote válido ✓, lote vacío bloquea ✓, falta cliente bloquea ✓, **atomicidad** (1 agente inválido bloquea el lote) ✓, **colisión de sesión** (mismo slug) bloquea ✓, composición de N payloads con sesiones únicas y `plan=basic` ✓.
- `dry_run` (demo Grupo Dental Sonrisa, 2 agentes US) → cotiza Starter por agente, compone 2 payloads y 2 comandos, **no ejecuta nada**; deja el precio del bundle Gold como pendiente (hueco #17), no lo inventa.
- `execute` sin `--confirm`/`CLINICS_REPO` → **NO ejecuta** (GUARDA-001), imprime los comandos para correr a mano.

## Condición de cierre del submódulo (falsable) — verificación
1. `packages/multi-agente/` con `manifest` + `inputs` validados → ✅
2. `dry_run()` corre sin efectos irreversibles → ✅
3. `execute()` solo con `--confirm` ([[GUARDA-001]]) y sin cuentas hardcodeadas ([[GUARDA-005]]) → ✅
4. `oracle` **PASA**, registrado aquí → ✅
5. Cero cambios en repos de producto → ✅ (`git status` de `resultados/agente-clinicas` = limpio; el módulo solo importa el conector y delega tras OK humano)

## Reglas duras propias añadidas
- **Lote atómico** (GUARDA-003): un agente inválido bloquea el lote entero — no hay creación parcial.
- **Sesión única**: dos agentes con el mismo slug de nombre → BLOQUEO (cada tenant exige sesión propia, verdad de agente-clinicas).

## Bloqueo conocido (no se inventa)
Precio del **bundle Gold** (no del agente Starter suelto) → mapeo tier→plan para Gold, **hueco #17 / [[DEC-009]]**. Decisión humana pendiente.

## Veredicto
Lógica de la capa **PASA** el oráculo y respeta todas las guardas.

**Ratificado por Jordy el 2026-07-16.** El submódulo 4c queda **cerrado**.

**Deuda asumida en la ratificación (no se tapa):** sigue **sin correrse la ejecución real end-to-end**
(N agentes creados contra una DB de prueba), así que **no iguala el rigor de [[VEREDICTO-001]]**, que
verificó por REST + `psql`. Se intentó el 2026-07-16 y no fue posible: `supabase` CLI y `psql` no están
instalados en la máquina. Jordy ratifica con ese hueco a la vista.

**Confianza: media-alta.** Alta en la lógica de la capa (oracle re-corrido 2026-07-16 → PASA). Media en
el conjunto: la ejecución real no se ha visto correr ni una vez.

**Siguiente paso que esta ratificación desbloquea:** Silver ([[DEC-014]]). **Precondición dura antes de
venderlo:** el RLS de `agente-clinicas` — 0 policies hoy, aislamiento solo de aplicación, con historiales
de pacientes. Silver = 3 agentes × N clínicas es exactamente la carga que lo rompe.

**Relaciones:** realiza submódulo 4c de `.claude/megagoal.md` · compone [[VEREDICTO-001]] · gobernado por [[GUARDA-001]] · habilitado por contrato de `contrato-capacidades`.
