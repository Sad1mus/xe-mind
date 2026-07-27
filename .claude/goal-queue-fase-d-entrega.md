# Goal Queue — Fase D: Xe orquesta la ENTREGA desde la VPS (traer repo → construir → visto humano)

estado: activa
current: 6
turn_cap_por_item: 15

<!--
NORTE: cerrar el hueco que hoy impide que Xe cree/entregue paquetes desde la VPS. Con los productos
ya versionados (Sad1mus/zenkai-agente-wa · juana-agente-wa · agente-clinicas — ver
vault/00_System/repos-productos-regionales.md), Xe debe poder: (1) TRAER el producto desde su repo
privado con el PAT (headless), (2) armar la ENTREGA de un cliente Starter/Silver en DRY-RUN
(discovery→payload→comando nueva_clinica), (3) dejarlo a VISTO HUMANO para el INSERT en Supabase y el
envío al cliente. Construir = automático/reversible; INSERT + envío al cliente = humano (GUARDA-001).

REFRAMES / VERDAD (no auto-engañarnos):
- Hoy `CLINICS_REPO` vacío en la VPS → Xe no trae el producto → no entrega. Este goal cablea el mecanismo.
- El motor de entrega es `agente-clinicas/scripts/nueva_clinica.ts` (Supabase INSERT + WhatsApp QR + envío).
  El INSERT a Supabase de PRODUCCIÓN y el envío al cliente son el gate humano (dinero/marca).
- `integrations/clinics/connector.py` (oracle PASA) ya arma el payload (Starter→basic, DEC-009) y el
  comando; `packages/onboarding` orquesta discovery→quote→alta→entrega. Se REUSA, no se reimplementa.

INVARIANTES DUROS:
- NADA a la VPS ni a Supabase de producción sin tu OK. El INSERT real + el envío al cliente = VISTO HUMANO.
- PAT de GitHub JAMÁS a git ni impreso; va por env 600 en la VPS. El clone del producto es a un workdir
  TEMPORAL, read-only; NO se commitea el producto dentro de xe-mind (DEC-010: integra donde vive).
- Secretos/PII jamás a git. Los checks que scanean deben GATEAR el commit (if count==0), no solo imprimir.
- No inventar (GUARDA-003): mapeo tier→plan solo Starter→basic firmado; el resto se marca PENDIENTE, no se fabrica.
- Un [blocked] no frena la cola.

RUTAS:
- xe-mind: integrations/clinics/connector.py · packages/onboarding/connector.py · packages/onboarding-meta/
- Producto: repo privado github.com/Sad1mus/agente-clinicas (script scripts/nueva_clinica.ts).
- Registro de repos + punteros: vault/00_System/repos-productos-regionales.md
- Node/tsx local (si hace falta): ~/Documentos/Agencia/grupojuana/agente-wa/node_modules/.bin/tsx
- Workdir temporal para clones de prueba: usar el scratchpad, NUNCA dentro de xe-mind.
-->

## == FASE 0 — Verificar el terreno (read-only / dry-run, no entregar) ==

## [done] 1. Correr oracles + leer cómo se ata la entrega (qué existe hoy)
**Evidencia:** **3 oracles PASA** (`integrations/clinics`, `packages/onboarding`, `packages/onboarding-meta`, con `REGISTRO_DB` desechable). `integrations/clinics/connector.py`: `cmd_for` (línea 65-66) arma `npx tsx scripts/nueva_clinica.ts --json '...'`; `CLINICS_REPO` (línea 86) es la **ruta LOCAL** al checkout — `execute` imprime `cd {repo} && {cmd}` (línea 93); `build_payload` (línea 51) espeja el input (`nombre/vertical/telefono_humano` + plan). `agente-clinicas/scripts/nueva_clinica.ts` existe (6477 B): requeridos `nombre, vertical, telefono_humano`; plan default `basic`; hace `clinicsTable().insert()` en Supabase (línea 120) = la parte irreversible (gate humano).
**Aprendizaje clave para Fase 1:** `CLINICS_REPO` = ruta local del checkout → el módulo de fetch debe clonar el repo a un workdir y ESE path es `CLINICS_REPO`.
**No tocó:** ninguna entrega ejecutada; Supabase intacto; no se clonó dentro de xe-mind.

<!-- ORIGINAL: [pendiente] 1. Correr oracles + leer cómo se ata la entrega (qué existe hoy) -->
**Condición:** reporte en la conversación de: (a) `oracle` de `integrations/clinics`, `packages/onboarding` y `packages/onboarding-meta` → todos **PASA** (con `REGISTRO_DB` desechable donde aplique); (b) cómo `integrations/clinics` espera `CLINICS_REPO` y qué comando arma (`clinics.cmd_for`/`build_payload`) — citar función:línea; (c) confirmar que `agente-clinicas/scripts/nueva_clinica.ts` existe en el repo (clonándolo o leyéndolo) y qué inputs pide. Sin ejecutar ninguna entrega real.
**Check:** las 3 líneas `ORACLE: PASA` impresas; se cita la función que arma el comando y el input de `nueva_clinica.ts`.
**No tocar:** NO ejecutar `execute` de entrega; NO tocar Supabase; NO clonar dentro de xe-mind (usar scratchpad si se clona).

## == FASE 1 — Mecanismo de traer el producto desde su repo (headless, PAT) ==

## [done] 2. Módulo de fetch del repo del producto (clone/pull con PAT), probado read-only
**Evidencia:** creado `integrations/clinics/repo_fetch.py` (Python3 stdlib): `clone(repo,dest,pat,branch)` hace `git clone --depth 1` a un workdir; con `GITHUB_PAT` inyecta `x-access-token:<pat>@` SOLO para el clone y **borra el token del remote** después (`remote set-url` limpio); nunca imprime el PAT (todo enmascarado a `***@`). **ORACLE PASA** (4/4: sin PAT→url limpia, con PAT→token inyectado pero `masked_url` lo oculta). **dry-run**: imprime el comando enmascarado + que ese dir sería `CLINICS_REPO`. **Clone REAL del privado** `Sad1mus/agente-clinicas` a scratchpad (auth ambiente, sin PAT) → trajo `scripts/nueva_clinica.ts` ✅, remote sin token, workdir borrado. Verificado: **nada clonado dentro de xe-mind** (DEC-010).
**No tocó:** producto no modificado; clone a scratchpad temporal; PAT no impreso ni persistido.

<!-- ORIGINAL: [pendiente] 2. Módulo de fetch del repo del producto (clone/pull con PAT), probado read-only -->
**Condición:** existe un módulo (p. ej. `integrations/clinics/repo_fetch.py` o `packages/repo-fetch/`) que, dado `CLINICS_REPO` + `GITHUB_PAT` (por env), hace `git clone --depth 1` (o `pull`) a un **workdir temporal** y devuelve la ruta — read-only del producto, sin efectos sobre él. En `dry-run` (sin PAT) imprime el comando exacto que correría, sin ejecutar. Se prueba el clone REAL del repo privado `Sad1mus/agente-clinicas` a un dir de scratchpad usando la auth disponible (git/gh) para demostrar que el mecanismo trae el código (en la VPS iría por PAT).
**Check:** `dry-run` imprime el comando parametrizado por env; la prueba real clona el repo a scratchpad y `ls` muestra `scripts/nueva_clinica.ts`; el workdir temporal se borra al final. El PAT nunca se imprime.
**No tocar:** NO clonar dentro de xe-mind; NO commitear el producto; NO imprimir el PAT.

## == FASE 2 — Entrega en DRY-RUN desde el producto traído ==

## [done] 3. Cablear discovery→payload→comando de entrega en dry-run (sin ejecutar)
**Evidencia:** creado `integrations/clinics/entrega_dryrun.py` (reusa `clinics.validate/build_payload/cmd_for`, no reimplementa): ata `CLINICS_REPO` (checkout traído) → comando `nueva_clinica`. **ORACLE PASA** (6/6): Starter→plan basic + comando `cd <checkout> && npx tsx scripts/nueva_clinica.ts` (string, no ejecuta); Gold→`PENDIENTE-#17` sin comando; discovery inválido→BLOQUEO; sin `CLINICS_REPO`→placeholder. **dry-run Starter** imprime el comando completo con `--json '{...,"plan":"basic"}'` + STOP GUARDA-001; **dry-run Gold** → PENDIENTE-#17, no arma comando. Nada tocó Supabase (el comando es un string impreso, no se corrió `nueva_clinica`).
**No tocó:** sin INSERT en Supabase; sin envío; solo Starter→basic (DEC-009), Gold no inventado.

<!-- ORIGINAL: [pendiente] 3. Cablear discovery→payload→comando de entrega en dry-run (sin ejecutar) -->
**Condición:** `packages/onboarding` (reusando `integrations/clinics`) toma un cliente Starter (discovery mínimo) + el producto traído en Fase 1, y produce en **dry-run** el payload de entrega (Starter→basic) + el **comando `nueva_clinica`** que correría, SIN ejecutarlo y SIN tocar Supabase. Un tier sin plan firmado → marca `PENDIENTE-#17`, no inventa. Se extiende el oracle para cubrir este dry-run e2e.
**Check:** `oracle`/`dry-run` imprime el payload + el comando de entrega para un Starter, y para un Gold marca PENDIENTE-#17; termina en STOP `GUARDA-001` (INSERT + envío = humano). Exit 0.
**No tocar:** NO ejecutar `nueva_clinica` real; NO INSERT en Supabase; NO enviar al cliente.

## == FASE 3 — Gate: construir=reversible, INSERT/envío=visto humano ==

## [done] 4. Clasificar la entrega en el gate (reusar patrón GOLIVE del canal)
**Evidencia:** `classify.ts` — `GOLIVE_RE` extendido con `nueva_clinica` + `entregar-al-cliente` (el INSERT a Supabase de producción es irreversible → siempre outbound/visto humano); la construcción/dry-run NO matchea. Oráculo del gate corrido → **20 casos verde, exit 0**: `entrega_dryrun.py dry-run`→allow (reversible), `cd ... && npx tsx scripts/nueva_clinica.ts`→deny (entrega/visto humano), + los 18 previos. `governance.ts` sin cambios (git); `unknown→baja` intacto (classify.ts). Umbral audit → 20 líneas (>=19).
**No tocó:** governance.ts; default no abierto; entrega al cliente jamás auto-aprobada.

<!-- ORIGINAL: [pendiente] 4. Clasificar la entrega en el gate (reusar patrón GOLIVE del canal) -->
**Condición:** en `infra/canal-mando/classify.ts`, la acción de **construir/dry-run** de entrega mapea a `write_reversible`/`read`, pero el **INSERT a Supabase de producción** y el **envío al cliente** (`nueva_clinica ... --execute`, `send`, `entregar-al-cliente`) mapean a una clase de **visto humano** (money/outbound → deny "pedí OK humano"). `unknown→baja` intacto; `governance.ts` sin tocar. Se agregan casos al oráculo del gate.
**Check:** oráculo del gate (`tsx infra/canal-mando/oracle.hook.ts`) verde con casos nuevos: entrega dry-run→allow; `nueva_clinica --execute`/envío→deny; todos los previos siguen. Exit 0.
**No tocar:** governance.ts; el default no se abre; el envío al cliente jamás se auto-aprueba.

## == FASE 4 — Runbook de aplicación a la VPS (gate humano, no ejecutar) ==

## [done] 5. Runbook: setear CLINICS_REPO + PAT en la VPS + correr el dry-run desde Telegram
**Evidencia:** creado `infra/RUNBOOK-fase-d-entrega.md`: Paso 1 (envs `GITHUB_PAT` scope repo read + `CLINICS_REPO` ruta local, `.env` 600), Paso 2 (`repo_fetch clone`), Paso 3 (dry-run desde Telegram, gateado), Paso 4 (entrega real `nueva_clinica` = INSERT Supabase, visto humano). Lista los 4 gates para el execute real. Impreso "APLICAR A LA VPS = TU OK — no toco la VPS ni Supabase". Nada aplicado.
**No tocó:** VPS/Supabase intactos; PAT real no versionado.

<!-- ORIGINAL: [pendiente] 5. Runbook: setear CLINICS_REPO + PAT en la VPS + correr el dry-run desde Telegram -->
**Condición:** existe `infra/RUNBOOK-fase-d-entrega.md` con los pasos EXACTOS (humano) para: setear `CLINICS_REPO` + `GITHUB_PAT` (scope `repo`, solo lectura) en el `.env` 600 de la VPS; cómo Xe corre el **dry-run de entrega** desde Telegram (gateado); y qué falta para el `execute` real (OK humano + Supabase de producción + escanear QR/enviar). Marca explícito que **aplicar a la VPS es TU OK** y no se ejecuta aquí.
**Check:** el runbook existe, lista los envs + el flujo Telegram + los gates; imprime "APLICAR A LA VPS = TU OK — no toco la VPS ni Supabase".
**No tocar:** NO setear nada en la VPS; NO poner el PAT real en ningún archivo versionado.

## == FASE 5 — DEC + cierre ==

## [pendiente] 6. DEC-019: Fase D cableada en dry-run + qué falta para execute real; docs + commit
**Condición:** existe `vault/10_Decisions/DEC-019_Fase-D-entrega-desde-VPS.md` (estado `propuesta`, fuente = este goal, con "qué la invalidaría") que fija: Xe trae el producto desde su repo (PAT) y construye la entrega en dry-run; el INSERT/envío quedan a visto humano; qué falta para el execute real. Actualiza `repos-productos-regionales.md` y el índice `MEMORY.md`. Commit a xe-mind con **gate de escaneo real** (solo commitea si el scan de secretos da 0). Push = patrón de respaldo off-local.
**Check:** DEC-019 existe con frontmatter válido y "qué la invalidaría"; índice actualizado; `git log -1` muestra el commit; scan del diff staged = 0 secretos (gateado).
**No tocar:** DEC-019 no se ratifica (sigue `propuesta`); no se inventa pricing; el scan GATEA el commit.
