#!/usr/bin/env python3
"""
graph_client — la interfaz de las llamadas a Meta Graph que usa el provisioning de Embedded Signup,
con dos implementaciones:

  · FakeGraph  — determinista, SIN red. Para dry-run / oracle / tests. Deriva ids del `code`
                 (sin azar ni reloj) y devuelve un token claramente marcado 'FAKE-' (nunca real).
  · RealGraph  — HUECO 'PENDIENTE-META-APP': cada método lanza hasta que Fase 0 (Tech Provider +
                 App Review) entregue META_APP_ID / META_APP_SECRET / EMBEDDED_SIGNUP_CONFIG_ID.
                 No se implementa contra Meta sin esas credenciales (GUARDA-003, no se inventa).

Interfaz (ambas la cumplen):
  exchange_code(code) -> {token, waba_id, phone_number_id}
  subscribe_app(waba_id, token) -> {ok, ...}
  register_number(phone_number_id, token, pin) -> {ok, ...}
  set_webhook(waba_id, token, callback_url, verify_token) -> {ok, ...}
"""

PENDIENTE_META = "PENDIENTE-META-APP"


class FakeGraph:
    """Determinista, sin red. Para dry-run/oracle/tests."""

    def exchange_code(self, code: str) -> dict:
        h = str(abs(hash(code)) % 10_000_000_000).rjust(10, "0")
        return {
            "token": f"FAKE-TOKEN-{h[:6]}-no-real",
            "waba_id": f"WABA-{h}",
            "phone_number_id": f"PNID-{h}",
        }

    def subscribe_app(self, waba_id, token):
        return {"ok": True, "waba_id": waba_id}

    def register_number(self, phone_number_id, token, pin):
        return {"ok": True, "phone_number_id": phone_number_id}

    def set_webhook(self, waba_id, token, callback_url, verify_token):
        return {"ok": True, "callback_url": callback_url}


class RealGraph:
    """Hueco PENDIENTE-META-APP. Sin credenciales de Fase 0, no llama a Meta."""

    def _blocked(self, *_a, **_k):
        raise NotImplementedError(
            f"{PENDIENTE_META}: la app real de Meta no existe hasta completar Fase 0 "
            "(Tech Provider + App Review). Ver vault/00_System/onboarding-meta-tech-provider.md."
        )

    exchange_code = subscribe_app = register_number = set_webhook = _blocked
