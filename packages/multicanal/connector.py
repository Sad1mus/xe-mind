#!/usr/bin/env python3
"""
Capacidad multicanal (M4) — Xe ata N canales a UN mismo agente sobre el conector clinics.

Gap de Gold: clinics entrega 1 canal/agente (WhatsApp). Esta capacidad lleva de 1->N canales
sobre el MISMO cerebro, SIN reimplementar clinics (lo compone) y SIN tocar agente-clinicas.
Simetrica a M3: M3 compone N agentes por cliente; M4 compone N canales por agente.

Cumple el contrato de capacidades: inputs · dry_run · execute · oracle.

Reglas duras (heredadas, no negociables):
  - No reimplementa la verdad de clinics: el cerebro (validate/build_payload/slug) es suyo.
  - Juego atomico: si UN canal es invalido, se bloquea el juego entero (GUARDA-003).
  - Un canal por tipo: dos bindings del mismo canal -> BLOQUEO (un cerebro, un canal de cada).
  - Credencial ausente NO se finge: el canal se marca BLOQUEADO y se nombra el env que falta
    (GUARDA-003). La licencia Meta esta EN TRAMITE: cloud_api/instagram_dm/messenger no
    ejecutan hasta que exista su env. dry_run si corre: valida la forma sin credenciales.
  - execute() NO corre sin OK humano (--confirm) ni sin los env de cada canal (GUARDA-001/005).

Canales (decididos 2026-07-16, CLAUDE.md 9.6):
  web · whatsapp[baileys|cloud_api] · instagram_dm · messenger

Uso:
  python3 connector.py dry-run                  # demo
  python3 connector.py dry-run --json '{...}'
  python3 connector.py oracle
  python3 connector.py execute --json '{...}'   # exige --confirm + env por canal
"""
import argparse, importlib.util, json, os, pathlib, sys

# --- Importa la verdad de clinics (no la reimplementa) ---
_CLINICS_PATH = pathlib.Path(__file__).resolve().parents[2] / "integrations" / "clinics" / "connector.py"


def _load_clinics():
    spec = importlib.util.spec_from_file_location("clinics_connector", _CLINICS_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


clinics = _load_clinics()

REQUERIDOS_JUEGO = ["cliente", "agente", "canales"]
CANALES = ["web", "whatsapp", "instagram_dm", "messenger"]
TRANSPORTES_WHATSAPP = ["baileys", "cloud_api"]

# Que env exige cada canal para ejecutar (GUARDA-005: por env, nunca hardcode).
# 'web' es capacidad propia (storefront): no exige credencial externa.
ENV_META = "META_ACCESS_TOKEN"


def env_requerido(canal: str, transporte: str = None):
    if canal == "web":
        return []
    if canal == "whatsapp":
        if transporte == "baileys":
            return ["CLINICS_REPO"]          # reusa el execute del producto
        return [ENV_META, "WHATSAPP_PHONE_NUMBER_ID"]
    if canal == "instagram_dm":
        return [ENV_META, "IG_BUSINESS_ACCOUNT_ID"]
    if canal == "messenger":
        return [ENV_META, "FB_PAGE_ID"]
    return []


def env_faltante(canal: str, transporte: str = None):
    return [e for e in env_requerido(canal, transporte) if not os.environ.get(e)]


def validate_juego(req: dict):
    """inputs: cliente + agente (valido por clinics) + lista no vacia de canales sin repetir."""
    faltan = [c for c in REQUERIDOS_JUEGO if not req.get(c)]
    if faltan:
        return False, f"[BLOQUEO GUARDA-003] faltan requeridos del juego: {faltan} -> pedir al humano."
    ok, msg = clinics.validate(req["agente"])
    if not ok:
        return False, f"[BLOQUEO] agente '{req['agente'].get('nombre','?')}': {msg}"
    canales = req["canales"]
    if not isinstance(canales, list) or len(canales) == 0:
        return False, "[BLOQUEO GUARDA-003] 'canales' debe ser una lista no vacia."
    vistos = []
    for i, c in enumerate(canales):
        if not isinstance(c, dict) or not c.get("canal"):
            return False, f"[BLOQUEO GUARDA-003] canal #{i}: falta la clave 'canal'."
        nombre = c["canal"]
        if nombre not in CANALES:
            return False, f"[BLOQUEO] canal #{i}: '{nombre}' no existe. Validos: {CANALES}."
        if nombre == "whatsapp":
            t = c.get("transporte")
            if t not in TRANSPORTES_WHATSAPP:
                return False, (f"[BLOQUEO GUARDA-003] whatsapp exige 'transporte' en {TRANSPORTES_WHATSAPP} "
                               f"(convivencia decidida 2026-07-16) -> recibido: {t!r}.")
        vistos.append(nombre)
    dups = sorted({c for c in vistos if vistos.count(c) > 1})
    if dups:
        return False, f"[BLOQUEO] canal repetido: {dups} -> un cerebro atiende un canal de cada tipo."
    return True, "ok"


def build_juego(req: dict):
    """Compone el cerebro (verdad de clinics) + un binding por canal. El agente hereda region del juego."""
    region = req.get("region", "LATAM")
    ag = dict(req["agente"])
    ag.setdefault("region", region)
    payload = clinics.build_payload(ag)
    cerebro = {
        "session_id": clinics.slug(req["agente"]["nombre"]),
        "payload": payload,
        "cmd": clinics.cmd_for(payload),
    }
    bindings = []
    for c in req["canales"]:
        canal = c["canal"]
        transporte = c.get("transporte") if canal == "whatsapp" else None
        faltan = env_faltante(canal, transporte)
        bindings.append({
            "canal": canal,
            "transporte": transporte,
            "session_id": cerebro["session_id"],   # un solo cerebro para todos
            "env_requerido": env_requerido(canal, transporte),
            "env_faltante": faltan,
            "listo": len(faltan) == 0,
        })
    return cerebro, bindings


def _etiqueta(b: dict):
    return f"{b['canal']}/{b['transporte']}" if b["transporte"] else b["canal"]


def dry_run(req: dict):
    ok, msg = validate_juego(req)
    print(f"[inputs] {msg}")
    if not ok:
        return
    region = req.get("region", "LATAM")
    cerebro, bindings = build_juego(req)
    listos = [b for b in bindings if b["listo"]]
    print(f"[cliente] {req['cliente']}  ·  agente '{cerebro['session_id']}'  ·  "
          f"{len(bindings)} canales  ·  region={region}")
    print(f"[cerebro] {json.dumps(cerebro['payload'], ensure_ascii=False)}")
    print(f"[quote ] Starter {region} = {clinics.quote(region)} por agente "
          f"(bundle Gold multicanal se cotiza aparte -> hueco #17, no se inventa)")
    for b in bindings:
        if b["listo"]:
            print(f"  - canal '{_etiqueta(b)}' -> cerebro '{b['session_id']}'  [listo]")
        else:
            print(f"  - canal '{_etiqueta(b)}' -> cerebro '{b['session_id']}'  "
                  f"[BLOQUEADO] falta env: {b['env_faltante']}")
    print(f"[estado ] {len(listos)}/{len(bindings)} canales listos.")
    print("[execute] STOP — GUARDA-001: no se ata nada sin OK humano. Juego atomico.")
    if len(listos) < len(bindings):
        print("   Licencia Meta EN TRAMITE: los canales bloqueados no se simulan (GUARDA-003).")


def execute(req: dict, confirm: bool):
    ok, msg = validate_juego(req)
    if not ok:
        print(msg)
        sys.exit(1)
    cerebro, bindings = build_juego(req)
    faltan_env = sorted({e for b in bindings for e in b["env_faltante"]})
    if not confirm or faltan_env:
        print(f"[execute] NO ejecutado (GUARDA-001). Juego atomico de {len(bindings)} canales.")
        if faltan_env:
            print(f"   Falta env: {faltan_env}")
            for b in bindings:
                if not b["listo"]:
                    print(f"     - '{_etiqueta(b)}' exige {b['env_requerido']}")
        if not confirm:
            print("   Falta --confirm (OK humano explicito).")
        print(f"   Cerebro que se crearia (en agente-clinicas): {cerebro['cmd']}")
        return
    # Con OK humano + env completo: ata cada canal al mismo cerebro.
    print(f"[execute] OK humano. Atando {len(bindings)} canales al cerebro '{cerebro['session_id']}' ...")
    for b in bindings:
        print(f"  -> {_etiqueta(b)}")
    print("[PENDIENTE-M4-wiring] el atado real por canal se cablea cuando exista la credencial de cada uno; "
          "no se inventa la llamada a un API que no se ha probado (GUARDA-003).")


def oracle():
    """Verifica la logica NUEVA de la capa (la de clinics ya tiene su propio oraculo)."""
    AG = {"nombre": "Sede Norte", "vertical": "veterinaria", "telefono_humano": "300"}
    casos = [
        # juego valido: 3 canales distintos, whatsapp con transporte
        ({"cliente": "Grupo Vet", "agente": AG, "canales": [
            {"canal": "web"}, {"canal": "whatsapp", "transporte": "cloud_api"},
            {"canal": "instagram_dm"}]}, True),
        # canales vacio -> bloqueo
        ({"cliente": "X", "agente": AG, "canales": []}, False),
        # falta cliente -> bloqueo
        ({"agente": AG, "canales": [{"canal": "web"}]}, False),
        # canal inexistente contamina el juego (atomicidad)
        ({"cliente": "X", "agente": AG, "canales": [
            {"canal": "web"}, {"canal": "tiktok"}]}, False),
        # whatsapp sin transporte -> bloqueo (convivencia exige declararlo)
        ({"cliente": "X", "agente": AG, "canales": [{"canal": "whatsapp"}]}, False),
        # whatsapp con transporte invalido -> bloqueo
        ({"cliente": "X", "agente": AG, "canales": [
            {"canal": "whatsapp", "transporte": "telegram"}]}, False),
        # canal repetido -> bloqueo
        ({"cliente": "X", "agente": AG, "canales": [
            {"canal": "web"}, {"canal": "web"}]}, False),
        # agente invalido contamina el juego
        ({"cliente": "X", "agente": {"nombre": "Malo", "vertical": "barberia", "telefono_humano": "1"},
          "canales": [{"canal": "web"}]}, False),
    ]
    allok = True
    for req, esperado in casos:
        got = validate_juego(req)[0]
        estado = "ok" if got == esperado else "FALLA"
        if got != esperado:
            allok = False
        print(f"   [{estado}] cliente={req.get('cliente','<falta>')} n={len(req.get('canales', []))} "
              f"-> valido={got} (esperado {esperado})")

    # compone N bindings sobre UN solo cerebro (la esencia de M4)
    req = {"cliente": "G", "agente": AG, "canales": [
        {"canal": "web"}, {"canal": "whatsapp", "transporte": "baileys"}, {"canal": "messenger"}]}
    cerebro, bindings = build_juego(req)
    un_cerebro = len({b["session_id"] for b in bindings}) == 1
    chk = (len(bindings) == 3 and un_cerebro
           and bindings[0]["session_id"] == cerebro["session_id"]
           and cerebro["payload"]["plan"] == clinics.PLAN_STARTER)
    print(f"   [{'ok' if chk else 'FALLA'}] compone {len(bindings)} canales sobre "
          f"{len({b['session_id'] for b in bindings})} cerebro, plan={clinics.PLAN_STARTER}")

    # 'web' no exige credencial; los canales Meta si -> se marcan, no se fingen (GUARDA-003)
    env_ok = (env_requerido("web") == []
              and ENV_META in env_requerido("instagram_dm")
              and ENV_META in env_requerido("messenger")
              and ENV_META in env_requerido("whatsapp", "cloud_api")
              and env_requerido("whatsapp", "baileys") == ["CLINICS_REPO"])
    print(f"   [{'ok' if env_ok else 'FALLA'}] env por canal: web=libre · baileys=CLINICS_REPO · "
          f"cloud_api/instagram_dm/messenger exigen {ENV_META}")

    print("ORACLE:", "PASA" if (allok and chk and env_ok) else "FALLA")


DEMO = {"cliente": "Grupo Dental Sonrisa", "region": "US",
        "agente": {"nombre": "Sonrisa Centro", "vertical": "dental",
                   "telefono_humano": "+1 (512) 555-0001", "ciudad": "Austin"},
        "canales": [{"canal": "web"},
                    {"canal": "whatsapp", "transporte": "cloud_api"},
                    {"canal": "instagram_dm"},
                    {"canal": "messenger"}]}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["dry-run", "execute", "oracle"])
    ap.add_argument("--json", help="juego de cliente+agente+canales en JSON")
    ap.add_argument("--confirm", action="store_true", help="OK humano para execute")
    a = ap.parse_args()
    if a.accion == "oracle":
        oracle()
    else:
        req = json.loads(a.json) if a.json else DEMO
        if a.accion == "dry-run":
            dry_run(req)
        elif a.accion == "execute":
            execute(req, a.confirm)
