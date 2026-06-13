#!/usr/bin/env python3
"""
Capacidad registro — la "verdad exacta" (CLAUDE.md §3.1) de CLIENTES y PROYECTOS de la agencia,
a traves de las 3 lentes (Americas/EMEA/APAC). Es la herramienta con la que Xe ADMINISTRA:
da de alta, consulta y mantiene el estado de cada cliente/proyecto, con residencia por region.

Cumple el contrato de capacidades: inputs · dry_run · execute · oracle.

Reglas duras:
  - Residencia (GUARDA-002): region_datos marca donde viven los datos; el indice referencia, no copia.
  - No inventa (GUARDA-003): campo requerido faltante / lente|tier invalido -> BLOQUEO. El mapeo
    tier->plan NO firmado (todo lo que no sea Starter->basic, DEC-009) se marca 'PENDIENTE-#17', no se fabrica.
  - execute() escribe SOLO con --confirm (GUARDA-001) y en la DB de env REGISTRO_DB (GUARDA-005, sin hardcode).
  - El ciclo de vida de 'estado' es PROPUESTO en la DEC del esquema; pendiente VEREDICTO humano.

Uso:
  python3 connector.py oracle
  python3 connector.py dry-run                       # demo (1 cliente EMEA Gold + 1 proyecto)
  python3 connector.py dry-run --json '{...}'
  REGISTRO_DB=/tmp/registro_test.db python3 connector.py execute --confirm --json '{...}'
  REGISTRO_DB=/tmp/registro_test.db python3 connector.py list
"""
import argparse, json, os, pathlib, re, sqlite3, sys, unicodedata

SCHEMA_PATH = pathlib.Path(__file__).resolve().parent / "schema.sql"

LENTES = ["Americas", "EMEA", "APAC"]                                   # CLAUDE.md §1
TIERS = ["Starter", "Silver", "Gold", "Enterprise", "Partner"]         # DEC-006
PLAN_FIRMADO = {"Starter": "basic"}                                    # DEC-009 (lo unico firmado)
PENDIENTE = "PENDIENTE-#17"                                            # marcador de hueco, NO un valor inventado
ESTADOS_CLIENTE = ["prospecto", "onboarding", "activo", "pausado", "cerrado"]
ESTADOS_PROYECTO = ["propuesto", "en-construccion", "entregado", "pausado", "cerrado"]
REQ_CLIENTE = ["nombre", "lente", "marca", "tier"]


def slug(nombre: str) -> str:
    s = unicodedata.normalize("NFD", nombre.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"^-|-$", "", s)


def residencia_default(lente: str) -> str:
    """Etiqueta gruesa de residencia por lente (§1). La politica por pais es hueco (GUARDA-002 'No hace')."""
    return {
        "Americas": "local/region-Americas",
        "EMEA": "UE (GDPR, residencia en-region obligatoria)",
        "APAC": "local/pais (residencia por pais)",
    }[lente]


def validate_cliente(c: dict):
    faltan = [k for k in REQ_CLIENTE if not c.get(k)]
    if faltan:
        return False, f"[BLOQUEO GUARDA-003] cliente: faltan requeridos {faltan} -> pedir al humano."
    if c["lente"] not in LENTES:
        return False, f"[BLOQUEO] lente invalida '{c['lente']}'. Usa: {LENTES}"
    if c["tier"] not in TIERS:
        return False, f"[BLOQUEO] tier invalido '{c['tier']}'. Usa: {TIERS}"
    if c.get("estado") and c["estado"] not in ESTADOS_CLIENTE:
        return False, f"[BLOQUEO] estado cliente invalido '{c['estado']}'. Usa: {ESTADOS_CLIENTE}"
    return True, "ok"


def validate_proyecto(p: dict, cliente_tier: str):
    caps = p.get("capacidades")
    if not isinstance(caps, list) or len(caps) == 0:
        return False, "[BLOQUEO GUARDA-003] proyecto: 'capacidades' debe ser lista no vacia."
    if p.get("estado") and p["estado"] not in ESTADOS_PROYECTO:
        return False, f"[BLOQUEO] estado proyecto invalido '{p['estado']}'. Usa: {ESTADOS_PROYECTO}"
    # plan_entrega: solo Starter->basic esta firmado (DEC-009). Lo demas NO se inventa.
    if not p.get("plan_entrega") and cliente_tier != "Starter":
        # no es error: se registra como hueco explicito, no se fabrica un plan
        pass
    return True, "ok"


def build_cliente(c: dict) -> dict:
    return {
        "id": slug(c["nombre"]),
        "nombre": c["nombre"],
        "lente": c["lente"],
        "marca": c["marca"],
        "tier": c["tier"],
        "region_datos": c.get("region_datos") or residencia_default(c["lente"]),
        "estado": c.get("estado") or "prospecto",
    }


def build_proyecto(p: dict, cliente_id: str, cliente_tier: str, idx: int) -> dict:
    plan = p.get("plan_entrega")
    if not plan:
        plan = PLAN_FIRMADO.get(cliente_tier, PENDIENTE)  # Starter->basic; resto -> PENDIENTE-#17
    pid = slug(p["nombre"]) if p.get("nombre") else f"{cliente_id}-p{idx + 1}"
    return {
        "id": pid,
        "cliente_id": cliente_id,
        "capacidades": list(p["capacidades"]),
        "plan_entrega": plan,
        "estado": p.get("estado") or "propuesto",
    }


def validate_alta(alta: dict):
    c = alta.get("cliente")
    if not isinstance(c, dict):
        return False, "[BLOQUEO GUARDA-003] falta 'cliente' (objeto)."
    ok, msg = validate_cliente(c)
    if not ok:
        return False, msg
    for i, p in enumerate(alta.get("proyectos", [])):
        ok, msg = validate_proyecto(p, c["tier"])
        if not ok:
            return False, f"[BLOQUEO] proyecto #{i}: {msg}"
    return True, "ok"


def compose(alta: dict):
    c = build_cliente(alta["cliente"])
    proys = [build_proyecto(p, c["id"], alta["cliente"]["tier"], i)
             for i, p in enumerate(alta.get("proyectos", []))]
    return c, proys


# ---------- contrato: dry_run ----------
def dry_run(alta: dict):
    ok, msg = validate_alta(alta)
    print(f"[inputs] {msg}")
    if not ok:
        return
    c, proys = compose(alta)
    print(f"[cliente] {c['id']} · {c['nombre']} · lente={c['lente']} · marca={c['marca']} · tier={c['tier']}")
    print(f"[residencia] {c['region_datos']}  (GUARDA-002: se referencia, no se copia el dato regulado)")
    print(f"[estado] {c['estado']}")
    for p in proys:
        marca_pend = "  ⚠️ plan NO firmado (hueco #17)" if p["plan_entrega"] == PENDIENTE else ""
        print(f"  - proyecto {p['id']}: caps={p['capacidades']} · plan_entrega={p['plan_entrega']}{marca_pend} · estado={p['estado']}")
    print("[execute] STOP — GUARDA-001: no se escribe sin OK humano (--confirm) ni sin env REGISTRO_DB.")


# ---------- contrato: execute ----------
def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn


def execute(alta: dict, confirm: bool):
    ok, msg = validate_alta(alta)
    if not ok:
        print(msg)
        sys.exit(1)
    db_path = os.environ.get("REGISTRO_DB")  # GUARDA-005: ruta por env, sin hardcode
    c, proys = compose(alta)
    if not confirm or not db_path:
        print("[execute] NO ejecutado (GUARDA-001).")
        if not db_path:
            print("   Falta env REGISTRO_DB (ruta a la DB local; usa una desechable para probar).")
        if not confirm:
            print("   Falta --confirm (OK humano explicito).")
        return
    conn = _connect(db_path)
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO clientes (id,nombre,lente,marca,tier,region_datos,estado) "
            "VALUES (?,?,?,?,?,?,?)",
            (c["id"], c["nombre"], c["lente"], c["marca"], c["tier"], c["region_datos"], c["estado"]))
        for p in proys:
            conn.execute(
                "INSERT OR REPLACE INTO proyectos (id,cliente_id,capacidades,plan_entrega,estado) "
                "VALUES (?,?,?,?,?)",
                (p["id"], p["cliente_id"], json.dumps(p["capacidades"]), p["plan_entrega"], p["estado"]))
    print(f"[execute] OK humano. Escrito en {db_path}: cliente '{c['id']}' + {len(proys)} proyecto(s).")
    _print_select(conn, c["id"])
    conn.close()


def _print_select(conn: sqlite3.Connection, cliente_id: str):
    print("[verificacion SELECT]")
    for row in conn.execute(
            "SELECT id,nombre,lente,marca,tier,region_datos,estado FROM clientes WHERE id=?", (cliente_id,)):
        print("   cliente:", dict(zip(["id", "nombre", "lente", "marca", "tier", "region_datos", "estado"], row)))
    for row in conn.execute(
            "SELECT id,cliente_id,capacidades,plan_entrega,estado FROM proyectos WHERE cliente_id=?", (cliente_id,)):
        print("   proyecto:", dict(zip(["id", "cliente_id", "capacidades", "plan_entrega", "estado"], row)))


def cmd_list():
    db_path = os.environ.get("REGISTRO_DB")
    if not db_path:
        print("[list] falta env REGISTRO_DB.")
        return
    conn = _connect(db_path)
    print("[clientes]")
    for row in conn.execute("SELECT id,lente,marca,tier,estado FROM clientes ORDER BY lente,id"):
        print("  ", row)
    print("[proyectos]")
    for row in conn.execute("SELECT id,cliente_id,plan_entrega,estado FROM proyectos ORDER BY cliente_id,id"):
        print("  ", row)
    conn.close()


# ---------- contrato: oracle ----------
def oracle():
    casos = [
        ({"cliente": {"nombre": "ACME EU", "lente": "EMEA", "marca": "ZENKAI", "tier": "Gold"}}, True),
        ({"cliente": {"nombre": "X", "lente": "EMEA", "marca": "ZENKAI"}}, False),                 # falta tier
        ({"cliente": {"nombre": "X", "lente": "LATAM", "marca": "EtherLabX", "tier": "Gold"}}, False),  # lente invalida
        ({"cliente": {"nombre": "X", "lente": "APAC", "marca": "Z", "tier": "Platino"}}, False),    # tier invalido
        ({"cliente": {"nombre": "X", "lente": "APAC", "marca": "Z", "tier": "Gold"},
          "proyectos": [{"capacidades": []}]}, False),                                             # proyecto sin caps
    ]
    allok = True
    for alta, esperado in casos:
        got = validate_alta(alta)[0]
        estado = "ok" if got == esperado else "FALLA"
        if got != esperado:
            allok = False
        print(f"   [{estado}] {alta['cliente'].get('nombre')}/{alta['cliente'].get('lente')}/"
              f"{alta['cliente'].get('tier')} -> valido={got} (esperado {esperado})")
    # residencia etiquetada por lente
    c_emea = build_cliente({"nombre": "R", "lente": "EMEA", "marca": "ZENKAI", "tier": "Gold"})
    res_ok = "GDPR" in c_emea["region_datos"]
    print(f"   [{'ok' if res_ok else 'FALLA'}] residencia EMEA etiquetada: {c_emea['region_datos']}")
    # mapeo tier->plan: Starter->basic firmado; Gold sin plan -> PENDIENTE (no inventa)
    pe_starter = build_proyecto({"capacidades": ["M1"]}, "c", "Starter", 0)["plan_entrega"]
    pe_gold = build_proyecto({"capacidades": ["M1", "M3"]}, "c", "Gold", 0)["plan_entrega"]
    map_ok = (pe_starter == "basic" and pe_gold == PENDIENTE)
    print(f"   [{'ok' if map_ok else 'FALLA'}] plan: Starter={pe_starter}, Gold={pe_gold} (no inventa el de Gold)")
    # composicion cliente->proyecto coherente
    c, proys = compose({"cliente": {"nombre": "Demo", "lente": "Americas", "marca": "Americas-por-definir", "tier": "Silver"},
                        "proyectos": [{"capacidades": ["M1", "M2"]}]})
    comp_ok = (len(proys) == 1 and proys[0]["cliente_id"] == c["id"])
    print(f"   [{'ok' if comp_ok else 'FALLA'}] composicion cliente->proyecto: {c['id']} <- {proys[0]['id']}")
    print("ORACLE:", "PASA" if (allok and res_ok and map_ok and comp_ok) else "FALLA")


DEMO = {
    "cliente": {"nombre": "Klinik Berlin Mitte", "lente": "EMEA", "marca": "ZENKAI", "tier": "Gold"},
    "proyectos": [{"nombre": "Klinik Berlin — agente Gold", "capacidades": ["M1", "M2", "M3"]}],
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["oracle", "dry-run", "execute", "list"])
    ap.add_argument("--json", help="alta {cliente, proyectos[]} en JSON")
    ap.add_argument("--confirm", action="store_true", help="OK humano para execute")
    a = ap.parse_args()
    if a.accion == "oracle":
        oracle()
    elif a.accion == "list":
        cmd_list()
    else:
        alta = json.loads(a.json) if a.json else DEMO
        if a.accion == "dry-run":
            dry_run(alta)
        elif a.accion == "execute":
            execute(alta, a.confirm)
