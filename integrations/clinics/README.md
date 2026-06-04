# integrations/clinics — Conector al producto `agente-clinicas`

Xe orquesta el asistente de WhatsApp de clínicas **sin tocar ni mover** `agente-clinicas`. Onboarding de un cliente **Starter** de vertical clínica: discovery → cotización → asistente vivo.

## Uso
```bash
python3 connector.py dry-run                 # demo (vet US): valida, cotiza, construye payload, SE DETIENE
python3 connector.py dry-run --json '{...}'  # con tu cliente
python3 connector.py oracle                  # verifica paridad con nueva_clinica.ts
python3 connector.py execute --json '{...}' --confirm   # solo con OK humano + env CLINICS_REPO
```

## Contrato cumplido
- **inputs**: requeridos `nombre · vertical · telefono_humano`; vertical ∈ {veterinaria, dental, estetica}. Falta → **bloqueo** (GUARDA-003).
- **quote**: Starter por región (DEC-006). US = $399 publicado; EU/LATAM = CONFIRMAR (no inventa).
- **dry_run**: payload exacto + comando, **sin escribir**.
- **execute**: delega a `agente-clinicas/scripts/nueva_clinica.ts` **solo con `--confirm` + env `CLINICS_REPO`** (GUARDA-001). Sin eso, emite el comando para que lo corra el humano.
- **oracle**: espeja la validación real de `nueva_clinica.ts` (requeridos, whitelist de vertical, `plan=basic`, limpieza de teléfono). `oracle → PASA`.

## Guardas
GUARDA-005 (la ruta al producto sale de `env CLINICS_REPO`, nada hardcodeado) · GUARDA-002 (residencia: el producto declara su región) · DEC-009 (`Starter→basic`).

> **Pendiente para ejecución real:** `export CLINICS_REPO=<ruta a agente-clinicas>` + decidir Supabase destino (el conectado es de HaxelGG/org Zenkai → requiere su OK) + correr con `--confirm`.
