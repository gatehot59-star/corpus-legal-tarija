"""Alias de procedencia para deduplicación por contenido.

Un mismo texto puede aparecer en varias fuentes, gestiones o archivos. No se elimina la
referencia: se conserva cada procedencia en ``documento_aliases`` y el documento canónico queda
indexado una sola vez. Esto evita que el contador de deduplicados se confunda con pérdida de
cobertura, que es exactamente lo que pasó cuando 40 documentos se reportaron como reemplazados.

**Esta tabla es la única fuente de verdad de su propio esquema**: no se declara en
``esquema.sql``. ``Corpus.__init__`` llama a ``instalar()`` en cada apertura, así que una base
vieja la gana sin migración manual. Ninguna base en producción la tenía antes de este cambio,
así que no hay filas que migrar.

**Por qué el archivo entra en la clave de unicidad:** la Gaceta de Tarija cae a una
``fuente_url`` genérica cuando el registro no trae la propia, así que dos archivos distintos con
el mismo texto compartían ``(fuente_id, fuente_url, sha256)`` y la segunda procedencia se
perdía en silencio. El silencio es el modo de falla que este módulo existe para cerrar.
"""
from __future__ import annotations

import hashlib
import sqlite3

DDL = """
CREATE TABLE IF NOT EXISTS documento_aliases (
  alias_id INTEGER PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documentos(doc_id) ON DELETE CASCADE,
  uid TEXT NOT NULL,
  fuente_id TEXT NOT NULL,
  fuente_url TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  archivo TEXT NOT NULL DEFAULT '',
  UNIQUE(fuente_id, fuente_url, archivo, sha256)
);
CREATE INDEX IF NOT EXISTS ix_alias_doc ON documento_aliases(doc_id);
CREATE INDEX IF NOT EXISTS ix_alias_hash ON documento_aliases(sha256);
CREATE INDEX IF NOT EXISTS ix_alias_uid ON documento_aliases(uid);
"""


def instalar(con: sqlite3.Connection) -> None:
    """Instala la tabla idempotentemente, en una base nueva o ya existente."""
    con.executescript(DDL)
    con.commit()


def sha256_de(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def registrar(con: sqlite3.Connection, *, doc_id: int, uid: str, fuente_id: str,
              fuente_url: str, texto: str = "", archivo: str = "",
              sha256: str = "") -> bool:
    """Registra una procedencia. Devuelve True si era nueva, False si ya estaba.

    El False no es un error: es el reintento exacto de una reingesta, y la ingesta lo cuenta
    aparte para que su invariante siga cerrando sin inflar el total.
    """
    cur = con.execute(
        "INSERT OR IGNORE INTO documento_aliases "
        "(doc_id, uid, fuente_id, fuente_url, sha256, archivo) VALUES (?,?,?,?,?,?)",
        (doc_id, uid, fuente_id, fuente_url, sha256 or sha256_de(texto), archivo or ""),
    )
    return cur.rowcount == 1


def por_hash(con: sqlite3.Connection, sha256: str) -> list[sqlite3.Row]:
    """Todas las procedencias que comparten un mismo contenido, sin perder ninguna."""
    return con.execute(
        "SELECT a.*, d.titulo, d.tipo_norma, d.numero "
        "FROM documento_aliases a JOIN documentos d ON d.doc_id = a.doc_id "
        "WHERE a.sha256 = ? ORDER BY a.alias_id", (sha256,)
    ).fetchall()


def por_uid(con: sqlite3.Connection, uid: str) -> list[sqlite3.Row]:
    """Las procedencias de un documento citable, para que la cita nombre todas sus fuentes."""
    return con.execute(
        "SELECT fuente_id, fuente_url, archivo, sha256 FROM documento_aliases "
        "WHERE uid = ? ORDER BY alias_id", (uid,)
    ).fetchall()


def auditar(con: sqlite3.Connection) -> dict[str, int]:
    """Documentos canónicos, alias y contenidos con más de una procedencia."""
    docs = con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
    aliases = con.execute("SELECT COUNT(*) FROM documento_aliases").fetchone()[0]
    repetidos = con.execute(
        "SELECT COUNT(*) FROM (SELECT sha256 FROM documento_aliases "
        "GROUP BY sha256 HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    huerfanos = con.execute(
        "SELECT COUNT(*) FROM documentos d WHERE NOT EXISTS "
        "(SELECT 1 FROM documento_aliases a WHERE a.doc_id = d.doc_id)"
    ).fetchone()[0]
    return {"documentos_canonicos": docs, "alias_procedencia": aliases,
            "hashes_con_multiples_procedencias": repetidos,
            "documentos_sin_procedencia": huerfanos}
