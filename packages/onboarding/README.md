# onboarding — discovery → cotización → alta → entrega (norte v1)

Realiza el **norte v1** de CLAUDE.md §9.2: el flujo de punta a punta con que Xe capta y da de alta
un cliente. **Compone** lo ya construido sin reimplementarlo:

- **`packages/registro`** → da de alta cliente+proyecto (verdad exacta §3.1, con residencia).
- **`integrations/clinics`** → valida el discovery (DEC-004) y arma el payload de entrega (Starter→basic).

## El flujo
```
prospecto (discovery DEC-004) → quote (DEC-006, por lente/tier) → alta en registro (cliente+proyecto)
        → payload de entrega (si tier mapea a plan firmado) → STOP en GUARDA-001
        → [HUMANO --confirm] → alta escrita en registro · NUNCA cobra/firma/envía
```

## Cómo cumple el contrato
- **inputs** → `{ prospecto:{nombre,vertical,telefono_humano,...}, lente∈{Americas,EMEA,APAC}, tier∈DEC-006, capacidades[] }`.
- **dry_run()** → discovery + quote + alta propuesta + payload de entrega. No escribe.
- **execute()** → solo con `--confirm`: da de alta en `registro` (env `REGISTRO_DB`). No cobra/firma/envía (GUARDA-001).
- **oracle** → valida la lógica del flujo: discovery/lente/tier, quote sin invención, alta coherente, entrega Starter→basic vs PENDIENTE.

## No inventa (huecos, no se rellenan)
- **#14 precios:** solo cotiza lo publicado (Gold US $1,749 / EU €1,149); el resto → `CONFIRMAR (FX en propuesta)`.
- **#17 entrega:** payload solo para `Starter→basic` (DEC-009); otros tiers → `PENDIENTE-#17`.
- **#26 marca:** lente `APAC` no tiene marca firmada (DEC-007 no la cubre) → BLOQUEO.
- ⚠️ Discovery hoy ceñido a verticales de clinics (vet/dental/estética) por reusar su validación.

## Uso
```bash
python3 connector.py oracle
python3 connector.py dry-run
REGISTRO_DB=/tmp/reg.db python3 connector.py execute --confirm --json '{...}'
```
