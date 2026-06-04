#!/usr/bin/env python3
"""
Conector clinics — Xe orquesta `agente-clinicas` SIN tocarlo ni moverlo.

Cumple el contrato de capacidades: inputs · dry_run · execute · oracle.
Modelado fiel a la validación real de scripts/nueva_clinica.ts.

Reglas duras:
  - No hardcodea cuentas: la ruta al producto sale de env CLINICS_REPO (GUARDA-005).
  - execute() NO escribe sin OK humano explícito (--confirm) (GUARDA-001).
  - Si falta un campo requerido -> bloquea, no inventa (GUARDA-003).

Uso:
  python3 connector.py dry-run                 # demo
  python3 connector.py dry-run --json '{...}'
  python3 connector.py oracle
  python3 connector.py execute --json '{...}'   # exige --confirm + CLINICS_REPO
"""
import argparse, json, os, re, shlex, sys, unicodedata

# --- Espejo de la verdad de nueva_clinica.ts (oráculo) ---
REQUERIDOS = ["nombre", "vertical", "telefono_humano"]
VERTICALES = ["veterinaria", "dental", "estetica"]
PLAN_STARTER = "basic"  # DEC-009 (Starter -> basic)

# DEC-006: precio Starter PUBLICADO (lo no publicado NO se inventa)
STARTER_PRICE = {
    "US": "USD 399/mo",
    "EU": "CONFIRMAR (no publicado; FX en propuesta)",
    "LATAM": "CONFIRMAR (no publicado; FX en propuesta)",
}

def slug(nombre: str) -> str:
    s = unicodedata.normalize("NFD", nombre.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"^-|-$", "", s)

def validate(cli: dict):
    """inputs: requeridos + whitelist de vertical. Bloquea, no inventa."""
    faltan = [c for c in REQUERIDOS if not cli.get(c)]
    if faltan:
        return False, f"[BLOQUEO GUARDA-003] faltan requeridos: {faltan} -> pedir al humano."
    if cli["vertical"] not in VERTICALES:
        return False, f"[BLOQUEO] vertical inválido '{cli['vertical']}'. Usa: {VERTICALES}"
    return True, "ok"

def quote(region: str) -> str:
    return STARTER_PRICE.get(region, "CONFIRMAR (región desconocida)")

def build_payload(cli: dict) -> dict:
    """Payload de entrada para nueva_clinica.ts (él rellena sus defaults)."""
    p = {
        "nombre": cli["nombre"],
        "vertical": cli["vertical"],
        "telefono_humano": re.sub(r"\D", "", cli["telefono_humano"]),
        "plan": PLAN_STARTER,
    }
    for k in ("ciudad", "direccion", "servicios", "horario", "medios_pago",
              "info_extra", "valor_cita_promedio", "google_review_url"):
        if cli.get(k) is not None:
            p[k] = cli[k]
    return p

def cmd_for(payload: dict) -> str:
    return f"npx tsx scripts/nueva_clinica.ts --json {shlex.quote(json.dumps(payload, ensure_ascii=False))}"

def dry_run(cli: dict):
    ok, msg = validate(cli)
    print(f"[inputs] {msg}")
    if not ok:
        return
    print(f"[quote ] Starter {cli.get('region','LATAM')} = {quote(cli.get('region','LATAM'))}")
    payload = build_payload(cli)
    print(f"[session_id preview] {slug(cli['nombre'])}")
    print("[payload] (NO ejecutado):")
    print("   " + json.dumps(payload, ensure_ascii=False))
    print("[execute] STOP — GUARDA-001: no se crea ni se cobra sin OK humano.")
    print("   Comando que se correría (en agente-clinicas):")
    print("   " + cmd_for(payload))

def execute(cli: dict, confirm: bool):
    ok, msg = validate(cli)
    if not ok:
        print(msg); sys.exit(1)
    repo = os.environ.get("CLINICS_REPO")  # GUARDA-005: ruta por env, no hardcode
    payload = build_payload(cli)
    if not confirm or not repo:
        print("[execute] NO ejecutado (GUARDA-001).")
        if not repo: print("   Falta env CLINICS_REPO (ruta a agente-clinicas).")
        if not confirm: print("   Falta --confirm (OK humano explícito).")
        print("   Comando para correrlo TÚ:")
        print(f"   cd {repo or '<CLINICS_REPO>'} && {cmd_for(payload)}")
        return
    # Con OK humano + repo: delega al producto externo (no lo reimplementa)
    import subprocess
    print(f"[execute] OK humano. Delegando a {repo} ...")
    subprocess.run(cmd_for(payload), shell=True, cwd=repo, check=False)

def oracle():
    """Verifica que el conector respeta la verdad de nueva_clinica.ts."""
    casos = [
        ({"nombre": "X", "vertical": "veterinaria", "telefono_humano": "300"}, True),
        ({"nombre": "X", "vertical": "veterinaria"}, False),            # falta telefono
        ({"nombre": "X", "vertical": "barberia", "telefono_humano": "1"}, False),  # vertical inválido
    ]
    allok = True
    for cli, esperado in casos:
        got = validate(cli)[0]
        estado = "ok" if got == esperado else "FALLA"
        if got != esperado: allok = False
        print(f"   [{estado}] {cli} -> válido={got} (esperado {esperado})")
    p = build_payload({"nombre": "Sunrise", "vertical": "veterinaria", "telefono_humano": "+1 512 555"})
    chk = p["plan"] == PLAN_STARTER and p["telefono_humano"] == "1512555"
    print(f"   [{'ok' if chk else 'FALLA'}] payload: plan={p['plan']}, telefono limpio={p['telefono_humano']}")
    print("ORACLE:", "PASA" if (allok and chk) else "FALLA")

DEMO = {"region": "US", "nombre": "Sunrise Vet Clinic", "vertical": "veterinaria",
        "telefono_humano": "+1 (512) 555-0123", "ciudad": "Austin",
        "servicios": ["Checkup", "Vaccines"], "valor_cita_promedio": 90}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["dry-run", "execute", "oracle"])
    ap.add_argument("--json", help="cliente en JSON")
    ap.add_argument("--confirm", action="store_true", help="OK humano para execute")
    a = ap.parse_args()
    cli = json.loads(a.json) if a.json else DEMO
    if a.accion == "dry-run": dry_run(cli)
    elif a.accion == "execute": execute(cli, a.confirm)
    elif a.accion == "oracle": oracle()
