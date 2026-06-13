# multi-agente (M3) — N agentes por cliente

Capacidad componible que cierra el gap **M3** de Gold: clinics es multi-tenant pero entrega
**1 agente/cliente**; esta capa lleva a **N agentes bajo un mismo cliente** (sedes, roles:
agendamiento/ventas/soporte) **componiendo** el conector `integrations/clinics` — sin
reimplementarlo y sin tocar el producto `agente-clinicas`.

## Cómo cumple el contrato
- **manifest** → `manifest.json` (tier Gold, compone `integrations/clinics`).
- **inputs** → `{ cliente, region?, agentes: [ {nombre, vertical, telefono_humano, rol?, ...} ] }`.
  Cada agente se valida con la **verdad de clinics** (`clinics.validate`), no con reglas nuevas.
- **dry_run()** → muestra cotización por agente, los N payloads y los N comandos. No ejecuta nada.
- **execute()** → delega N veces a `nueva_clinica.ts`; **solo con `--confirm` + env `CLINICS_REPO`**
  (GUARDA-001, GUARDA-005).
- **oracle** → verifica la **lógica nueva** de esta capa (lote atómico, colisión de sesión,
  composición de payloads). La lógica de clinics ya tiene su propio oráculo.

## Reglas duras propias
- **Lote atómico**: un agente inválido bloquea el lote entero (GUARDA-003: no invención parcial).
- **Sesión única**: dos agentes cuyo nombre produce el mismo slug → BLOQUEO (cada tenant exige sesión propia).

## Uso
```bash
python3 connector.py dry-run                 # demo (Grupo Dental Sonrisa, 2 agentes)
python3 connector.py oracle                  # PASA/FALLA
python3 connector.py execute --json '{...}'  # exige --confirm + CLINICS_REPO
```

## Bloqueo conocido (no se inventa)
El **precio del bundle Gold** (no el del agente Starter suelto) depende del mapeo tier→plan para
Gold — **hueco #17 / [[DEC-009]]**, decisión humana pendiente. El `dry_run` cotiza el agente
Starter y deja el bundle marcado como pendiente.
