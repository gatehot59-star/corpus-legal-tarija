"""SQLite en WAL: los UPDATE fueron al -wal y el .db quedo con el md5 viejo.
Sin checkpoint, copiar el .db al servidor copia la base SIN los cambios."""
import os, sqlite3, sys
DB = os.environ.get("RAG_DB", "/workspace/bolivia-v7.db")
print("antes:", os.path.getsize(DB), "bytes | wal:",
      os.path.getsize(DB + "-wal") if os.path.exists(DB + "-wal") else "no hay")
c = sqlite3.connect(DB)
print("modo:", c.execute("PRAGMA journal_mode").fetchone()[0])
print("checkpoint:", c.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone())
c.execute("VACUUM")
c.close()
print("despues:", os.path.getsize(DB), "bytes | wal:",
      os.path.getsize(DB + "-wal") if os.path.exists(DB + "-wal") else "no hay")
c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
print("documentos:", c.execute("SELECT count(*) FROM documentos").fetchone()[0],
      "| chunks:", c.execute("SELECT count(*) FROM chunks").fetchone()[0],
      "| titulos-slug:", c.execute("SELECT count(*) FROM documentos WHERE titulo LIKE '%start=%'").fetchone()[0],
      "| con vigencia:", c.execute("SELECT count(*) FROM documentos WHERE vigente IS NOT NULL").fetchone()[0])
