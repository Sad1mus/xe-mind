# Contrato de capacidades — cómo la mente orquesta (el punto de inflexión)

> El contrato que permite que Jordy y HaxelGG construyan capacidades **en paralelo** y la mente las orqueste sin pisarse. Nace de probar el lazo Starter una vez (`loop/starter_loop_dryrun.py`).

## Interfaz que TODA capacidad debe cumplir
Para que la mente (Xe) pueda orquestar un módulo (skill de orvex, pipeline de clínicas, ecommerce, lo que sea) como subagente, el módulo expone:

1. **`manifest`** — qué hace, qué tier(s) sirve, qué vertical(es), qué inputs requiere, qué entrega.
2. **`inputs` validados** — esquema explícito (la mente NO inventa campos faltantes → bloquea, GUARDA-003).
3. **`dry_run()`** — produce el resultado SIN efectos irreversibles (sin cobro, sin envío, sin escribir prod). Obligatorio.
4. **`execute()`** — el efecto real. **Detrás de GUARDA-001**: cobro/firma/envío/creación en prod = requiere OK humano.
5. **`oracle`** — cómo se verifica que hizo bien (para la absorción strangler-fig: la versión vieja es el oráculo de la nueva).

## El lazo (probado en dry-run)
```
cliente → discovery (DEC-004) → quote (DEC-006, por región) → build_payload
        → dry_run: muestra todo, NO ejecuta
        → [HUMANO aprueba] → execute() (crea el asistente, cobra)   ← GUARDA-001
```

## Por qué esto habilita el paralelo
- Jordy construye módulo A, HaxelGG módulo B; **ambos cumplen el contrato** → la mente los descubre y compone sin integración a medida.
- Un tier = un bundle de módulos. Un nicho = un bundle + tuning. "Todo el portafolio" emerge de la librería, no de 10 monolitos ([[DEC-008]]).

## Estado
- ✅ Lazo Starter probado en dry-run determinista (`loop/starter_loop_dryrun.py`) — sin tocar prod, sin LLM, sin invención.
- ⏳ Falta: envolver `nueva_clinica.ts` real tras `execute()` vía MCP (Fase 3, requiere mapeo tier→plan, hueco #17) + cablear MCP read-first.

**Relaciones:** habilita [[DEC-008]] · `execute()` gobernado por [[GUARDA-001]] · módulos entregan bajo [[DEC-005]].
