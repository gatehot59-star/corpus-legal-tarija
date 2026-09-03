"""Busqueda sobre el indice FTS5 del corpus legal, con ranking BM25 y filtros.

Uso tipico de un estudio:
    python buscar.py --db corpus.db "prescripcion adquisitiva"
    python buscar.py --db corpus.db "Art. 17.I" --fuente jurisprudencia_tsj
    python buscar.py --db corpus.db "asistencia familiar" --sala "Sala Social 1era" --gestion 2024

El ranking pondera las columnas: `encabezado` pesa mas que `cuerpo` porque acertar el numero de
resolucion o la materia es una senal mas fuerte que una mencion suelta en el medio del texto.
"""
import argparse
import re
import sqlite3
import unicodedata


def plano(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s or ""))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def a_consulta_fts(q: str) -> str:
    """Convierte la consulta del usuario en sintaxis FTS5 sin que un caracter la rompa.

    FTS5 trata `.`, `/`, `-` y `"` como sintaxis, asi que "AS/0122/2026" o "Art. 17.I"
    explotan si se pasan crudos. Se citan los tokens y las frases entre comillas se respetan.
    """
    q = q.strip()
    frases = re.findall(r'"([^"]+)"', q)
    resto = re.sub(r'"[^"]+"', " ", q)
    partes = ['"' + f.replace('"', "") + '"' for f in frases]
    for token in re.split(r"\s+", resto):
        token = token.strip()
        if not token:
            continue
        # Cada token va entre comillas: eso lo vuelve literal para FTS5.
        partes.append('"' + token.replace('"', "") + '"')
    return " ".join(partes) if partes else '""'


def buscar(db: str, consulta: str, limite: int = 10, fuente: str = "", sala: str = "",
           gestion: str = "", materia: str = "") -> list:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    sql = [
        "SELECT d.archivo, d.fuente, d.numero, d.tipo_norma, d.gestion, d.sala, d.materia,",
        "       d.partes, d.titulo, c.nro_chunk,",
        "       bm25(chunks, 1.0, 3.0, 5.0) AS puntaje,",
        "       snippet(chunks, 0, '>>', '<<', ' ... ', 18) AS fragmento",
        "FROM chunks c JOIN documentos d ON d.doc_id = c.doc_id",
        "WHERE chunks MATCH ?",
    ]
    params = [a_consulta_fts(consulta)]
    for campo, valor in (("d.fuente", fuente), ("d.sala", sala),
                         ("d.gestion", gestion), ("d.materia", materia)):
        if valor:
            sql.append("AND " + campo + " = ?")
            params.append(valor)
    sql.append("ORDER BY puntaje LIMIT ?")
    params.append(limite)
    filas = con.execute("\n".join(sql), params).fetchall()
    con.close()
    return [dict(f) for f in filas]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("consulta")
    ap.add_argument("--db", required=True)
    ap.add_argument("--limite", type=int, default=10)
    ap.add_argument("--fuente", default="")
    ap.add_argument("--sala", default="")
    ap.add_argument("--gestion", default="")
    ap.add_argument("--materia", default="")
    a = ap.parse_args()

    import time
    t0 = time.time()
    filas = buscar(a.db, a.consulta, a.limite, a.fuente, a.sala, a.gestion, a.materia)
    ms = (time.time() - t0) * 1000

    print(f'"{a.consulta}" -> {len(filas)} resultados en {ms:.0f} ms')
    for i, f in enumerate(filas, start=1):
        cab = " | ".join(str(x) for x in (f["numero"], f["tipo_norma"], f["sala"],
                                         f["materia"], f["gestion"]) if x)
        print(f"\n{i}. {cab}")
        if f["partes"]:
            print("   partes: " + str(f["partes"])[:110])
        print("   " + f["archivo"] + " (chunk " + str(f["nro_chunk"])
              + ", bm25 " + str(round(f["puntaje"], 2)) + ")")
        frag = re.sub(r"\s+", " ", f["fragmento"] or "")
        print("   " + frag[:260])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
