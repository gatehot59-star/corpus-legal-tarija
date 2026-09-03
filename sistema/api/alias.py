"""Alias de procedencia para deduplicación por contenido.

Un mismo texto puede aparecer en varias fuentes o gestiones. No se elimina la referencia:
se conserva cada procedencia en ``documento_aliases`` y el documento canónico queda indexado una
sola vez. Esto evita que el contador de deduplicados se confunda con pérdida de cobertura.
"""
from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterable

DDL = """
CREATE TABLE IF NOT EXISTS documento_aliases (
  alias_id INTEGER PRIMARY KEY,
  doc_id INTEGER NOT NULL REFERENCES documentos(doc_id) ON DELETE CASCADE,
  uid TEXT NOT NULL,
  fuente_id TEXT NOT NULL,
  fuente_url TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  archivo TEXT,
  UNIQUE(fuente_id, fuente_url, sha256),
  UNIQUE(uid, fuente_id, fuente_url)
);
CREATE INDEX IF NOT EXISTS ix_alias_doc ON documento_aliases(doc_id);
CREATE INDEX IF NOT EXISTS ix_alias_hash ON documento_aliases(sha256);
"""


def instalar(con: sqlite3.Connection) -> None:
    """Instala la tabla idempotentemente en una base existente o nueva."""
    con.executescript(DDL)
    con.commit()


def registrar(con: sqlite3.Connection, *, doc_id: int, uid: str, fuente_id: str,
              fuente_url: str, texto: str, archivo: str = "") -> bool:
    """Registra una procedencia y devuelve True si era nueva."""
    sha256 = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    cur = con.execute(
        "INSERT OR IGNORE INTO documento_aliases "
        "(doc_id, uid, fuente_id, fuente_url, sha256, archivo) VALUES (?,?,?,?,?,?)",
        (doc_id, uid, fuente_id, fuente_url, sha256, archivo),
    )
    return cur.rowcount == 1


def por_hash(con: sqlite3.Connection, sha256: str) -> list[sqlite3.Row]:
    """Devuelve todas las procedencias que comparten contenido, sin perder ninguna."""
    return con.execute(
        "SELECT a.*, d.titulo, d.tipo_norma, d.numero "
        "FROM documento_aliases a JOIN documentos d ON d.doc_id=a.doc_id "
        "WHERE a.sha256=? ORDER BY a.alias_id", (sha256,)
    ).fetchall()


def auditar(con: sqlite3.Connection) -> dict[str, int]:
    """Cuenta documentos canónicos, alias y hashes repetidos para el informe de ingesta."""
    docs = con.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
    aliases = con.execute("SELECT COUNT(*) FROM documento_aliases").fetchone()[0]
    repetidos = con.execute(
        "SELECT COUNT(*) FROM (SELECT sha256 FROM documento_aliases GROUP BY sha256 HAVING COUNT(*)>1)"
    ).fetchone()[0]
    return {"documentos_canonicos": docs, "alias_procedencia": aliases,
            "hashes_con_multiples_procedencias": repetidos}
