#!/usr/bin/env python3
"""
Receptor del callback de Embedded Signup (`/es-callback`).

Al cerrar el popup de Meta, el navegador entrega un `code` a este endpoint. El receptor NO
ejecuta el alta real: corre `onboarding-meta` en modo DRY-RUN (FakeGraph, sin red) y ENCOLA el
resultado para VISTO HUMANO (DEC-017 Dec.4). La construcción/alta real solo ocurre tras el OK.

Superficie: SOLO se sirve `/es-callback`; cualquier otro path -> 404. El panel y todo lo demás
siguen en loopback (invariante cero-inbound; Caddy expone solo /webhook y /es-callback — ver Fase 3).

La implementación real de Meta (RealGraph) es el hueco PENDIENTE-META-APP: aquí se usa FakeGraph.

Uso:
  python3 callback.py serve            # levanta el server loopback (ES_CALLBACK_PORT, default 3002)
  python3 callback.py selftest         # e2e local: postea un code, verifica 200 + encolado + no-ejecutado
"""
import importlib.util, json, os, pathlib, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


onboarding = _load("onboarding_meta_connector", "packages/onboarding-meta/connector.py")
registro = onboarding.registro

# Cola de revisión en memoria (para tests). En producción: persistir a ES_REVIEW_QUEUE (JSONL) o dashboard.
REVIEW_QUEUE: list = []


def build_review_item(inp: dict) -> dict:
    """Corre el provisioning en DRY-RUN (FakeGraph) y arma el ítem para la superficie de revisión.
    NO ejecuta ningún efecto real (ni Meta ni DB). Devuelve {ok, item|error}."""
    ok, msg = onboarding.validate(inp)
    if not ok:
        return {"ok": False, "error": msg}
    plan = onboarding.provision_plan(inp, onboarding.FakeGraph())
    c, proys = registro.compose(onboarding.build_alta(inp, plan["ids"]))
    return {
        "ok": True,
        "item": {
            "cliente": {"id": c["id"], "nombre": c["nombre"], "lente": c["lente"],
                        "marca": c["marca"], "tier": c["tier"], "estado": c["estado"],
                        "region_datos": c["region_datos"]},
            "proyecto": {"id": proys[0]["id"], "plan_entrega": proys[0]["plan_entrega"]},
            "provisioning": {"waba_id": plan["ids"]["waba_id"], "phone_number_id": plan["ids"]["phone_number_id"],
                             "modo": "SIMULADO (FakeGraph — real bloqueado por PENDIENTE-META-APP)"},
            "siguiente_paso": "VISTO HUMANO — abrir al público requiere OK explícito (DEC-017 Dec.4). NO ejecutado.",
        },
    }


def handle_callback(params: dict, queue: list) -> dict:
    """Punto puro y testeable. Recibe los params del callback, encola el dry-run, NO ejecuta."""
    code = params.get("code")
    if not code:
        return {"status": 400, "queued": False, "error": "falta 'code' de Embedded Signup"}
    inp = {
        "code": code,
        "cliente": {"nombre": params.get("nombre", "")},
        "lente": params.get("lente", ""),
        "tier": params.get("tier", ""),
        "marca": params.get("marca", ""),
    }
    res = build_review_item(inp)
    if not res["ok"]:
        # 200: el callback se recibió bien; el ítem queda marcado como incompleto para el humano.
        queue.append({"estado": "incompleto", "error": res["error"], "code_recibido": True})
        return {"status": 200, "queued": True, "ejecutado": False, "incompleto": True}
    queue.append({"estado": "pendiente-visto-humano", **res["item"]})
    return {"status": 200, "queued": True, "ejecutado": False, "incompleto": False}


class Handler(BaseHTTPRequestHandler):
    def _only_callback(self):
        return urlparse(self.path).path.startswith("/es-callback")

    def _params(self):
        q = parse_qs(urlparse(self.path).query)
        params = {k: v[0] for k, v in q.items()}
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length:
            body = self.rfile.read(length).decode("utf-8")
            try:
                params.update(json.loads(body))
            except json.JSONDecodeError:
                for k, v in parse_qs(body).items():
                    params[k] = v[0]
        return params

    def _respond(self, code, obj):
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        if not self._only_callback():
            self._respond(404, {"error": "not found"}); return
        result = handle_callback(self._params(), REVIEW_QUEUE)
        self._respond(result["status"], result)

    def do_GET(self):
        if not self._only_callback():
            self._respond(404, {"error": "not found"}); return
        result = handle_callback(self._params(), REVIEW_QUEUE)
        self._respond(result["status"], result)

    def log_message(self, *a):  # silencio (no logs de acceso con posibles datos)
        pass


def serve():
    port = int(os.environ.get("ES_CALLBACK_PORT", "3002"))
    httpd = HTTPServer(("127.0.0.1", port), Handler)
    print(f"[es-callback] escuchando en 127.0.0.1:{port}/es-callback (solo loopback)")
    httpd.serve_forever()


def selftest():
    """e2e local: levanta el server en un puerto efímero, postea un code, verifica 200+encolado+no-ejecutado."""
    import threading, urllib.request
    REVIEW_QUEUE.clear()
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    allok = True

    def check(name, cond):
        nonlocal allok
        if not cond: allok = False
        print(f"   [{'ok' if cond else 'FALLA'}] {name}")

    # 1. POST con code + contexto completo -> 200, encolado, NO ejecutado
    body = json.dumps({"code": "AQD-es-code", "nombre": "Clinica Sonrisa",
                       "lente": "Americas", "tier": "Starter", "marca": "EtherLabX"}).encode()
    req = urllib.request.Request(f"http://127.0.0.1:{port}/es-callback", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())
    check("POST /es-callback responde 200", resp["status"] == 200)
    check("encolado para revisión", resp["queued"] is True)
    check("NO ejecutado (sin efecto real)", resp["ejecutado"] is False)
    check("ítem en la cola con estado pendiente-visto-humano",
          len(REVIEW_QUEUE) == 1 and REVIEW_QUEUE[0]["estado"] == "pendiente-visto-humano")
    check("ítem trae plan dry-run (waba SIMULADO)", "SIMULADO" in REVIEW_QUEUE[0]["provisioning"]["modo"])
    check("ítem marca siguiente paso = visto humano", "VISTO HUMANO" in REVIEW_QUEUE[0]["siguiente_paso"])

    # 2. POST sin code -> 400
    req2 = urllib.request.Request(f"http://127.0.0.1:{port}/es-callback",
                                  data=json.dumps({"lente": "Americas"}).encode(),
                                  headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req2)
        code2 = 200
    except urllib.error.HTTPError as e:
        code2 = e.code
    check("POST sin code -> 400", code2 == 400)

    # 3. Otro path -> 404
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/otra-cosa")
        code3 = 200
    except urllib.error.HTTPError as e:
        code3 = e.code
    check("path distinto de /es-callback -> 404", code3 == 404)

    httpd.shutdown()
    print("SELFTEST:", "PASA" if allok else "FALLA")
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
    elif len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
    else:
        print("uso: python3 callback.py [serve|selftest]")
