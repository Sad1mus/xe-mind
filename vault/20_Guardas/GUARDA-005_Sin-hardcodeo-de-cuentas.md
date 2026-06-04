---
id: GUARDA-005
dueño: Jordy + HaxelGG
ámbito: infra / portabilidad
estado: aceptada (2026-06-04)
---
**Restringe:** escribir en el código cualquier **referencia de cuenta o proyecto** — IDs, `project ref`, URLs de Supabase/Vercel, tokens, keys, dominios. Todo eso vive **solo en `env`/config**.

**Por qué:** la agencia es empresa compartida y migrará a Team/Org. La migración es **trivial si nada está hardcodeado** (transferir repo + cambiar env); se vuelve una caza de referencias si lo está. Esta guarda mantiene Xe **portable por diseño** ([[DEC-010]]).

**No hace:** no decide qué cuentas se usan (eso es decisión humana); solo prohíbe enterrarlas en el código.
