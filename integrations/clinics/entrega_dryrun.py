#!/usr/bin/env python3
"""
entrega_dryrun — el e2e de Fase D en DRY-RUN: ata (producto traído por repo_fetch) → CLINICS_REPO →
comando de entrega `nueva_clinica`, para un cliente Starter, SIN ejecutar y SIN tocar Supabase.

Reusa integrations/clinics (payload + comando, espejo fiel de nueva_clinica.ts) — no reimplementa.
Regla dura: solo Starter→basic está firmado (DEC-009). Otro tier → PENDIENTE-#17, NO se inventa.
GUARDA-001: el INSERT en Supabase + el envío al cliente NUNCA ocurren acá (visto humano).

Uso:
  python3 entrega_dryrun.py oracle
  python3 entrega_dryrun.py dry-run                      # demo Starter
  CLINICS_REPO=/tmp/clinics-checkout python3 entrega_dryrun.py dry-run --json '{...}'
"""
import argparse, importlib.util, json, os, pathlib, sys

_HERE = pathlib.Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


clinics = _load("clinics_connector", _HERE / "connector.py")

PLAN_FIRMADO = {"Starter": "basic"}     # DEC-009 (lo único firmado)
PENDIENTE = "PENDIENTE-#17"


def resolve_repo() -> str:
    """CLINICS_REPO = ruta local del checkout (lo pone repo_fetch en la VPS). Placeholder si falta."""
    return os.environ.get("CLINICS_REPO") or "<CLINICS_REPO>"


def build_entrega(cliente: dict, tier: str):
    """Devuelve (plan, comando|None, error|None). Nada se ejecuta."""
    if tier not in PLAN_FIRMADO:
        return PENDIENTE, None, None  # no firmado → no se fabrica (GUARDA-003)
    ok, msg = clinics.validate(cliente)
    if not ok:
        return None, None, f"[BLOQUEO] discovery: {msg}"
    payload = clinics.build_payload(cliente)
    repo = resolve_repo()
    cmd = f"cd {repo} && {clinics.cmd_for(payload)}"
    return PLAN_FIRMADO[tier], cmd, None


def dry_run(cliente: dict, tier: str):
    plan, cmd, err = build_entrega(cliente, tier)
    if err:
        print(err); return
    print(f"[cliente] {cliente.get('nombre')} · vertical={cliente.get('vertical')} · tier={tier}")
    print(f"[plan de entrega] {plan}")
    if cmd:
        print(f"[comando que correría (NO ejecutado)]:\n   {cmd}")
    else:
        print(f"[entrega] {PENDIENTE} — tier no firmado; NO se arma comando (no se inventa).")
    print("[STOP GUARDA-001] el INSERT en Supabase y el envío al cliente = VISTO HUMANO. Aquí nada se ejecuta.")


def oracle():
    ok = True

    def check(name, cond):
        nonlocal ok
        if not cond: ok = False
        print(f"   [{'ok' if cond else 'FALLA'}] {name}")

    starter = {"nombre": "Clinica Dental Sonrisa", "vertical": "dental", "telefono_humano": "+57 300 123 4567"}
    os.environ["CLINICS_REPO"] = "/tmp/clinics-checkout"  # simula el checkout traído por repo_fetch
    plan_s, cmd_s, err_s = build_entrega(starter, "Starter")
    check("Starter → plan basic", plan_s == "basic")
    check("Starter → comando apunta a nueva_clinica en el checkout", cmd_s and "cd /tmp/clinics-checkout && npx tsx scripts/nueva_clinica.ts" in cmd_s and not err_s)
    check("Starter → comando NO ejecuta (solo string)", isinstance(cmd_s, str))

    plan_g, cmd_g, _ = build_entrega(starter, "Gold")
    check("Gold → PENDIENTE-#17 (no inventa)", plan_g == PENDIENTE and cmd_g is None)

    bad = {"nombre": "X", "vertical": "loquesea", "telefono_humano": "1"}  # vertical fuera de whitelist
    _, _, err_b = build_entrega(bad, "Starter")
    check("discovery inválido → BLOQUEO", bool(err_b))

    del os.environ["CLINICS_REPO"]
    plan_np, cmd_np, _ = build_entrega(starter, "Starter")
    check("sin CLINICS_REPO → comando usa placeholder <CLINICS_REPO>", "<CLINICS_REPO>" in cmd_np)
    print("ORACLE:", "PASA" if ok else "FALLA")


DEMO = {"nombre": "Clinica Dental Sonrisa", "vertical": "dental",
        "telefono_humano": "+57 300 123 4567", "ciudad": "Pereira"}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["oracle", "dry-run"])
    ap.add_argument("--json", help="cliente discovery en JSON")
    ap.add_argument("--tier", default="Starter")
    a = ap.parse_args()
    if a.accion == "oracle":
        oracle()
    else:
        cli = json.loads(a.json) if a.json else DEMO
        dry_run(cli, a.tier)
