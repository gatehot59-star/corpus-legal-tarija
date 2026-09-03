-- Esquema del corpus legal boliviano. Generalizado a TODO el pais desde el dia uno.
--
-- La version anterior era Tarija-especifica: `sala`, `gestion` y `fuente` sueltos, pensados
-- para dos fuentes. Eso funciona hasta que entra el primer Codigo nacional y hay que migrar
-- 3.646 documentos. Este esquema separa lo que varia (jurisdiccion, organo, tipo de norma) de
-- lo que no (un documento tiene texto, procedencia verificable y vigencia).
--
-- Tres decisiones que existen por el agente, no por el humano:
--
-- 1. `uid` ESTABLE y legible: "nac-ley-1178-1990", "jur-tar-auto-supremo-as-0122-2026-2026".
--    Un agente que cita necesita un identificador que no cambie si se reindexa. Un rowid no
--    sirve: cambia al reconstruir.
-- 2. `sha256` y `fuente_url` en el MISMO registro que el texto. Una cita sin procedencia
--    verificable es una afirmacion, y este proyecto ya midio lo que cuesta eso.
-- 3. `vigente` y `derogada_por` explicitos y NULLABLES. NULL no es "vigente": es NO MEDIDO.
--    Un agente legal que asume vigencia por ausencia de dato da un consejo peligroso.

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- Registro de fuentes: cada nueva (Gaceta nacional, un municipio, el TCP) se agrega aca
-- sin tocar el resto del sistema.
CREATE TABLE IF NOT EXISTS fuentes (
  fuente_id     TEXT PRIMARY KEY,          -- tarija_gaceta, tsj_genesis, gaceta_nacional
  nombre        TEXT NOT NULL,
  jurisdiccion  TEXT NOT NULL,             -- nacional | departamental | municipal | jurisprudencia
  departamento  TEXT,                      -- NULL cuando es nacional
  organo        TEXT,                      -- Asamblea Legislativa Departamental, TSJ, ...
  url_base      TEXT,
  licencia      TEXT,
  actualizado   TEXT
);

CREATE TABLE IF NOT EXISTS documentos (
  doc_id        INTEGER PRIMARY KEY,
  uid           TEXT UNIQUE NOT NULL,      -- identificador estable y citable
  fuente_id     TEXT NOT NULL REFERENCES fuentes(fuente_id),
  jurisdiccion  TEXT NOT NULL,
  departamento  TEXT,
  organo        TEXT,
  tipo_norma    TEXT,                      -- Ley, Auto Supremo, Decreto Supremo, Sentencia
  numero        TEXT,
  anio          TEXT,
  fecha         TEXT,
  titulo        TEXT,
  materia       TEXT,                      -- Civil, Penal, Del Trabajo, Familia, ...
  sala          TEXT,                      -- solo jurisprudencia
  magistrado    TEXT,
  partes        TEXT,
  vigente       INTEGER,                   -- 1 si | 0 no | NULL NO MEDIDO
  derogada_por  TEXT,
  fuente_url    TEXT NOT NULL,
  sha256        TEXT,
  via_texto     TEXT,                      -- html_oficial | texto_nativo_pdf | ocr
  confianza     TEXT,                      -- alta | media | revision_humana
  chars         INTEGER,
  archivo       TEXT
);

CREATE INDEX IF NOT EXISTS ix_doc_jur    ON documentos(jurisdiccion);
CREATE INDEX IF NOT EXISTS ix_doc_dep    ON documentos(departamento);
CREATE INDEX IF NOT EXISTS ix_doc_tipo   ON documentos(tipo_norma);
CREATE INDEX IF NOT EXISTS ix_doc_mat    ON documentos(materia);
CREATE INDEX IF NOT EXISTS ix_doc_anio   ON documentos(anio);
CREATE INDEX IF NOT EXISTS ix_doc_num    ON documentos(numero);

-- El texto vive en chunks para que la busqueda devuelva el PARRAFO y no el documento entero:
-- un agente con ventana limitada no puede recibir 140.000 caracteres por resultado.
CREATE VIRTUAL TABLE IF NOT EXISTS chunks USING fts5(
  cuerpo,
  citas,            -- citas legales normalizadas (Art. 17.I aunque el OCR diga 17.1)
  encabezado,       -- numero, tipo, materia, partes: pesa mas en el ranking
  uid       UNINDEXED,
  doc_id    UNINDEXED,
  nro       UNINDEXED,
  tokenize = "unicode61 remove_diacritics 2"
);

-- Cola de revision humana, explicita y consultable. Un corpus legal sin esto miente por omision.
CREATE TABLE IF NOT EXISTS revision (
  id       INTEGER PRIMARY KEY,
  uid      TEXT NOT NULL,
  tipo     TEXT NOT NULL,      -- cita_ambigua | gate_no_pasa | vigencia_no_medida
  detalle  TEXT,
  contexto TEXT,
  resuelto INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_rev_uid ON revision(uid);
