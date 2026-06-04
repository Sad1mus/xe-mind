# Convenciones del Vault — zenkai-mind

Hereda el ADN epistémico de MIDAS. Un hecho, un dueño. Nada de criterio inventado.

## Tipos de nota

### DEC — Decisión (falsable)
Archivo: `vault/10_Decisions/DEC-NNN_titulo-kebab.md`. Frontmatter + cuerpo:
```
---
id: DEC-001
titulo: ...
dueño: <humano que la firma>
fuente: <artefacto/ruta de donde se destiló>
estado: propuesta | aceptada | superada
lente: global | americas | emea | latam
---
**Decisión:** qué se decidió, en una frase.
**Porqué:** la razón.
**Supuestos:** de qué depende que sea válida.
**Qué la invalidaría:** el evento/dato que la mata (falsabilidad — obligatorio).
**Relaciones:** [[DEC-00X]] (deriva_de | supersede | restringida_por | contradice)
```

### GUARDA — restricción (solo limita, nunca crea)
Archivo: `vault/20_Guardas/GUARDA-NNN_titulo.md`.
```
---
id: GUARDA-001
dueño: <humano>
ámbito: global | regional | financiero | datos
---
**Restringe:** qué acción cierra.
**Por qué:** el riesgo que evita.
**No hace:** (recordatorio) una guarda nunca inventa una regla con criterio propio.
```

### VEREDICTO — resultado de probar una hipótesis sin piedad
Archivo: `vault/40_Postmortems/` (cuando aplique). "Se probó así → salió esto → con esta confianza". Puede matar una DEC.

## Reglas duras
- **Falsabilidad obligatoria** en cada DEC (el campo "qué la invalidaría" no puede estar vacío).
- **Cita la fuente.** Si una DEC no se puede atar a un artefacto o a una firma humana, es invento → no va.
- **Hueco ≠ invento.** Lo que no está decidido se registra en `30_Founders/preguntas-entrevista.md`, no se rellena.
- **Lente explícita.** Toda decisión dice si es global o regional (americas/emea/latam).
- **Índice.** Cada nota nueva añade una línea a `vault/MEMORY.md`.
