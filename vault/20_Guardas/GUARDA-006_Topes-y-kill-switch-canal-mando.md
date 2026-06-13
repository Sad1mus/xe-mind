---
id: GUARDA-006
dueño: Jordy + socios
ámbito: global (financiero + operacional)
estado: propuesta (pendiente VEREDICTO humano)
---
**Restringe:** el **canal de mando** (cualquier interfaz que dispare ejecución de Xe — Telegram en v1, ver [[DEC-012]]) no puede:
1. Ejecutar una acción cuyo efecto **exceda los topes duros configurados**: monto $ por acción / por día / por cliente; gasto de tokens del LLM por sesión / por día; nº de acciones de cara afuera (cobros, mensajes, deploys) por ventana de tiempo.
2. Ejecutar una acción **irreversible o de dinero sin un `confirm` humano explícito** entregado por el propio canal (refuerza y NO reemplaza [[GUARDA-001]]).
3. Seguir operando cuando se acciona el **kill switch**: una señal única debe abortar toda ejecución en curso en los tres teatros en segundos.

Además: **el gate vive en CÓDIGO, no en el prompt.** Una instrucción en el system prompt no cuenta como control — debe ser imposible de saltar por alucinación o prompt-injection. Toda acción queda en un **log append-only** (acción · confianza · quién confirmó · resultado).

**Por qué:** a la escala de "Xe controla toda la agencia y mueve montos grandes", un loop, un jailbreak o un error sin tope puede causar daño **masivo e irreversible** (cobros en cascada, gasto de tokens descontrolado, mensajes equivocados a clientes) **antes** de que un humano lo note. El tope, el confirm-en-código y el kill switch acotan el blast radius: convierten un fallo catastrófico en uno contenido y reversible.

**No hace:** una guarda no decide los montos ni las políticas (los umbrales concretos son decisión humana → [[DEC-012]] / `30_Founders/preguntas-entrevista.md`); solo **cierra la ejecución por encima de los límites** y exige el freno. Tampoco sustituye [[GUARDA-001]] (la prohibición de cobrar/firmar/enviar sin humano sigue intacta); la endurece para el canal automatizado.

**Relaciones:** endurece [[GUARDA-001]] para el canal de mando · restringe [[DEC-012]] · convive con [[GUARDA-002]] (residencia) y [[GUARDA-005]] (sin hardcodeo: los topes viven en `env`/config, no en el código).
