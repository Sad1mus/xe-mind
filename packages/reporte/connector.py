#!/usr/bin/env python3
"""
Capacidad reporte (M6) — cockpit de cartera: Xe ve el estado de la agencia leyendo la
"verdad exacta" del registro (CLAUDE.md §3.1). Agrega clientes/proyectos por lente/tier/estado.

Compone packages/registro (su schema y su DB), NO lo reimplementa.

Reglas duras:
  - GUARDA-001: execute() persiste un snapshot del reporte; NUNCA lo envía al cliente (eso es humano).
  - GUARDA-003: las métricas de ROI (ingresos/citas/conversión) requieren datos de producto + KPIs
    firmados -> salen como 'PENDIENTE-#23'. No se inventan.
  - GUARDA-002: el reporte agrega por region/lente; no extrae el dato regulado, solo cuenta.
  - GUARDA-005: la DB sale de env REGISTRO_DB; el snapshot va a env REPORTE_OUT. Sin hardcode.

Uso:
  python3 connector.py oracle
  REGISTRO_DB=/tmp/reg.db python3 connector.py dry-run
  REGISTRO_DB=/tmp/reg.db python3 connector.py dry-run --json '{"periodo":"2026-W24","lente":"EMEA"}'
  REGISTRO_DB=/tmp/reg.db REPORTE_OUT=/tmp/rep.md python3 connector.py execute --confirm
"""
import argparse, importlib.util, json, os, pathlib, sqlite3, sys

_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


registro = _load("registro_connector", "packages/registro/connector.py")

ROI_PENDIENTE = {"ingresos": "PENDIENTE-#23", "citas": "PENDIENTE-#23", "conversion": "PENDIENTE-#23"}


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(registro.SCHEMA_PATH.read_text(encoding="utf-8"))  # idempotente; reusa la verdad del registro
    return conn


def aggregate(conn: sqlite3.Connection, periodo: str, lente=None) -> dict:
    if lente is not None and lente not in registro.LENTES:
        raise ValueError(f"[BLOQUEO] lente inválida '{lente}'. Usa: {registro.LENTES}")
    cw = " WHERE lente = ?" if lente else ""
    cp = (lente,) if lente else ()

    def grp(col):
        return dict(conn.execute(f"SELECT {col}, COUNT(*) FROM clientes{cw} GROUP BY {col}", cp).fetchall())

    cli_total = conn.execute(f"SELECT COUNT(*) FROM clientes{cw}", cp).fetchone()[0]
    pbase = "FROM proyectos p"
    pp = ()
    if lente:
        pbase += " JOIN clientes c ON c.id = p.cliente_id WHERE c.lente = ?"
        pp = (lente,)
    pro_total = conn.execute(f"SELECT COUNT(*) {pbase}", pp).fetchone()[0]
    pro_estado = dict(conn.execute(f"SELECT p.estado, COUNT(*) {pbase} GROUP BY p.estado", pp).fetchall())
    pro_plan = dict(conn.execute(f"SELECT p.plan_entrega, COUNT(*) {pbase} GROUP BY p.plan_entrega", pp).fetchall())

    return {
        "periodo": periodo,
        "lente_filtro": lente or "todas",
        "clientes": {"total": cli_total, "por_lente": grp("lente"),
                     "por_tier": grp("tier"), "por_estado": grp("estado")},
        "proyectos": {"total": pro_total, "por_estado": pro_estado, "por_plan_entrega": pro_plan},
        "roi": dict(ROI_PENDIENTE),
    }


def render(rep: dict) -> str:
    L = [f"# Reporte de cartera — {rep['periodo']} (lente: {rep['lente_filtro']})", ""]
    c = rep["clientes"]
    L.append(f"## Clientes — total {c['total']}")
    L.append(f"- por lente: {c['por_lente']}")
    L.append(f"- por tier: {c['por_tier']}")
    L.append(f"- por estado: {c['por_estado']}")
    p = rep["proyectos"]
    L.append(f"## Proyectos — total {p['total']}")
    L.append(f"- por estado: {p['por_estado']}")
    L.append(f"- por plan_entrega: {p['por_plan_entrega']}")
    L.append("## ROI (requiere datos de producto + KPIs firmados)")
    L.append(f"- {rep['roi']}  ⚠️ no se inventa (hueco #23)")
    return "\n".join(L)


# ---------- contrato: dry_run ----------
def dry_run(inp: dict):
    db = os.environ.get("REGISTRO_DB")
    if not db:
        print("[inputs] [BLOQUEO GUARDA-005] falta env REGISTRO_DB (DB del registro).")
        return
    periodo = inp.get("periodo", "sin-periodo")
    lente = inp.get("lente")
    try:
        rep = aggregate(_connect(db), periodo, lente)
    except ValueError as e:
        print(f"[inputs] {e}")
        return
    print("[inputs] ok (lectura del registro, sin escribir ni enviar)")
    print(render(rep))
    print("[execute] STOP — GUARDA-001: persistir el snapshot exige --confirm; ENVIAR al cliente es paso humano.")


# ---------- contrato: execute ----------
def execute(inp: dict, confirm: bool):
    db = os.environ.get("REGISTRO_DB")
    out = os.environ.get("REPORTE_OUT")
    if not db:
        print("[execute] [BLOQUEO GUARDA-005] falta env REGISTRO_DB.")
        sys.exit(1)
    periodo = inp.get("periodo", "sin-periodo")
    lente = inp.get("lente")
    try:
        rep = aggregate(_connect(db), periodo, lente)
    except ValueError as e:
        print(e)
        sys.exit(1)
    if not confirm or not out:
        print("[execute] NO persistido (GUARDA-001).")
        if not out:
            print("   Falta env REPORTE_OUT (ruta del snapshot).")
        if not confirm:
            print("   Falta --confirm (OK humano explícito).")
        return
    pathlib.Path(out).write_text(render(rep) + "\n", encoding="utf-8")
    print(f"[execute] OK humano. Snapshot persistido en {out} (NO enviado al cliente — GUARDA-001).")


# ---------- contrato: oracle ----------
def oracle():
    conn = _connect(":memory:")
    fixtures_cli = [
        ("acme-eu", "ACME EU", "EMEA", "ZENKAI", "Gold", "UE", "activo"),
        ("vet-usa", "Vet USA", "Americas", "Americas-por-definir", "Starter", "local", "onboarding"),
        ("spa-eu", "Spa EU", "EMEA", "ZENKAI", "Silver", "UE", "prospecto"),
    ]
    conn.executemany("INSERT INTO clientes (id,nombre,lente,marca,tier,region_datos,estado) VALUES (?,?,?,?,?,?,?)", fixtures_cli)
    conn.executemany("INSERT INTO proyectos (id,cliente_id,capacidades,plan_entrega,estado) VALUES (?,?,?,?,?)", [
        ("acme-eu-gold", "acme-eu", '["M1","M3"]', "PENDIENTE-#17", "en-construccion"),
        ("vet-usa-basic", "vet-usa", '["M1"]', "basic", "entregado"),
    ])
    conn.commit()

    rep = aggregate(conn, "2026-W24")
    c1 = (rep["clientes"]["total"] == 3
          and rep["clientes"]["por_lente"] == {"Americas": 1, "EMEA": 2}
          and rep["clientes"]["por_tier"] == {"Gold": 1, "Silver": 1, "Starter": 1})
    print(f"   [{'ok' if c1 else 'FALLA'}] cuentas globales: clientes={rep['clientes']['total']}, por_lente={rep['clientes']['por_lente']}")
    p1 = (rep["proyectos"]["total"] == 2
          and rep["proyectos"]["por_plan_entrega"] == {"PENDIENTE-#17": 1, "basic": 1})
    print(f"   [{'ok' if p1 else 'FALLA'}] proyectos: total={rep['proyectos']['total']}, por_plan={rep['proyectos']['por_plan_entrega']}")
    rep_emea = aggregate(conn, "2026-W24", "EMEA")
    f1 = (rep_emea["clientes"]["total"] == 2 and rep_emea["proyectos"]["total"] == 1)
    print(f"   [{'ok' if f1 else 'FALLA'}] filtro lente=EMEA: clientes={rep_emea['clientes']['total']}, proyectos={rep_emea['proyectos']['total']}")
    roi_ok = all(v == "PENDIENTE-#23" for v in rep["roi"].values())
    print(f"   [{'ok' if roi_ok else 'FALLA'}] ROI no inventado: {rep['roi']}")
    try:
        aggregate(conn, "x", "LATAM")
        bad = True
    except ValueError:
        bad = False
    print(f"   [{'ok' if not bad else 'FALLA'}] lente inválida (LATAM) -> BLOQUEO")
    print("ORACLE:", "PASA" if (c1 and p1 and f1 and roi_ok and not bad) else "FALLA")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["oracle", "dry-run", "execute"])
    ap.add_argument("--json", help='{"periodo":..., "lente":...} en JSON')
    ap.add_argument("--confirm", action="store_true", help="OK humano para persistir el snapshot")
    a = ap.parse_args()
    if a.accion == "oracle":
        oracle()
    else:
        inp = json.loads(a.json) if a.json else {"periodo": "2026-W24"}
        if a.accion == "dry-run":
            dry_run(inp)
        elif a.accion == "execute":
            execute(inp, a.confirm)
