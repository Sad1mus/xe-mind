# infra/canal-mando — Operar Xe por chat (Telegram → Claude Code headless)

Implementación de referencia de [[DEC-012]], bajo [[GUARDA-001]] · [[GUARDA-002]] · [[GUARDA-005]] · [[GUARDA-006]].

> **Estado: esqueleto.** El núcleo de gobierno (`governance.ts`) es código real y completo. El adaptador al **Claude Agent SDK** (`agent.ts`) tiene un punto de integración marcado `TODO(verificar-SDK)` — fijar la firma exacta contra la versión instalada de `@anthropic-ai/claude-agent-sdk` antes de producción. La lógica de gate NO depende del SDK a propósito.

## Principio de diseño (el que no se negocia)
**El gate vive en código, no en el prompt.** Una instrucción "pide permiso antes de cobrar" en el system prompt no es un control — un jailbreak o una alucinación la salta. Por eso toda acción del agente pasa por `governance.ts` ANTES de ejecutarse, y el agente físicamente no tiene la credencial de dinero hasta que un humano confirma.

## Flujo
```
Telegram (solo chat_id en allowlist)
   │  ── valida identidad + rate-limit + kill switch
   ▼
bridge.ts ── arma el system prompt = CLAUDE.md de Xe + handoff entrante del substrato
   ▼
agent.ts (Claude Agent SDK, headless, cwd = repo Agencia)
   │  cada tool-call → canUseTool() → governance.ts:
   ├─ READ / reversible + bajo tope            → ALLOW (ejecuta)
   ├─ irreversible / dinero                    → DRY-RUN → pide confirm en Telegram
   │                                              → 2º OK humano → ejecuta con credencial de dinero
   ├─ excede tope ($/tokens/acciones)          → DENY (GUARDA-006)
   └─ confianza BAJA / conflicto GUARDA        → DENY + escala (§4 del CLAUDE.md)
   ▼
audit.ts ── log append-only (acción · confianza · quién confirmó · resultado)
substrato ── handoff saliente escrito (§7), no en contexto
```

## Mapa de controles → guardas
| Control en código | Guarda / DEC |
|---|---|
| Allowlist por `chat_id`; token del bot = secreto crítico | [[DEC-012]] |
| `canUseTool` que clasifica y gatea cada acción | [[GUARDA-001]] |
| Doble confirm humano para dinero (no solo el del prompt) | [[GUARDA-001]] + [[DEC-012]] |
| Topes duros: $/acción, $/día, $/cliente, tokens/día, acciones-cara-afuera/ventana | [[GUARDA-006]] |
| Kill switch (archivo/flag que aborta todo) | [[GUARDA-006]] |
| Log append-only de cada decisión | [[GUARDA-006]] |
| Credenciales por tier (lectura ≠ cliente ≠ dinero ≠ deploy); todo en `env` | [[GUARDA-005]] |
| Ruteo por teatro: dato regulado se ejecuta en su región | [[GUARDA-002]] |

## Rollout por fases (NO saltar — §5 / megagoal Fase 6)
1. **Solo lectura** — `EXEC_MODE=read_only`. El bot consulta estado/métricas/substrato. Cero escritura. Ganas confianza en el canal.
2. **Escritura reversible con confirm** — `EXEC_MODE=reversible`. Redacta cotizaciones/mensajes en borrador; tú apruebas el envío.
3. **Dinero con doble gate + topes** — `EXEC_MODE=money_double_gate`. Esta es la etapa elegida. Solo tras construir y probar topes + kill switch + auditoría con la versión vieja como oráculo (strangler-fig, §9.3).
4. **Autonomía graduada** — solo donde la confianza medida sea ALTA y la acción reversible. Nunca alto-monto + irreversible sin humano.

## Archivos
- `bridge.ts` — entrada: Telegram → arma contexto → invoca agente → responde.
- `agent.ts` — adaptador al Claude Agent SDK (punto de integración marcado).
- `governance.ts` — el gate: clasificación, topes, kill switch, confirm. **Núcleo, framework-agnóstico.**
- `audit.ts` — log append-only.
- `.env.example` — toda la config/credenciales por `env` (GUARDA-005). NUNCA commitear el `.env` real.
