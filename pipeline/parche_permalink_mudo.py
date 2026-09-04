#!/usr/bin/env python3
"""ROJO medido: un permalink cuyo pasaje no cae en la pagina pedida NO decia nada.
La pagina cargaba, la busqueda corria, y el lector se quedaba cerrado como si el
enlace no hubiera pedido nada. Un fallo silencioso es peor que un error visible:
el abogado cree que abrio el pasaje que le mandaron.

Ahora, si no lo encuentra, la interfaz lo DICE arriba del registro, con el numero
de pasaje pedido y que hacer. Y si esta en otra pagina de la misma consulta, lo
busca antes de rendirse: recorre hasta 12 paginas mas por la API (no por el DOM)
y salta directo a la pagina donde vive.

Entrada index.html md5 a1c126f8757f7746162023e677ed42e7
"""
import hashlib, sys

VIEJO = "a1c126f8757f7746162023e677ed42e7"

CSS = """
.enlace-roto{border:1px solid var(--vino);border-left-width:3px;padding:.85rem 1rem;margin:0 0 1.6rem;background:rgba(158,42,64,.045)}
.enlace-roto b{color:var(--vino)}
.enlace-roto p{margin:.3rem 0 0;font-size:.84rem;color:var(--graf);line-height:1.5}
.enlace-roto button{margin-top:.55rem;font-family:var(--mono);font-size:.7rem;letter-spacing:.04em;color:var(--vino);background:transparent;border:1px solid var(--vino);padding:.3rem .6rem;cursor:pointer}
html[data-modo="noche"] .enlace-roto{background:rgba(212,120,140,.07)}
</style>"""

BUSCADOR = """/* --- un permalink que no encuentra su pasaje NO puede callarse. Primero lo busca
   en las otras paginas de la misma consulta (por la API, no por el DOM), y si
   tampoco esta, lo dice con el numero de pasaje y el termino. --- */
const PAGINAS_A_REVISAR = 12;
async function ubicarPasaje(clave, q, f){
  const corte = clave.lastIndexOf("|");
  if (corte < 0) return null;
  const uid = clave.slice(0, corte), nro = clave.slice(corte + 1);
  for (let p = 1; p <= PAGINAS_A_REVISAR; p++){
    const u = new URL(API + "/buscar");
    u.searchParams.set("q", q);
    u.searchParams.set("limit", String(POR_PAGINA));
    u.searchParams.set("offset", String((p - 1) * POR_PAGINA));
    for (const k in (f || {})) u.searchParams.set(k, f[k]);
    let d;
    try{ d = await (await fetch(u)).json(); }catch(e){ return null; }
    if (d.error || !d.resultados || !d.resultados.length) return null;
    if (d.resultados.some(r => r.uid === uid && String(r.nro) === String(nro))) return p;
    if ((p * POR_PAGINA) >= (d.total_pasajes || 0)) return null;
  }
  return null;
}
function avisarEnlaceRoto(clave, q){
  const corte = clave.lastIndexOf("|");
  const nro = corte < 0 ? "?" : clave.slice(corte + 1);
  const uid = corte < 0 ? clave : clave.slice(0, corte);
  const aviso = document.createElement("div");
  aviso.className = "enlace-roto";
  aviso.innerHTML = `<b>El enlace apuntaba a un pasaje que no est\\u00e1 en estos resultados.</b>
    <p>Ped\\u00eda el pasaje <b>${esc(nro)}</b> del documento <s>${esc(uid)}</s> para la b\\u00fasqueda \\u00ab${esc(q)}\\u00bb,
    y no aparece en las primeras ${nf(PAGINAS_A_REVISAR * POR_PAGINA)} coincidencias. Abajo est\\u00e1n los
    resultados de esa b\\u00fasqueda, sin ese pasaje desplegado.</p>
    <button type="button" data-ver-doc="${esc(uid)}" data-ver-nro="${esc(nro)}">abrir ese documento igual</button>`;
  const reg = $("#registro");
  reg.insertBefore(aviso, reg.firstChild);
  const b = aviso.querySelector("[data-ver-doc]");
  b.onclick = async () => {
    b.textContent = "abriendo\\u2026";
    const u = new URL(API + "/texto");
    u.searchParams.set("uid", b.dataset.verDoc); u.searchParams.set("nro", b.dataset.verNro);
    try{
      const d = await (await fetch(u)).json();
      if (d.error){ b.textContent = "ese documento no existe"; return; }
      const doc = d.documento || {};
      const tit = [doc.tipo_norma, doc.numero].filter(Boolean).join(" ") || b.dataset.verDoc;
      const caja = document.createElement("div");
      caja.className = "lector";
      caja.innerHTML = `<div class="lector-cab"><span>${esc(tit)} \\u00b7 texto continuo \\u00b7
        <b>${nf(d.desde)}</b>\\u2013<b>${nf(d.hasta)}</b> de <b>${nf(d.total_caracteres)}</b> caracteres</span>
        <button type="button" class="cerrar" data-cerrar="1">cerrar \\u2715</button></div>
        <div class="lector-cuerpo">${resaltar(d.cuerpo || "", ultima)}</div>`;
      aviso.appendChild(caja);
      caja.querySelector("[data-cerrar]").onclick = () => { caja.remove(); b.textContent = "abrir ese documento igual"; };
      b.textContent = "documento abierto";
    }catch(e){ b.textContent = "no se pudo abrir"; }
  };
}
async function abrirPasajeOAvisar(clave, q, f){
  if (abrirPasaje(clave)) return;
  const p = await ubicarPasaje(clave, q, f);
  if (p && p !== pagina){ return buscar(q, p, {reemplazar: true, abrir: clave, sinReintento: true}); }
  if (p && abrirPasaje(clave)) return;
  avisarEnlaceRoto(clave, q);
}

/* --- buscar --- */"""

R = [
 (
  "\n</style>",
  CSS,
 ),
 (
  "/* --- buscar --- */",
  BUSCADOR,
 ),
 (
  "    if (opc.abrir) abrirPasaje(opc.abrir);",
  "    if (opc.abrir){\n"
  "      if (opc.sinReintento) { if (!abrirPasaje(opc.abrir)) avisarEnlaceRoto(opc.abrir, q); }\n"
  "      else abrirPasajeOAvisar(opc.abrir, q, filtros);\n"
  "    }",
 ),
]

VERDES = ["function ubicarPasaje", "function avisarEnlaceRoto", "abrirPasajeOAvisar",
          "sinReintento", "enlace-roto", "data-ver-doc", "PAGINAS_A_REVISAR"]

def main(ruta):
    h = open(ruta, encoding="utf8").read()
    a = hashlib.md5(h.encode()).hexdigest()
    print("entrada md5", a, len(h), "caracteres")
    if a != VIEJO:
        print("ROJO: entrada inesperada, esperaba", VIEJO); return 1
    for i, (v, n) in enumerate(R, 1):
        c = h.count(v)
        if c != 1:
            print("ROJO: ancla", i, "aparece", c, "veces:", v[:50].replace("\n", " ")); return 1
        h = h.replace(v, n, 1)
        print("  ancla", i, "aplicada")
    for t in VERDES:
        if t not in h:
            print("ROJO: falta en la salida:", t); return 1
    if h.count("<script") != 1:
        print("ROJO: hay", h.count("<script"), "bloques de script"); return 1
    if h.count("abrirPasaje(opc.abrir)") > 1:
        print("ROJO: quedo el llamado viejo suelto"); return 1
    open(ruta, "w", encoding="utf8").write(h)
    print("VERDE salida md5", hashlib.md5(h.encode()).hexdigest(), len(h), "caracteres")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "index.html"))
