#!/usr/bin/env python3
"""
Lazo Starter — DRY-RUN (prueba del punto de inflexión).

Demuestra el lazo end-to-end SIN efectos irreversibles:
  cliente -> discovery (DEC-004) -> quote (DEC-006) -> payload nueva_clinica
  -> SE DETIENE antes de execute()  [GUARDA-001: cobro/creación = OK humano]

Determinista, sin LLM, sin escribir en prod, sin inventar (datos no publicados = CONFIRMAR).
Uso:  python3 loop/starter_loop_dryrun.py
"""

# --- DEC-006: precios Starter PUBLICADOS (lo no publicado NO se inventa) ---
STARTER_PRICE = {
    "US": "USD 399/mo",          # publicado en el doc EtherLabX
    "EU": "CONFIRMAR (no publicado; FX en propuesta)",   # hueco #14
    "LATAM": "CONFIRMAR (no publicado; FX en propuesta)" # hueco #14
}

# --- DEC-004: discovery = cuestionario mínimo (patrón 10 preguntas) ---
DISCOVERY_FIELDS = [
    "nombre", "direccion", "servicios", "horario", "duracion_cita",
    "medios_pago", "extras", "valor_cita_promedio",
    "telefono_humano", "google_maps_url",
]

def discovery(client):
    captured = {k: client.get(k) for k in DISCOVERY_FIELDS}
    missing = [k for k, v in captured.items() if v in (None, "")]
    return captured, missing

def quote(region, tier="Starter"):
    return STARTER_PRICE.get(region, "CONFIRMAR (región desconocida)")

def build_payload(client):
    # mapea discovery -> input de nueva_clinica.ts (NO lo ejecuta)
    return {
        "nombre": client["nombre"],
        "vertical": client["vertical"],          # vet/dental/estetica
        "telefono_humano": client["telefono_humano"],
        "ciudad": client.get("ciudad"),
        "servicios": client.get("servicios"),
        "valor_cita_promedio": client.get("valor_cita_promedio"),
        "plan": "basic",  # PROVISIONAL: mapeo Starter->basic es hueco #17, sin firmar
    }

def run(client):
    print("== LAZO STARTER (dry-run) ==\n")
    captured, missing = discovery(client)
    print("1) DISCOVERY (DEC-004):")
    for k, v in captured.items():
        print(f"   - {k}: {v}")
    if missing:
        print(f"\n   [BLOQUEO GUARDA-003] faltan campos: {missing} -> pedir al humano, NO inventar.\n")
        return
    print(f"\n2) COTIZACION (DEC-006): Starter {client['region']} = {quote(client['region'])}")
    print("\n3) PAYLOAD para nueva_clinica.ts (construido, NO ejecutado):")
    for k, v in build_payload(client).items():
        print(f"   {k}: {v}")
    print("\n4) [GUARDA-001] STOP. No se ejecuta execute() (crear asistente / cobrar)")
    print("   sin OK humano explícito. La mente hizo todo lo reversible; el humano firma.")
    print("\n>> Lazo demostrado. Para producción: envolver nueva_clinica.ts tras execute() vía MCP (Fase 3).")

if __name__ == "__main__":
    # cliente simulado (vet, US) — datos de prueba
    cliente_demo = {
        "region": "US", "vertical": "veterinaria",
        "nombre": "Sunrise Vet Clinic", "direccion": "123 Main St, Austin TX",
        "servicios": ["Checkup", "Vaccines", "Grooming"], "horario": "Mon-Sat 8-18",
        "duracion_cita": "30min", "medios_pago": "Card, cash",
        "extras": "Parking", "valor_cita_promedio": 90,
        "telefono_humano": "+15125550123", "google_maps_url": "https://g.page/...",
    }
    run(cliente_demo)
