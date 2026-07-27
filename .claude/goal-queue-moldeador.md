# Goal Queue — Moldeador: discovery destilado → KB/persona para CUALQUIER emprendimiento

estado: activa
current: 1
turn_cap_por_item: 15

<!--
NORTE: romper el techo de los 3 verticales de clínicas. Que el discovery que destila el bot de WhatsApp
(DEC-004) se convierta AUTOMÁTICAMENTE en la base de conocimiento + persona del MOLDE GENÉRICO
(Juana/ZENKAI), para cualquier emprendedor/a — no solo vet/dental/estetica. La construcción es
automática/reversible; publicar el agente moldeado = VISTO HUMANO (DEC-017).

CONTRATO DEL MOLDE (lo que el moldeador debe PRODUCIR — verificado en Zenkaisystems/agente-wa/src):
- `NEGOCIO` (objeto estructurado: nombre, posicionamiento, whatsapp, email, web, agenda) → ficha.ts
- `CONOCIMIENTO` (KB en markdown por secciones) → hoy en 06-*-BASE-CONOCIMIENTO.md, consumido por ficha.ts
- `INSTRUCCIONES_BASE` (persona/tono/comportamiento) → hoy en 07-*-SYSTEM-PROMPT.md, consumido por prompts.ts

LA GUARDA CENTRAL DE ESTE GOAL (no negociable): NO INVENTAR HECHOS DEL NEGOCIO (GUARDA-003).
- Cada dato afirmado en la KB/persona DEBE trazar a una respuesta del discovery. Lo que la clienta NO dio
  se marca `PENDIENTE-<campo>`, NUNCA se rellena con un precio/horario/servicio inventado (eso alucina y
  quema la marca). El moldeador ESTRUCTURA lo provisto; no fabrica.
- Vertical-AGNÓSTICO: sin whitelist de vertical (a diferencia de agente-clinicas). Funciona para pastelería,
  coach, boutique, lo que sea — porque lo maneja el discovery, no un catálogo cerrado.

INVARIANTES DUROS:
- No inventar (arriba). Discovery incompleto (falta requerido) → BLOQUEA, no produce a medias.
- Publicar/activar el agente moldeado = VISTO HUMANO (gate outbound/go-live). Generar la KB = reversible.
- Si se usa LLM (Fase 4): SOLO para redacción, con el CLI de suscripción (cero API key de Anthropic), y
  SIEMPRE pasa por el verificador no-inventa (Fase 3); si introduce un hecho nuevo, se rechaza.
- packages/ = Python3 stdlib (§10.1). Contrato oracle/dry-run/execute. Nada a prod. Commit scan-gateado.
- Un [blocked] no frena la cola.

RUTAS:
- Molde genérico (contrato de salida): Zenkaisystems/agente-wa/src/{ficha.ts,prompts.ts} + 06-*/07-* .md
- Discovery de referencia: grupojuana/05-PREGUNTAS-AL-CLIENTE.md; campos en integrations/clinics (build_payload)
- Nuevo paquete: xe-mind/packages/moldeador/
- tsx local si hace falta: ~/Documentos/Agencia/grupojuana/agente-wa/node_modules/.bin/tsx
-->

## == FASE 0 — Contrato de salida + shape del discovery (read-only) ==

## [pendiente] 1. Fijar qué produce el moldeador y qué recibe (leer molde + discovery)
**Condición:** reporte que confirma, con archivo:línea: (a) qué consume el molde genérico — `NEGOCIO` (campos) + `CONOCIMIENTO` (secciones típicas de la KB) + `INSTRUCCIONES_BASE` (persona/tono) en `Zenkaisystems/agente-wa/src/{ficha.ts,prompts.ts}`; (b) el shape del discovery hoy (`05-PREGUNTAS-AL-CLIENTE.md` + campos de `build_payload` en `integrations/clinics`). Se define el **contrato de salida** del moldeador: 3 artefactos (`NEGOCIO.json`, `CONOCIMIENTO.md`, `SYSTEM-PROMPT.md`).
**Check:** el reporte cita los campos de `NEGOCIO`, las secciones de la KB y de dónde sale la persona; enumera los 3 artefactos de salida.
**No tocar:** solo lectura; no crear nada aún.

## == FASE 1 — Esquema del discovery estructurado (input, vertical-agnóstico) ==

## [pendiente] 2. Esquema de discovery estructurado + validador (bloquea, no inventa)
**Condición:** existe `packages/moldeador/discovery_schema.py` (o dentro del connector) que define un discovery estructurado **agnóstico al vertical**: REQUERIDOS mínimos (p. ej. `nombre_negocio`, `que_vende`, `canal_contacto`, `responsable_escalamiento`) + opcionales comunes (`servicios`, `precios`, `horarios`, `medios_pago`, `politicas`, `tono_deseado`, `que_NO_hacer`, `ubicacion`, `web`). Un validador que bloquea si falta un requerido (GUARDA-003) y NO completa lo ausente. Es lo que el bot de WhatsApp destila (DEC-004).
**Check:** un discovery completo → válido; uno sin un requerido → BLOQUEO nombrando el campo; un vertical cualquiera ("pasteleria") NO se rechaza (agnóstico). Imprimir los 3 casos.
**No tocar:** no whitelist de vertical; requeridos faltantes se bloquean, no se inventan.

## == FASE 2 — Moldeador determinista (core, SIN LLM, no inventa) ==

## [pendiente] 3. packages/moldeador: discovery → NEGOCIO + CONOCIMIENTO.md + SYSTEM-PROMPT.md
**Condición:** `packages/moldeador/connector.py` (Python3 stdlib, contrato oracle/dry-run/execute + manifest) toma el discovery estructurado y produce los 3 artefactos, rellenando **SOLO lo provisto**; cada hueco → `PENDIENTE-<campo>` (nunca un valor inventado). La KB se arma por secciones fijas (Identidad · Qué vende · Servicios/precios · Horarios/logística · Políticas · Tono · Qué NO hacer · Escalamiento) desde los campos del discovery. `execute --confirm` escribe los 3 archivos a un dir de salida por env (`MOLDE_OUT`, GUARDA-005); dry-run los muestra sin escribir.
**Check:** `oracle` **PASA**: un discovery de una **emprendedora NO-clínica** (p. ej. pastelería artesanal) produce los 3 artefactos con SUS datos y `PENDIENTE-<campo>` donde no dio dato; un discovery sin requerido → BLOQUEA; se verifica que NINGÚN artefacto contiene un dato que el discovery no traía. dry-run imprime los 3; execute --confirm + `MOLDE_OUT=/tmp/x` los escribe.
**No tocar:** no inventar; sin whitelist; execute solo con --confirm + env (GUARDA-001/005).

## == FASE 3 — Verificador "no inventa" (adversarial, la guarda que hace esto seguro) ==

## [pendiente] 4. Verificador de trazabilidad: cada hecho de la KB traza al discovery
**Condición:** existe `packages/moldeador/verificador.py` que, dado el discovery + los 3 artefactos, comprueba que **cada dato concreto afirmado** (precios, horarios, servicios, teléfonos, políticas) **traza a una respuesta del discovery** o está como `PENDIENTE`. Si aparece un hecho que la clienta no dio → **FALLA** (no-invent gate). Es la red que permite, más adelante, dejar que un LLM redacte sin riesgo.
**Check:** `oracle` PASA: artefactos generados por Fase 3 → verificador OK; un artefacto manipulado a mano con un **precio inventado** que no está en el discovery → verificador **FALLA** nombrando el dato colado. Imprimir ambos.
**No tocar:** el verificador no "corrige" inventando; solo detecta y bloquea.

## == FASE 4 — (Opcional, gateado) enriquecimiento LLM grounded ==

## [pendiente] 5. Capa de redacción LLM (CLI de suscripción), SOLO estilo, verificada
**Condición:** documentar + esbozar (`packages/moldeador/enriquecer.py`) una capa OPCIONAL que mejora la **redacción** del skeleton usando el CLI de suscripción (`claude -p`, **cero API key**), con prompt estricto: "usá SOLO estos hechos del discovery, marcá lo que falte como PENDIENTE, NO inventes datos". La salida pasa OBLIGATORIAMENTE por el verificador (Fase 4/tarea 4): si introduce un hecho nuevo → se rechaza y se cae al skeleton determinista. En este goal se hace en **dry-run/diseño** (no se corre contra prod; el binario claude vive en la VPS).
**Check:** el módulo existe con el prompt grounded + el paso de verificación cableado; documentado que sin verificador NO se usa; dry-run muestra el flujo (skeleton → enriquecer → verificar → aceptar|rechazar) sin llamar al LLM real aquí.
**No tocar:** el LLM NUNCA reemplaza al verificador; cero API key (solo suscripción); si el verificador falla, gana el skeleton.

## == FASE 5 — Gate + visto humano + DEC ==

## [pendiente] 6. Gate (generar=reversible, publicar=humano) + DEC-020 + docs + commit
**Condición:** en `classify.ts` la **generación** del molde (`moldeador ... dry-run/execute`) mapea a `write_reversible`; **publicar/activar el agente moldeado** cae en el visto humano ya existente (go-live/entrega → deny). Se agrega caso al oráculo del gate. Existe `vault/10_Decisions/DEC-020_Moldeador-vertical-agnostico.md` (estado `propuesta`, "qué la invalidaría", fuente = este goal): el moldeador estructura el discovery en KB/persona para cualquier vertical, sin inventar, con verificador y visto humano. Índice `MEMORY.md` actualizado. Commit a xe-mind con **gate de escaneo real** (solo si scan==0).
**Check:** oráculo del gate verde con el caso nuevo (moldeador dry-run→allow, publicar→deny); DEC-020 con frontmatter válido; índice actualizado; `git log -1` = commit; scan staged = 0.
**No tocar:** DEC-020 no se ratifica (propuesta); publicar al cliente jamás auto-aprobado; no inventar.
