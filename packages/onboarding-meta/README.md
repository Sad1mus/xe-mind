# onboarding-meta — provisioning por Embedded Signup

Mecanismo de provisioning de [[DEC-017]]: el `code` de Embedded Signup dispara la **construcción** del paquete WhatsApp Cloud de un cliente nuevo; la **apertura/entrega al cliente** queda en visto humano (GUARDA-001).

## Contrato
```
python3 connector.py oracle          # auto-verificación -> ORACLE: PASA
python3 connector.py dry-run         # 6 pasos, SIN red ni DB (FakeGraph)
REGISTRO_DB=/tmp/x.db python3 connector.py execute --confirm --json '{...}'   # alta REAL en registro
```

Input: `{code, cliente:{nombre}, lente∈{Americas,EMEA,APAC}, tier∈DEC-006, marca, [pin, callback_url, verify_token]}`.

## Flujo (6 pasos)
1. `exchange_code` → token del cliente · 2. leer `WABA_ID`/`PHONE_NUMBER_ID` · 3. `subscribe_app` · 4. `register_number` · 5. `set_webhook` · 6. alta en `packages/registro` (estado `onboarding`).
**go-live NO está** en el flujo automático: es visto humano (DEC-017 Dec.4).

## Bloqueos (no inventar)
- **PENDIENTE-META-APP:** `RealGraph` lanza hasta que Fase 0 (Tech Provider + App Review) entregue las credenciales. Todo se prueba con `FakeGraph` (determinista, sin red). Ver `vault/00_System/onboarding-meta-tech-provider.md`.
- **hueco #26:** `EtherLabX`=LATAM se pasa como `marca` explícita sobre `lente` `Americas` (registro usa Americas/EMEA/APAC); no se auto-mapea.
- Ningún token real vive en el repo; `FakeGraph` devuelve tokens marcados `FAKE-…`.
