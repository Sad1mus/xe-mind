# SMC — Qué falta para entregar

> **Snapshot de auditoría · 2026-06-20.** Estado del repo `Sad1mus/smc-platform` en su
> último commit. Evidencia = lectura directa del código (auditoría adversarial: sesgo a
> buscar lo que falta). Los ❓ son huecos: NO se inventan, van a
> [[preguntas-entrevista]]. Esto es status operativo, no una DEC.

**Veredicto honesto:** **no está "próximo a entregar"** como dice la descripción del
repo. El esqueleto de ingeniería es sólido y maduro; lo comercial/legal está crudo.
Tratarlo como **demo técnica funcional**, no como producto entregable a cliente de pago.

## Stack
Next.js 16 (App Router, React 19, server actions) + Supabase (Auth + Postgres con RLS) +
Stripe + embed TradingView. Tailwind v4/shadcn, Sentry condicional, Resend, pnpm. Código
de buena calidad, sin TODOs/FIXMEs reales.

## ✅ Hecho y funcionando
- **Auth completo**: email+password + Google OAuth, recuperar/actualizar password, callbacks, validación Zod, protección de rutas (`lib/auth/actions.ts`, `lib/supabase/proxy.ts`).
- **Supabase con RLS en TODAS las tablas** (profiles, plans, subscriptions, payment_events, watchlists); RBAC `is_admin()`, trigger de perfil, hardening de privilegios (`supabase/migrations/`).
- **Stripe técnicamente robusto**: webhook con firma verificada + idempotencia por `stripe_event_id`, checkout + Customer Portal (`app/api/webhooks/stripe/route.ts`, `lib/stripe/actions.ts`).
- **TradingView**: widget oficial con atribución (`components/dashboard/tradingview-chart.tsx`).
- **Dashboard**: market view, watchlist CRUD con RLS, paywall `hasActiveAccess()`.
- **Seguridad OWASP**: CSP + headers, rate limiting (`next.config.ts`, `proxy.ts`).
- **CI + tests**: GitHub Actions lint→test→build→e2e; 25 unit + 14 e2e Playwright.

## 🚧 Parcial / incompleto
- **README = boilerplate** de create-next-app. Cero setup real → fricción de handoff.
- **Rate limiting en memoria** (`lib/security/rate-limit.ts`): no funciona multi-instancia en Vercel serverless. Deuda documentada (Upstash Redis).
- **Planes sin precio en Stripe**: seed deja `stripe_price_id` NULL; hay que correr `scripts/setup-stripe.mjs` a mano o el checkout dice "plan sin precio".
- **Emails en stub** salvo `RESEND_API_KEY` (`lib/email/send.ts`).
- **Plan VIP sin flujo**: botón "Hablar con SMC" → `/registro?plan=vip`, sin formulario ni proceso de ventas.

## ❌ Falta para entregar
**BLOQUEANTES:**
1. **Stripe hard-locked a TEST mode.** `getStripe()` rechaza claves que no sean `sk_test_`/`rk_test_` (`lib/stripe/client.ts`). **La plataforma NO PUEDE cobrar dinero real.** Hay que abrir el candado para producción.
2. **Sin páginas legales.** No existe Términos / Privacidad / Reembolsos. Stripe los exige para activar modo live; LATAM/UE exigen privacidad (GDPR). Footer tiene disclaimers pero ningún link legal.
3. **Sin panel de admin** (si está en scope). PRODUCT.md define un admin que gestiona usuarios/suscripciones; existe `is_admin()`/`role='admin'` en DB pero **no hay ruta `/admin` ni UI**.
4. **Bug — pago único duplica filas.** Webhook modo `payment` hace upsert `onConflict: stripe_subscription_id` (NULL en pagos únicos) → Postgres permite múltiples NULL → cada compra crea fila nueva (`app/api/webhooks/stripe/route.ts`).

**DESEABLES:**
- Bug: customers Stripe huérfanos si se abandona el checkout (`lib/stripe/actions.ts`).
- Sin `vercel.json` → env vars a mano, deploy sin versionar.
- `/precios` no existe como ruta (resuelta como ancla `/#planes`); discrepancia con la spec.

## ❓ Huecos → van a [[preguntas-entrevista]] (no se inventan)
- ¿Precios finales y modalidad? Bronce $1.500 / Plata $2.800 (¿mensual/anual?); "Prueba" $250 pago único = 30 días de acceso — ¿es la regla querida?
- ¿El deploy en Vercel **existe y está live**? (hay commit, no verificable desde el repo)
- ¿Hay cuenta Stripe **live** con negocio verificado?
- ¿Licencia comercial de TradingView? (se usa el embed gratuito)
- ¿El panel de admin está en el MVP o se difiere? (define si es bloqueante)
- ¿Resend con dominio verificado para emails reales?

## Top bloqueantes, en orden
1. Stripe en test mode forzado → no factura live.
2. Sin páginas legales → bloquea activación Stripe + cumplimiento.
3. Sin panel de admin (si en scope).
4. Precios Stripe sin aprovisionar + bug de pago único.
5. README boilerplate + sin `vercel.json` → handoff/deploy sin documentar.

---
*Fuente: auditoría adversarial del repo (2026-06-20). Regenerar cuando cambie el estado.*
