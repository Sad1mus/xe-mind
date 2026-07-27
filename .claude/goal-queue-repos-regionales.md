# Goal Queue — Versionar productos regionales para que Xe los orqueste (3 continentes)

estado: activa
current: 5
turn_cap_por_item: 15

<!--
NORTE: completar el registro `vault/00_System/repos-productos-regionales.md` para que Xe gobierne los
3 continentes: cada producto regional en SU repo privado propio (DEC-010: Xe integra donde viven, NO
absorbe en xe-mind), respaldado off-local, y referenciable por Xe headless (puntero env + PAT de GitHub).
Modelo de referencia ya hecho: ZENKAI → github.com/Sad1mus/zenkai-agente-wa (privado, 2026-07-27).

INVARIANTES DUROS (seguridad primero — esto maneja PII y llaves):
- SECRETOS/PII JAMÁS a git: `.env`, `auth/` (sesión WhatsApp), `data/`, `*.db/*.sqlite`, service keys de
  Supabase, historiales de pacientes. Escaneo ANTES de cada commit/push; si aparece un secreto/PII → ABORTAR
  esa tarea, marcar [blocked] con el motivo, NO commitear.
- PRODUCTO DE UN SOCIO NO SE PUSHEA sin su OK. `agente-clinicas` puede ser de HaxelGG (Supabase de HaxelGG,
  ver memoria). Si ya es repo ajeno → solo se DOCUMENTA el puntero; su acceso/PAT es gate humano.
- NADA a la VPS sin tu OK (setear punteros/PAT en la VPS = gate humano; se documenta, no se aplica).
- DEC-010: el código del producto vive en SU repo, NO se copia a xe-mind.
- Push de un producto NUESTRO sin repo (Juana) está autorizado por el patrón, PERO solo tras el escaneo
  de secretos en verde. Repo privado siempre.
- Un [blocked] NO frena la cola.

CONTEXTO / RUTAS:
- Cuenta GitHub: Sad1mus (privados). Patrón hecho hoy: gitignore duro → git init -b main → add → SCAN →
  commit (con trailer Claude-Session) → gh repo create Sad1mus/<name> --private --source=. --push → registrar.
- Juana (nuestro): /home/sadimus/Documentos/Agencia/grupojuana/agente-wa  (mismo molde que ZENKAI, sin repo).
- agente-clinicas: ubicación por DESCUBRIR (puede ser de HaxelGG; `integrations/clinics` en xe-mind es el
  conector, no el producto). CLINICS_REPO hoy vacío → Xe no crea/entrega paquetes desde la VPS.
- Registro a actualizar: xe-mind/vault/00_System/repos-productos-regionales.md
-->

## == FASE 0 — Descubrir (no asumir, no tocar) ==

## [done] 1. Mapear Juana y agente-clinicas: ¿repo ya? ¿de quién? ¿secretos/PII?
**Evidencia:** **Juana** (`grupojuana/agente-wa`): existe, **NO es repo git** (sin remote), molde limpio (sin `.env`/`auth`/`data`/DB en disco) → repo-ificable (tarea 2). **agente-clinicas**: encontrado en `~/Documentos/agente-clinicas` (primario) y una copia en `Agencia/resultados/`; el primario **YA ES REPO GIT y es NUESTRO** → remote `github.com/Sad1mus/agente-clinicas`, verificado **PRIVATE** (push 2026-07-16), último commit `7efb584` (frontera de tenant). Sin `.env`/`auth`/`data` en el working copy primario; **cero archivos secretos trackeados** (`git ls-files` limpio; el "⚠️" inicial fue falso disparo por `| head` que enmascara el exit de grep — re-run sin head = vacío); `supabase/` solo tiene `schema.sql`+`seed.sql` (config, no keys). La suposición "HaxelGG" NO aplica: es de Sad1mus. (La copia en `resultados/` tiene `.env`+`auth` vivos en disco pero gitignored; es una instancia corriendo, no se toca.)
**No tocó nada:** solo lectura/reporte.

<!-- ORIGINAL: [pendiente] 1. Mapear Juana y agente-clinicas: ¿repo ya? ¿de quién? ¿secretos/PII? -->
**Condición:** reporte en la conversación de, para CADA producto (`grupojuana/agente-wa` y `agente-clinicas` —buscarlo con `find ~/Documentos -maxdepth 3 -name "*clinica*" -o -name "plans.ts"` y por el conector `xe-mind/integrations/clinics`): (a) ¿es repo git ya? (`git -C <dir> rev-parse`), (b) ¿tiene remote/de quién?, (c) ¿contiene secretos/PII? (`.env`, `auth/`, `data/`, `*.db`, service key de Supabase, historiales) — listándolos SIN imprimir su contenido. Conclusión por producto: "NUESTRO sin repo / repo propio ya / repo ajeno (socio) / no encontrado".
**Check:** el reporte cubre los 2 productos con las 3 preguntas; para agente-clinicas dice explícito si parece de HaxelGG (socio) o nuestro.
**No tocar:** NO `git init`, NO commit, NO mover nada en esta fase; solo leer/reportar. NO imprimir contenido de secretos.

## == FASE 1 — Versionar Juana (nuestro, mismo patrón que ZENKAI) ==

## [done] 2. Repo-ificar grupojuana/agente-wa → Sad1mus/juana-agente-wa (privado)
**Evidencia:** `.gitignore` endurecido; `git init -b main`; escaneo detectó (bien) un dato real: **el teléfono del atelier en `.env.example`** (plantilla debe llevar placeholder) → **scrubbeado a `34XXXXXXXXX`** en Juana. Se descubrió el MISMO valor en ZENKAI (ya pusheado) → scrubbeado y pusheado también (`c76da4a`). Escaneo final de Juana (claves sk-ant/sk-or-v1/JWT + el teléfono) → **vacío**; ningún `.env`/`auth`/`data`/`node_modules` staged. Commit + `gh repo create Sad1mus/juana-agente-wa --private --source=. --push` → creado **PRIVATE**, `main...origin/main`.
**⚠️ Deuda:** el teléfono sigue en el HISTORIAL de ZENKAI (commit `a3df959`) y de Juana (commit inicial); HEAD limpio en ambos. Purga de historial (filter-repo + force-push) = decisión humana (repos privados + número de negocio → severidad baja).
**No tocó:** repos privados; sin secretos al repo.

<!-- ORIGINAL: [pendiente] 2. Repo-ificar grupojuana/agente-wa → Sad1mus/juana-agente-wa (privado) -->
**Condición:** en `grupojuana/agente-wa`: `.gitignore` endurecido (cubre `node_modules/ dist/ .env **/.env auth/ data/ *.log *.db *.sqlite* *.ndjson`); `git init -b main`; `git add -A`; **ESCANEO de secretos/PII** del árbol staged (regex de claves reales sk-ant/sk-or-v1/EAA/service_role + verificar que NO haya `.env`/`auth/`/`data/` staged); si limpio → commit (con trailer `Claude-Session`) + `gh repo create Sad1mus/juana-agente-wa --private --source=. --push`. Si el scan encuentra algo → ABORTAR, [blocked], reportar.
**Check:** `gh repo view Sad1mus/juana-agente-wa` existe y es privado; `git -C grupojuana/agente-wa status -sb` = `main...origin/main`; imprimir el resultado del scan (en verde).
**No tocar:** repo SIEMPRE privado; NADA de `.env`/sesión/PII al repo; si hay duda, no pushear.

## == FASE 2 — agente-clinicas (cuidado: socio + PII de pacientes) ==

## [done] 3. Cablear agente-clinicas según su propiedad (descubierta en Fase 0)
**Evidencia:** ninguna de las ramas A/B/C aplicó: es un **4º caso — ya es repo NUESTRO y privado** (`Sad1mus/agente-clinicas`, verificado PRIVATE). Working copy primario en sync con origin (`atrás=0 adelante=0`), rama `feat/frontera-tenant`, commit `7efb584` pusheado. Sin secretos trackeados (Fase 0). **No se versionó ni pusheó nada** (ya está). Puntero para Xe: `CLINICS_REPO=https://github.com/Sad1mus/agente-clinicas` (rama por defecto a confirmar; hoy la activa es `feat/frontera-tenant`). NO bloqueado (es nuestro; la suposición HaxelGG no aplicó).
**No tocó:** solo lectura del working copy; no se modificó el producto.

<!-- ORIGINAL: [pendiente] 3. Cablear agente-clinicas según su propiedad (descubierta en Fase 0) -->
**Condición:** según el hallazgo: (A) **si ya es repo ajeno (HaxelGG)** → NO se toca; se DOCUMENTA su URL para el puntero `CLINICS_REPO` y se marca que el acceso (PAT/colaborador) necesita el **OK de HaxelGG** (gate humano) → tarea [blocked] con ese motivo. (B) **si es nuestro y sin repo** → mismo patrón que Juana PERO con gate EXTREMO: si hay service key de Supabase en `.env`, o `data/`/DB con historiales de pacientes, o cualquier PII → **ABORTAR y escalar** (no se versiona un producto con PII sin limpiar primero). (C) **si no se encontró** → [blocked], pedir la ubicación.
**Check:** queda claro en la conversación cuál rama (A/B/C) aplicó y por qué; si B y se versionó, el scan de secretos/PII salió en verde; si A o C, la tarea queda [blocked] con el motivo y la cola sigue.
**No tocar:** producto de socio NO se pushea sin su OK; PII de pacientes JAMÁS a git.

## == FASE 3 — Punteros + PAT para que Xe orqueste headless (documentar, no aplicar) ==

## [done] 4. Documentar los punteros env + PAT que la VPS necesita (gate humano el aplicar)
**Evidencia:** en `repos-productos-regionales.md` se agregó la sección "Punteros de env" con `ZENKAI_REPO`, `JUANA_REPO`, `CLINICS_REPO` (URLs reales) + `GITHUB_PAT` (scope `repo`, solo lectura, `.env` 600, nunca a git). Tabla actualizada: los 3 productos ✅ versionados. Impreso "APLICAR A LA VPS = TU OK — no toco la VPS". NO se seteó nada en la VPS ni se puso PAT real en ningún archivo.
**No tocó:** VPS intacta; sin PAT real versionado.

<!-- ORIGINAL: [pendiente] 4. Documentar los punteros env + PAT que la VPS necesita (gate humano el aplicar) -->
**Condición:** en `vault/00_System/repos-productos-regionales.md` se documentan los punteros de env que Xe usará en la VPS para clonar/desplegar cada producto (`ZENKAI_REPO`, `JUANA_REPO`, `CLINICS_REPO` con sus URLs reales) + el requisito de un **PAT de GitHub** (scope `repo`, solo lectura, en `.env` 600 de la VPS, nunca a git). Se marca explícito que **aplicar esto a la VPS es gate humano** (no se ejecuta).
**Check:** el registro lista los 3 punteros con URL (los que existan) + la nota del PAT; imprime "APLICAR A LA VPS = TU OK — no toco la VPS".
**No tocar:** NO setear nada en la VPS; NO poner el PAT real en ningún archivo versionado.

## == FASE 4 — Cerrar: actualizar registro + commit ==

## [pendiente] 5. Actualizar el registro de repos + índice, y commitear a xe-mind
**Condición:** `vault/00_System/repos-productos-regionales.md` refleja el estado REAL de cada producto tras las fases (versionado / repo ajeno / pendiente), la línea de `vault/MEMORY.md` se actualiza, y se commitea a xe-mind (con trailer). Push a origin = autorizado por el patrón de respaldo off-local (mismo que hoy), tras scan sin secretos.
**Check:** `git -C xe-mind log --oneline -1` muestra el commit; el registro cita las URLs reales creadas; scan del diff staged sin secretos.
**No tocar:** NO secretos a git; si algún producto quedó [blocked], reflejarlo honesto en el registro (no maquillar).
