#!/usr/bin/env python3
"""
Capacidad onboarding-meta — provisioning por Embedded Signup (DEC-017: construir auto, entregar humano).

Disparador: un cliente NUEVO conecta su WhatsApp por Embedded Signup y llega un `code`. Xe:
  1. intercambia el `code` por el token de negocio del cliente (Graph oauth),
  2. lee WABA_ID + PHONE_NUMBER_ID,
  3. suscribe la app a la WABA,
  4. registra el número (Cloud API),
  5. apunta el webhook al receptor de la VPS,
  6. da de alta el cliente en packages/registro (verdad exacta §3.1), estado 'onboarding'.
El "abrir al público / primer envío al cliente" NO ocurre aquí: es visto humano (GUARDA-001, Task 7 del gate).

DISEÑO honesto:
  - Todas las llamadas a Meta van tras un CLIENTE GRAPH INYECTABLE.
    · FakeGraph  = determinista, SIN red — para dry-run / oracle / execute de prueba.
    · RealGraph  = hueco PENDIENTE-META-APP: lanza hasta que Fase 0 (Tech Provider) entregue
                   META_APP_ID/META_APP_SECRET/EMBEDDED_SIGNUP_CONFIG_ID. NO se inventa (GUARDA-003).
  - Ningún token real vive en el repo. FakeGraph devuelve un token claramente marcado 'FAKE-...'.
  - El alta en registro es el ÚNICO efecto real (local, reversible, REGISTRO_DB por env, GUARDA-005).
    Los pasos de Meta en execute quedan SIMULADOS y rotulados PENDIENTE-META-APP.

Reglas duras: GUARDA-001 (execute solo con --confirm; jamás cobra/firma/abre al cliente) ·
GUARDA-002 (residencia por lente, la deriva registro) · GUARDA-003 (requerido faltante/lente|tier
inválido -> BLOQUEO; Meta real -> PENDIENTE-META-APP) · GUARDA-005 (REGISTRO_DB por env).

Uso:
  python3 connector.py oracle
  python3 connector.py dry-run
  python3 connector.py dry-run --json '{...}'
  REGISTRO_DB=/tmp/reg.db python3 connector.py execute --confirm --json '{...}'
"""
import argparse, importlib.util, json, pathlib, sys

_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


registro = _load("registro_connector", "packages/registro/connector.py")
graph_client = _load("graph_client", "packages/onboarding-meta/graph_client.py")

FakeGraph = graph_client.FakeGraph
RealGraph = graph_client.RealGraph
PENDIENTE_META = graph_client.PENDIENTE_META   # hueco: no hay app real hasta Fase 0 (GUARDA-003)

LENTES = registro.LENTES
TIERS = registro.TIERS
REQ = ["code", "cliente", "lente", "tier", "marca"]
# Los 6 pasos del provisioning, en orden. go-live NO está: es visto humano (DEC-017 Dec.4).
PASOS = ["exchange_code", "leer_ids", "subscribe_app", "register_number", "set_webhook", "alta_registro"]


# ─────────────────────────────────────────────────────────────────────────────
# Validación (no inventa)
# ─────────────────────────────────────────────────────────────────────────────
def validate(inp: dict):
    faltan = [k for k in REQ if not inp.get(k)]
    if faltan:
        return False, f"[BLOQUEO GUARDA-003] faltan requeridos {faltan} -> pedir al humano (no se inventa)."
    if not isinstance(inp.get("cliente"), dict) or not inp["cliente"].get("nombre"):
        return False, "[BLOQUEO GUARDA-003] 'cliente.nombre' requerido."
    if inp["lente"] not in LENTES:
        return False, f"[BLOQUEO] lente inválida '{inp['lente']}'. Usa: {LENTES} (LATAM/EtherLabX: hueco #26)."
    if inp["tier"] not in TIERS:
        return False, f"[BLOQUEO] tier inválido '{inp['tier']}'. Usa: {TIERS}."
    return True, "ok"


def build_alta(inp: dict, ids: dict) -> dict:
    """Alta mínima para registro: cliente en 'onboarding' + proyecto de conexión WhatsApp Cloud.
    plan_entrega lo deriva registro (Starter->basic firmado; resto PENDIENTE-#17). Nada se inventa."""
    nombre = inp["cliente"]["nombre"]
    return {
        "cliente": {"nombre": nombre, "lente": inp["lente"], "marca": inp["marca"],
                    "tier": inp["tier"], "estado": "onboarding"},
        "proyectos": [{
            "nombre": f"{nombre} — WhatsApp Cloud",
            "capacidades": ["whatsapp-cloud"],
            "estado": "en-construccion",
        }],
    }


def provision_plan(inp: dict, graph) -> dict:
    """Corre los 5 pasos de Meta (con el graph inyectado) y devuelve el estado de cada uno + los ids."""
    code = inp["code"]
    pin = inp.get("pin", "000000")
    callback = inp.get("callback_url", "https://wa.<region>/es-callback")
    verify = inp.get("verify_token", "<WEBHOOK_VERIFY_TOKEN>")
    ids = graph.exchange_code(code)
    steps = {
        "exchange_code": {"ok": True, "waba_id": ids["waba_id"], "phone_number_id": ids["phone_number_id"]},
        "subscribe_app": graph.subscribe_app(ids["waba_id"], ids["token"]),
        "register_number": graph.register_number(ids["phone_number_id"], ids["token"], pin),
        "set_webhook": graph.set_webhook(ids["waba_id"], ids["token"], callback, verify),
    }
    return {"ids": ids, "steps": steps}


# ---------- contrato: dry_run ----------
def dry_run(inp: dict, graph=None):
    graph = graph or FakeGraph()
    ok, msg = validate(inp)
    print(f"[inputs] {msg}")
    if not ok:
        return
    simulado = isinstance(graph, FakeGraph)
    tag = " (SIMULADO — FakeGraph, sin red)" if simulado else ""
    print(f"[provisioning Meta]{tag}")
    plan = provision_plan(inp, graph)
    ids = plan["ids"]
    print(f"  1. exchange_code -> token={ids['token']} · waba={ids['waba_id']} · phone_id={ids['phone_number_id']}")
    print(f"  2. leer_ids       -> WABA_ID + PHONE_NUMBER_ID capturados")
    print(f"  3. subscribe_app  -> {plan['steps']['subscribe_app']}")
    print(f"  4. register_number-> {plan['steps']['register_number']}")
    print(f"  5. set_webhook    -> {plan['steps']['set_webhook']}")
    c, proys = registro.compose(build_alta(inp, ids))
    print(f"  6. alta_registro  -> cliente {c['id']} ({c['marca']} · {c['lente']} · estado={c['estado']} · "
          f"{c['region_datos']}) | proyecto {proys[0]['id']} plan={proys[0]['plan_entrega']}")
    print("[go-live] STOP — GUARDA-001/DEC-017: abrir al público / enviar al cliente = VISTO HUMANO, nunca aquí.")
    if not simulado:
        print(f"  ⚠️ {PENDIENTE_META}: sin credenciales de Fase 0 el paso real de Meta se bloquea.")


# ---------- contrato: execute ----------
def execute(inp: dict, confirm: bool, graph=None):
    graph = graph or FakeGraph()
    ok, msg = validate(inp)
    if not ok:
        print(msg); sys.exit(1)
    if not confirm:
        print("[execute] NO ejecutado (GUARDA-001). Falta --confirm (OK humano explícito).")
        return
    # Pasos de Meta: SIMULADOS y rotulados (no hay app real hasta Fase 0). El único efecto real es el alta.
    plan = provision_plan(inp, graph)
    print(f"[execute] pasos Meta SIMULADOS ({PENDIENTE_META} hasta Fase 0). ids={plan['ids']['waba_id']}/"
          f"{plan['ids']['phone_number_id']}")
    print("[execute] alta en registro (REAL, reversible — no cobra / no firma / no abre al cliente):")
    registro.execute(build_alta(inp, plan["ids"]), confirm=True)
    print("[go-live] pendiente de VISTO HUMANO por Telegram (DEC-017 Dec.4). No se abre al público.")


# ---------- contrato: oracle ----------
def oracle():
    allok = True

    def check(name, cond):
        nonlocal allok
        if not cond: allok = False
        print(f"   [{'ok' if cond else 'FALLA'}] {name}")

    base = {"code": "AQD-ejemplo", "cliente": {"nombre": "Clinica Dental Sonrisa"},
            "lente": "Americas", "tier": "Starter", "marca": "EtherLabX"}

    # 1. validación: caso válido y bloqueos que NO deben pasar
    check("input válido -> ok", validate(base)[0] is True)
    check("sin code -> BLOQUEO", validate({**base, "code": None})[0] is False)
    check("sin marca -> BLOQUEO (no inventa)", validate({**base, "marca": None})[0] is False)
    check("lente inválida (LATAM) -> BLOQUEO (hueco #26)", validate({**base, "lente": "LATAM"})[0] is False)
    check("tier inválido -> BLOQUEO", validate({**base, "tier": "Platino"})[0] is False)

    # 2. FakeGraph determinista (mismo code -> mismos ids), sin red
    g = FakeGraph()
    a, b = g.exchange_code("AQD-ejemplo"), g.exchange_code("AQD-ejemplo")
    check("FakeGraph determinista (mismo code -> mismos ids)", a == b and a["waba_id"].startswith("WABA-"))
    check("FakeGraph token marcado FAKE (nunca real)", a["token"].startswith("FAKE-TOKEN-"))

    # 3. plan de provisioning: los 5 pasos Meta corren; go-live NO está en PASOS
    plan = provision_plan(base, g)
    check("provisioning corre exchange+subscribe+register+webhook",
          all(plan["steps"][s].get("ok", True) for s in ["subscribe_app", "register_number", "set_webhook"])
          and plan["steps"]["exchange_code"]["waba_id"])
    check("go-live NO está en los pasos automáticos (es humano)", "go_live" not in PASOS and "send" not in PASOS)

    # 4. alta compuesta correcta (Starter->basic firmado; cliente en 'onboarding')
    c, proys = registro.compose(build_alta(base, a))
    check("alta: cliente en estado onboarding", c["estado"] == "onboarding")
    check("alta: Starter->basic (registro deriva, no se inventa)", proys[0]["plan_entrega"] == "basic")
    check("alta: proyecto de conexión WhatsApp Cloud", proys[0]["capacidades"] == ["whatsapp-cloud"])

    # 5. RealGraph está bloqueado (hueco PENDIENTE-META-APP), no inventa una llamada real
    try:
        RealGraph().exchange_code("x"); real_blocked = False
    except NotImplementedError as e:
        real_blocked = PENDIENTE_META in str(e)
    check("RealGraph bloqueado con PENDIENTE-META-APP (no hay app real hasta Fase 0)", real_blocked)

    print("ORACLE:", "PASA" if allok else "FALLA")


DEMO = {
    "code": "AQD-embedded-signup-code-ejemplo",
    "cliente": {"nombre": "Clinica Dental Sonrisa"},
    "lente": "Americas", "tier": "Starter", "marca": "EtherLabX",
    "pin": "123456", "callback_url": "https://wa.etherlabx.com/es-callback",
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["oracle", "dry-run", "execute"])
    ap.add_argument("--json", help="input {code, cliente, lente, tier, marca, [pin, callback_url]} en JSON")
    ap.add_argument("--confirm", action="store_true", help="OK humano para el alta en registro")
    a = ap.parse_args()
    if a.accion == "oracle":
        oracle()
    else:
        inp = json.loads(a.json) if a.json else DEMO
        if a.accion == "dry-run":
            dry_run(inp)
        elif a.accion == "execute":
            execute(inp, a.confirm)
