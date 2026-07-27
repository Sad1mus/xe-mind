# Onboarding Meta Tech Provider — Embedded Signup (GATE HUMANO)

> **Esto NO lo puede hacer Xe.** Volverse Tech Provider y pasar el App Review son trámites de cuenta y revisión de Meta: los ejecuta un humano en `business.facebook.com` + `developers.facebook.com`. Xe construye y testea TODO el código de Embedded Signup sin esto (Fases 1–5 del goal `goal-queue-embedded-signup.md`), pero el flujo **en vivo** queda bloqueado hasta que estos pasos cierren y entregues los 5 datos del final.
>
> Fuente: doc oficial `developers.facebook.com/docs/whatsapp` (Cloud API · Business Management API · Embedded Signup / Facebook Login for Business). Los nombres exactos de pantallas en Meta cambian; verificar contra la doc vigente al ejecutar.

---

## Por qué existe este gate

Embedded Signup = el "botón de conectar" que deja al cliente enlazar su WhatsApp en ~2 min sin tocar tokens ni IDs. Para ofrecerlo, **la agencia** debe estar registrada ante Meta como **Tech Provider** (antes "Solution Partner"/BSP) y su app debe tener **acceso avanzado aprobado** a los permisos de WhatsApp. Sin eso, el popup de Meta ni siquiera se puede montar.

---

## Checklist (orden por lead-time; ⏳ = espera a revisión de Meta, no depende de ti)

### A. Negocio y app
- [ ] **Verificación del negocio** de la Meta Business de la agencia (nombre legal, dirección, documento). ⏳ *la aprueba Meta.*
- [ ] **App de Meta** tipo **Business** creada en `developers.facebook.com` → producto **WhatsApp** agregado.
- [ ] Anotar el **App ID** y el **App Secret** (Configuración → Información básica).

### B. Tech Provider + permisos
- [ ] Confirmar el estatus/rol de **Tech Provider** para la app (habilita gestionar activos WhatsApp de terceros).
- [ ] **App Review — acceso avanzado** para:
  - [ ] `whatsapp_business_management`
  - [ ] `whatsapp_business_messaging`
  - [ ] (según el flujo) `business_management`
  ⏳ *App Review lo revisa Meta; puede pedir video/descripción de uso.*

### C. Embedded Signup
- [ ] Agregar **Facebook Login for Business** a la app.
- [ ] Crear una **configuración de Embedded Signup** (define qué activos y permisos pide el popup) → obtener el **`config_id`**.
- [ ] Registrar el **dominio del callback** en los **URIs de redirección OAuth válidos** de la app (el dominio donde vivirá `/es-callback`, p. ej. `wa.<dominio-region>`).

### D. Webhooks
- [ ] Definir un **verify token** para el handshake del webhook (string secreto, lo elige la agencia).
- [ ] (Se conecta en Fase 3/5 del goal, con el dominio + Caddy ya montados.)

---

## ➡️ Datos que Xe necesita de vuelta (por canal seguro, NUNCA a git ni chat abierto)

Al cerrar el checklist, entregar estos 5 para operar el flujo en vivo:

| Dato | De dónde sale | ¿Secreto? |
|---|---|---|
| `META_APP_ID` | App → Información básica | No |
| `META_APP_SECRET` | App → Información básica | 🔴 **Sí** |
| `EMBEDDED_SIGNUP_CONFIG_ID` | La configuración de Embedded Signup (paso C) | No |
| `GRAPH_API_VERSION` | Versión de Graph vigente al montar (p. ej. `v22.0`) | No |
| Dominio del callback | El que registraste en los URIs OAuth (paso C) | No |

> El **token de negocio de cada cliente** NO va acá: lo obtiene Xe en runtime intercambiando el `code` de Embedded Signup (paquete `onboarding-meta`). Ese token es de terceros (permitido headless) pero vive por env 600 en la VPS, jamás en el repo.

---

## Qué desbloquea

Con estos 5 datos, `packages/onboarding-meta` puede reemplazar su cliente Graph **fake** por el real (hueco `PENDIENTE-META-APP`) y el flujo cliente→popup→`code`→provisioning→visto humano→go-live corre de punta a punta. Hasta entonces: todo el código existe, testea y bloquea, pero no ejecuta contra Meta.

**Relaciones:** desbloquea `goal-queue-embedded-signup.md` (Fases 1–5) · mecanismo de provisioning de [[DEC-017]] (construir auto, entregar humano) · encaja en Fase D del canal de mando · restringido por [[GUARDA-001]] (envío al cliente = humano) y [[GUARDA-002]] (residencia por región).
