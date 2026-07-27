# RUNBOOK — Fase D: Xe orquesta la entrega desde la VPS

> Cómo se enciende que Xe **cree/entregue paquetes** desde la VPS. Todo lo de código está construido y
> probado en dry-run (goal `goal-queue-fase-d-entrega.md`). Lo de abajo es **acción humana** (tu OK):
> setear credenciales/punteros y decidir cada entrega real. **Este runbook NO se ejecutó.**

## Reparto (no negociable — GUARDA-001 / DEC-017)
- **Automático (Xe, reversible):** traer el producto desde su repo (`repo_fetch`), correr el discovery,
  armar el payload y el comando de entrega en **dry-run** (`entrega_dryrun`). El gate lo permite.
- **Humano (visto obligatorio):** correr `nueva_clinica` (INSERT en Supabase de producción) y el envío al
  cliente. El gate los **frena** (outbound→deny) hasta tu OK.

## Paso 1 — Credenciales y punteros en la VPS (`.env` 600, JAMÁS a git)
En el `.env` del contenedor de Xe (permiso 600, en la VPS):
```
GITHUB_PAT=<token>          # scope `repo` (privados), SOLO lectura. Nunca a git, nunca impreso.
CLINICS_REPO=/data/checkouts/agente-clinicas    # ruta LOCAL donde repo_fetch clona el producto
```
- `repo_fetch` clona `https://github.com/Sad1mus/agente-clinicas` a `CLINICS_REPO` usando el PAT
  (token inyectado solo en el clone, borrado del remote después).
- El PAT es token de terceros → funciona headless (no es API key de Anthropic).

## Paso 2 — Traer/actualizar el producto (Xe, reversible)
```
GITHUB_PAT=$GITHUB_PAT python3 integrations/clinics/repo_fetch.py clone \
  --repo https://github.com/Sad1mus/agente-clinicas --dest $CLINICS_REPO --branch <rama-default>
```
(Rama por defecto a confirmar; hoy la activa es `feat/frontera-tenant`.) `npm ci` dentro del checkout
si hace falta ejecutar el script después.

## Paso 3 — Entrega en dry-run desde Telegram (Xe, gateado)
El operador pide por Telegram "entregá a <cliente> Starter". Xe corre (gate lo permite):
```
CLINICS_REPO=$CLINICS_REPO python3 integrations/clinics/entrega_dryrun.py dry-run --json '{...discovery...}'
```
→ devuelve el **comando exacto** de `nueva_clinica` que se correría, sin ejecutar. Xe lo deja para tu visto.

## Paso 4 — Entrega REAL (VISTO HUMANO — el gate la frena sola)
Solo tras tu OK explícito, y con las envs de Supabase de producción presentes:
```
cd $CLINICS_REPO && npx tsx scripts/nueva_clinica.ts --json '{...,"plan":"basic"}'
```
- Esto hace el **INSERT en Supabase** (irreversible) + provisiona el agente. El gate lo clasifica
  `outbound`→**deny** en modo autónomo: requiere tu confirmación fuera del canal automático.
- Falta además: escanear el **QR de WhatsApp** (o Cloud API) y el **envío al cliente** — pasos humanos.

## Qué queda para el execute real (los gates)
1. 🔴 **Setear `CLINICS_REPO` + `GITHUB_PAT`** en la VPS (Paso 1) — tu OK.
2. 🔴 **Envs de Supabase de producción** disponibles para `nueva_clinica` (service key = secreto; VPS 600).
3. 🔴 **Tu visto por entrega** (INSERT + envío) — nunca automático (GUARDA-001).
4. Confirmar la **rama por defecto** de agente-clinicas para el clone.

## Estado (2026-07-27)
Construido + probado en dry-run: `repo_fetch` (oracle PASA, clone real del privado OK), `entrega_dryrun`
(oracle PASA, comando armado sin ejecutar), gate (20 casos: dry-run→allow, `nueva_clinica`→deny).
**Nada aplicado a la VPS ni a Supabase.** Aplicar = tu OK.

**Relaciones:** cierra el hueco Fase D de [[DEC-010]] · usa el registro `vault/00_System/repos-productos-regionales.md` · gobernado por [[GUARDA-001]] (entrega = humano) · pricing/tier por [[DEC-006]]/[[DEC-009]] (solo Starter→basic firmado).
