---
id: DEC-015
titulo: Linear como capa de coordinación; git sigue siendo fuente de verdad
dueño: Jordy (Sad1mus) — pendiente ratificación de HaxelGG (empresa compartida)
fuente: conversación de decisión 2026-06-20 + endpoint verificado contra linear.app/docs/mcp
estado: propuesta
lente: global
---
**Decisión:** La coordinación de trabajo de Xe (issues, ciclos, roadmap) vive en
**Linear**, vía su MCP oficial hosted. El conocimiento —DEC, GUARDA, VEREDICTO,
specs, código— **sigue en git, en el monorepo `xe-mind`**. Linear es el tablero; git
es el cerebro. Se descarta Huly autohosteado (≈13 contenedores, ya fallaba, sin MCP).

**Operativo (verificado 2026-06-20):**
- Endpoint: `https://mcp.linear.app/mcp` (Streamable HTTP, OAuth).
- Alta: `claude mcp add --transport http --scope user linear-server https://mcp.linear.app/mcp`
- Auth: `/mcp` en sesión de Claude Code (requiere reiniciar la sesión si se agregó en caliente).
- Puente git↔Linear: integración nativa GitHub; ramas/PRs referencian el issue
  (`Fixes ABC-123`) para autolinkear tarea ↔ commit ↔ PR.

**Porqué:** los socios necesitan un PM compartido sin volverse sysadmins; Linear es
cloud, tiene MCP oficial y cero infra. Mejor que GitHub Projects para multi-cliente y
multi-región. Mantener la fuente de verdad en git preserva el ADN epistémico
(DEC/GUARDA/VEREDICTO auditables, versionados) que una herramienta de chat/PM no da.

**Supuestos:** el plan de Linear alcanza para los socios sin costo prohibitivo · la
integración GitHub conecta issue↔PR de forma fiable · Linear mantiene su MCP oficial.

**Qué la invalidaría:** que una decisión arquitectónica empiece a vivir SOLO en
comentarios de un issue de Linear (erosión de la frontera → la herramienta estaría
violando su propósito) · que Linear degrade o discontinúe el MCP · que el costo por
asiento se vuelva prohibitivo al crecer sin alternativa con MCP · que la residencia
regional ([[GUARDA-002]]) obligue a no meter datos de cliente regulados en Linear
cloud (en ese caso Linear no toca esos datos; no se invalida la coordinación general).

**Guardas:** restringida_por [[GUARDA-002]] (residencia: ningún dato regulado de
cliente entra a Linear cloud) · candidata a nueva GUARDA (propuesta, no creada): "las
decisiones no viven solo en Linear; si es decisión, es DEC en git".

**Relaciones:** contextualiza [[DEC-010]] (Linear coordina; NO toca el monorepo ni los
productos integrados) · registra el descarte de Huly · concreta CLAUDE.md §9.4 (Linear
pasa de sistema aspiracional a sistema vivo confirmado).
