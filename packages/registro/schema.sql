-- registro — capa "verdad exacta" (CLAUDE.md §3.1) de clientes y proyectos de la agencia.
-- Local-first (DEC-010). Un dueño por hecho: esta DB es la verdad de clientes/proyectos.
-- Residencia (GUARDA-002): region_datos marca dónde viven los datos regulados; el indice
-- global referencia, NO copia el dato regulado.

CREATE TABLE IF NOT EXISTS clientes (
  id           TEXT PRIMARY KEY,                         -- slug(nombre)
  nombre       TEXT NOT NULL,
  lente        TEXT NOT NULL CHECK (lente IN ('Americas','EMEA','APAC')),   -- CLAUDE.md §1
  marca        TEXT NOT NULL,                            -- DEC-007 (ZENKAI/EtherLabX/Americas-por-definir)
  tier         TEXT NOT NULL CHECK (tier IN ('Starter','Silver','Gold','Enterprise','Partner')), -- DEC-006
  region_datos TEXT NOT NULL,                            -- GUARDA-002 (residencia)
  estado       TEXT NOT NULL DEFAULT 'prospecto'         -- ciclo de vida: propuesto en DEC del esquema
               CHECK (estado IN ('prospecto','onboarding','activo','pausado','cerrado')),
  creado_utc   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS proyectos (
  id           TEXT PRIMARY KEY,
  cliente_id   TEXT NOT NULL REFERENCES clientes(id),
  capacidades  TEXT NOT NULL,                            -- JSON array de módulos (M1..M7 / ids de packages)
  plan_entrega TEXT NOT NULL,                            -- DEC-009 (Starter->basic firmado; resto 'PENDIENTE-#17')
  estado       TEXT NOT NULL DEFAULT 'propuesto'
               CHECK (estado IN ('propuesto','en-construccion','entregado','pausado','cerrado')),
  creado_utc   TEXT NOT NULL DEFAULT (datetime('now'))
);
