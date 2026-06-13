#!/usr/bin/env python3
"""
Capacidad onboarding — el NORTE v1 (CLAUDE.md §9.2): discovery -> cotización -> alta -> entrega.

Orquesta lo ya construido, sin reimplementarlo:
  - packages/registro  -> da de alta cliente+proyecto (verdad exacta §3.1).
  - integrations/clinics -> valida el discovery y arma el payload de entrega (Starter->basic).

Reglas duras:
  - GUARDA-001: execute() da de alta SOLO con --confirm; NUNCA cobra/firma/envía al cliente.
  - GUARDA-003: discovery incompleto / lente|tier inválidos -> BLOQUEO; nada se inventa.
  - GUARDA-006/DEC-006: cotiza SOLO precios publicados; lo no publicado -> 'CONFIRMAR' (hueco #14).
  - DEC-009: solo Starter->basic está firmado; otro tier -> entrega 'PENDIENTE-#17', no se fabrica.
  - GUARDA-005: la DB del registro sale de env REGISTRO_DB (sin hardcode).

Uso:
  python3 connector.py oracle
  python3 connector.py dry-run                       # demo (prospecto EMEA Gold)
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
clinics = _load("clinics_connector", "integrations/clinics/connector.py")

LENTES = registro.LENTES
TIERS = registro.TIERS
MARCA_POR_LENTE = {"EMEA": "ZENKAI", "Americas": "Americas-por-definir"}  # DEC-007 (APAC sin marca firmada)
USD_BASE = {"Starter": "USD 399/mo", "Silver": "USD 699/mo", "Gold": "USD 1,749/mo",
            "Enterprise": "USD 2,999/mo", "Partner": "desde USD 5,000/mo"}  # DEC-006 columna USD
NO_PUBLICADO = "CONFIRMAR (FX en propuesta — hueco #14, no publicado)"


def quote(lente: str, tier: str) -> str:
    """DEC-006: solo precios publicados. NO inventa los no publicados."""
    if lente == "Americas":
        return USD_BASE[tier]
    if lente == "EMEA" and tier == "Gold":
        return "EUR 1,149/mo"   # único local explícito en el doc
    return NO_PUBLICADO


def marca_de(lente: str, marca_in=None):
    if marca_in:
        return marca_in, None
    if lente in MARCA_POR_LENTE:
        return MARCA_POR_LENTE[lente], None
    return None, f"[BLOQUEO GUARDA-003] sin marca firmada para lente '{lente}' (DEC-007 no cubre APAC; hueco #26)."


def validate(inp: dict):
    p = inp.get("prospecto")
    if not isinstance(p, dict):
        return False, "[BLOQUEO GUARDA-003] falta 'prospecto' (objeto discovery)."
    ok, msg = clinics.validate(p)  # DEC-004: nombre/vertical/telefono + whitelist de vertical
    if not ok:
        return False, f"discovery: {msg}"
    if inp.get("lente") not in LENTES:
        return False, f"[BLOQUEO] lente inválida '{inp.get('lente')}'. Usa: {LENTES}"
    if inp.get("tier") not in TIERS:
        return False, f"[BLOQUEO] tier inválido '{inp.get('tier')}'. Usa: {TIERS}"
    caps = inp.get("capacidades")
    if not isinstance(caps, list) or not caps:
        return False, "[BLOQUEO GUARDA-003] 'capacidades' debe ser lista no vacía."
    _, merr = marca_de(inp["lente"], inp.get("marca"))
    if merr:
        return False, merr
    return True, "ok"


def build_alta(inp: dict) -> dict:
    """Compone el alta para packages/registro (no escribe; registro valida y persiste)."""
    marca, _ = marca_de(inp["lente"], inp.get("marca"))
    p = inp["prospecto"]
    return {
        "cliente": {"nombre": p["nombre"], "lente": inp["lente"], "marca": marca, "tier": inp["tier"]},
        "proyectos": [{"nombre": f"{p['nombre']} — {inp['tier']}", "capacidades": list(inp["capacidades"])}],
    }


def delivery(inp: dict) -> dict:
    """Payload de entrega: solo si el tier mapea a un plan firmado (DEC-009: Starter->basic via clinics)."""
    p = inp["prospecto"]
    plan = registro.PLAN_FIRMADO.get(inp["tier"])   # solo Starter->basic
    if plan and p.get("vertical") in clinics.VERTICALES:
        payload = clinics.build_payload(p)
        return {"plan": plan, "payload": payload, "cmd": clinics.cmd_for(payload)}
    return {"plan": registro.PENDIENTE, "payload": None, "cmd": None}


# ---------- contrato: dry_run ----------
def dry_run(inp: dict):
    ok, msg = validate(inp)
    print(f"[inputs] {msg}")
    if not ok:
        return
    p = inp["prospecto"]
    print(f"[discovery] {p['nombre']} · vertical={p['vertical']} · lente={inp['lente']} · tier={inp['tier']}")
    print(f"[quote ] {inp['tier']} {inp['lente']} = {quote(inp['lente'], inp['tier'])}")
    c, proys = registro.compose(build_alta(inp))
    print(f"[alta -> registro] cliente {c['id']} ({c['marca']} · {c['region_datos']}) | "
          f"proyecto {proys[0]['id']} caps={proys[0]['capacidades']} plan_entrega={proys[0]['plan_entrega']}")
    d = delivery(inp)
    if d["payload"]:
        print(f"[entrega] plan={d['plan']} -> {d['cmd']}")
    else:
        print(f"[entrega] {d['plan']} — mapeo tier->plan no firmado, no se arma payload (hueco #17)")
    print("[execute] STOP — GUARDA-001: el alta corre con --confirm; NUNCA cobrar/firmar/enviar al cliente.")


# ---------- contrato: execute ----------
def execute(inp: dict, confirm: bool):
    ok, msg = validate(inp)
    if not ok:
        print(msg)
        sys.exit(1)
    if not confirm:
        print("[execute] NO ejecutado (GUARDA-001). Falta --confirm (OK humano explícito).")
        return
    alta = build_alta(inp)
    print("[execute] alta en registro (no cobra / no firma / no envía):")
    registro.execute(alta, confirm=True)   # escribe en REGISTRO_DB y hace el SELECT
    d = delivery(inp)
    print("[siguiente paso — creación del producto, con su PROPIO --confirm en clinics]:")
    print("   " + (d["cmd"] or f"{registro.PENDIENTE}: mapeo tier->plan no firmado (hueco #17)"))


# ---------- contrato: oracle ----------
def oracle():
    casos = [
        ({"prospecto": {"nombre": "Klinik", "vertical": "dental", "telefono_humano": "49"},
          "lente": "EMEA", "tier": "Gold", "capacidades": ["M1", "M3"]}, True),
        ({"prospecto": {"nombre": "X", "vertical": "dental"},
          "lente": "EMEA", "tier": "Gold", "capacidades": ["M1"]}, False),                 # falta telefono
        ({"prospecto": {"nombre": "X", "vertical": "dental", "telefono_humano": "1"},
          "lente": "LATAM", "tier": "Gold", "capacidades": ["M1"]}, False),                # lente inválida
        ({"prospecto": {"nombre": "X", "vertical": "dental", "telefono_humano": "1"},
          "lente": "EMEA", "tier": "Platino", "capacidades": ["M1"]}, False),              # tier inválido
        ({"prospecto": {"nombre": "X", "vertical": "dental", "telefono_humano": "1"},
          "lente": "APAC", "tier": "Gold", "capacidades": ["M1"]}, False),                 # APAC sin marca firmada
        ({"prospecto": {"nombre": "X", "vertical": "dental", "telefono_humano": "1"},
          "lente": "EMEA", "tier": "Gold", "capacidades": []}, False),                     # caps vacías
    ]
    allok = True
    for inp, esp in casos:
        got = validate(inp)[0]
        st = "ok" if got == esp else "FALLA"
        if got != esp:
            allok = False
        print(f"   [{st}] {inp['lente']}/{inp['tier']} -> válido={got} (esperado {esp})")
    q_es = quote("EMEA", "Silver")
    q_ug = quote("Americas", "Gold")
    q_ok = ("CONFIRMAR" in q_es and q_ug == "USD 1,749/mo")
    print(f"   [{'ok' if q_ok else 'FALLA'}] quote no inventa: EMEA/Silver={q_es} · Americas/Gold={q_ug}")
    c, proys = registro.compose(build_alta(
        {"prospecto": {"nombre": "Demo", "vertical": "dental", "telefono_humano": "+49 1"},
         "lente": "EMEA", "tier": "Gold", "capacidades": ["M1", "M3"]}))
    alta_ok = (proys[0]["cliente_id"] == c["id"] and c["marca"] == "ZENKAI")
    print(f"   [{'ok' if alta_ok else 'FALLA'}] alta compuesta: cliente {c['id']} ({c['marca']}) <- proyecto {proys[0]['id']}")
    d_s = delivery({"prospecto": {"nombre": "S", "vertical": "dental", "telefono_humano": "1"},
                    "lente": "Americas", "tier": "Starter", "capacidades": ["M1"]})
    d_g = delivery({"prospecto": {"nombre": "G", "vertical": "dental", "telefono_humano": "1"},
                    "lente": "EMEA", "tier": "Gold", "capacidades": ["M1"]})
    del_ok = (d_s["plan"] == "basic" and d_s["payload"] and d_g["plan"] == registro.PENDIENTE)
    print(f"   [{'ok' if del_ok else 'FALLA'}] entrega: Starter={d_s['plan']} (payload sí) · Gold={d_g['plan']} (no inventa)")
    print("ORACLE:", "PASA" if (allok and q_ok and alta_ok and del_ok) else "FALLA")


DEMO = {
    "prospecto": {"nombre": "Klinik Berlin Mitte", "vertical": "dental",
                  "telefono_humano": "+49 30 555 0100", "ciudad": "Berlin"},
    "lente": "EMEA", "tier": "Gold", "capacidades": ["M1", "M2", "M3"],
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["oracle", "dry-run", "execute"])
    ap.add_argument("--json", help="onboarding {prospecto, lente, tier, capacidades[]} en JSON")
    ap.add_argument("--confirm", action="store_true", help="OK humano para el alta")
    a = ap.parse_args()
    if a.accion == "oracle":
        oracle()
    else:
        inp = json.loads(a.json) if a.json else DEMO
        if a.accion == "dry-run":
            dry_run(inp)
        elif a.accion == "execute":
            execute(inp, a.confirm)
