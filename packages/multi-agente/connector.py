#!/usr/bin/env python3
"""
Capacidad multi-agente (M3) — Xe compone N agentes por cliente sobre el conector clinics.

Gap de Gold: clinics es multi-tenant pero entrega 1 agente/cliente. Esta capacidad
lleva de 1->N agentes bajo un mismo cliente, SIN reimplementar clinics (lo compone) y
SIN tocar el producto agente-clinicas.

Cumple el contrato de capacidades: inputs · dry_run · execute · oracle.

Reglas duras (heredadas, no negociables):
  - No reimplementa la verdad de clinics: importa y reutiliza su validate/build_payload (oraculo unico).
  - Lote atomico: si UN agente es invalido, se bloquea el lote entero (GUARDA-003: no invencion parcial).
  - Colision de sesion: dos agentes con el mismo slug de nombre -> BLOQUEO (cada tenant exige sesion unica).
  - execute() NO corre sin OK humano (--confirm) ni sin env CLINICS_REPO (GUARDA-001, GUARDA-005).

Uso:
  python3 connector.py dry-run                  # demo
  python3 connector.py dry-run --json '{...}'
  python3 connector.py oracle
  python3 connector.py execute --json '{...}'   # exige --confirm + CLINICS_REPO
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

REQUERIDOS_LOTE = ["cliente", "agentes"]


def validate_lote(req: dict):
    """inputs del lote: cliente + lista no vacia de agentes; cada agente valido por clinics; sesiones unicas."""
    faltan = [c for c in REQUERIDOS_LOTE if not req.get(c)]
    if faltan:
        return False, f"[BLOQUEO GUARDA-003] faltan requeridos del lote: {faltan} -> pedir al humano."
    agentes = req["agentes"]
    if not isinstance(agentes, list) or len(agentes) == 0:
        return False, "[BLOQUEO GUARDA-003] 'agentes' debe ser una lista no vacia."
    # cada agente: valido por la verdad de clinics (lote atomico, no invencion parcial)
    for i, ag in enumerate(agentes):
        ok, msg = clinics.validate(ag)
        if not ok:
            return False, f"[BLOQUEO] agente #{i} ('{ag.get('nombre','?')}'): {msg}"
    # sesiones unicas: cada tenant exige slug propio (verdad de agente-clinicas)
    slugs = [clinics.slug(ag["nombre"]) for ag in agentes]
    dups = sorted({s for s in slugs if slugs.count(s) > 1})
    if dups:
        return False, f"[BLOQUEO] colision de sesion (slugs repetidos): {dups} -> renombrar agentes."
    return True, "ok"


def build_lote(req: dict):
    """Compone N items de clinics (reusa su build_payload). Cada agente hereda region del lote si no trae la suya."""
    region = req.get("region", "LATAM")
    items = []
    for ag in req["agentes"]:
        ag2 = dict(ag)
        ag2.setdefault("region", region)
        payload = clinics.build_payload(ag2)
        items.append({
            "session_id": clinics.slug(ag["nombre"]),
            "rol": ag.get("rol"),
            "payload": payload,
            "cmd": clinics.cmd_for(payload),
        })
    return items


def dry_run(req: dict):
    ok, msg = validate_lote(req)
    print(f"[inputs] {msg}")
    if not ok:
        return
    region = req.get("region", "LATAM")
    items = build_lote(req)
    print(f"[cliente] {req['cliente']}  ·  {len(items)} agentes  ·  region={region}")
    print(f"[quote ] Starter {region} = {clinics.quote(region)} por agente "
          f"(bundle Gold se cotiza aparte -> hueco #17, no se inventa)")
    for item in items:
        rol = f" ({item['rol']})" if item["rol"] else ""
        print(f"  - agente '{item['session_id']}'{rol}: {json.dumps(item['payload'], ensure_ascii=False)}")
    print("[execute] STOP — GUARDA-001: no se crea ni se cobra sin OK humano. Lote atomico.")
    print("   Comandos que se correrian (en agente-clinicas):")
    for item in items:
        print("   " + item["cmd"])


def execute(req: dict, confirm: bool):
    ok, msg = validate_lote(req)
    if not ok:
        print(msg)
        sys.exit(1)
    repo = os.environ.get("CLINICS_REPO")  # GUARDA-005: ruta por env, no hardcode
    items = build_lote(req)
    if not confirm or not repo:
        print(f"[execute] NO ejecutado (GUARDA-001). Lote atomico de {len(items)} agentes.")
        if not repo:
            print("   Falta env CLINICS_REPO (ruta a agente-clinicas).")
        if not confirm:
            print("   Falta --confirm (OK humano explicito).")
        print("   Comandos para correrlos TU:")
        for item in items:
            print(f"   cd {repo or '<CLINICS_REPO>'} && {item['cmd']}")
        return
    # Con OK humano + repo: delega N veces al producto externo (no lo reimplementa)
    import subprocess
    print(f"[execute] OK humano. Delegando {len(items)} agentes a {repo} ...")
    for item in items:
        print(f"  -> {item['session_id']}")
        subprocess.run(item["cmd"], shell=True, cwd=repo, check=False)


def oracle():
    """Verifica la logica NUEVA de la capa (la de clinics ya tiene su propio oraculo)."""
    casos = [
        # lote valido de 2 agentes distintos
        ({"cliente": "Grupo Vet", "agentes": [
            {"nombre": "Sede Norte", "vertical": "veterinaria", "telefono_humano": "300"},
            {"nombre": "Sede Sur",   "vertical": "veterinaria", "telefono_humano": "301"}]}, True),
        # lote vacio -> bloqueo
        ({"cliente": "X", "agentes": []}, False),
        # falta cliente -> bloqueo
        ({"agentes": [{"nombre": "A", "vertical": "dental", "telefono_humano": "1"}]}, False),
        # un agente invalido contamina el lote (atomicidad)
        ({"cliente": "X", "agentes": [
            {"nombre": "Bueno", "vertical": "dental",   "telefono_humano": "1"},
            {"nombre": "Malo",  "vertical": "barberia", "telefono_humano": "2"}]}, False),
        # colision de sesion (mismo slug)
        ({"cliente": "X", "agentes": [
            {"nombre": "Clinica Uno", "vertical": "dental", "telefono_humano": "1"},
            {"nombre": "clinica uno", "vertical": "dental", "telefono_humano": "2"}]}, False),
    ]
    allok = True
    for req, esperado in casos:
        got = validate_lote(req)[0]
        estado = "ok" if got == esperado else "FALLA"
        if got != esperado:
            allok = False
        print(f"   [{estado}] cliente={req.get('cliente','<falta>')} n={len(req.get('agentes', []))} "
              f"-> valido={got} (esperado {esperado})")
    # compone N payloads bien formados, con sesiones unicas y plan correcto
    req = {"cliente": "G", "agentes": [
        {"nombre": "Uno", "vertical": "dental",   "telefono_humano": "+1 (1)"},
        {"nombre": "Dos", "vertical": "estetica", "telefono_humano": "+1 (2)"}]}
    items = build_lote(req)
    chk = (len(items) == 2
           and len({i["session_id"] for i in items}) == 2
           and all(i["payload"]["plan"] == clinics.PLAN_STARTER for i in items))
    print(f"   [{'ok' if chk else 'FALLA'}] compone {len(items)} payloads, sesiones unicas, plan={clinics.PLAN_STARTER}")
    print("ORACLE:", "PASA" if (allok and chk) else "FALLA")


DEMO = {"cliente": "Grupo Dental Sonrisa", "region": "US", "agentes": [
    {"nombre": "Sonrisa Centro", "vertical": "dental", "telefono_humano": "+1 (512) 555-0001",
     "rol": "agendamiento", "ciudad": "Austin"},
    {"nombre": "Sonrisa Norte", "vertical": "dental", "telefono_humano": "+1 (512) 555-0002",
     "rol": "ventas", "ciudad": "Austin"}]}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["dry-run", "execute", "oracle"])
    ap.add_argument("--json", help="lote de cliente+agentes en JSON")
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
