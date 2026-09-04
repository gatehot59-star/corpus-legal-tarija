#!/usr/bin/env python3
"""Parche EXACTO del auditor: paginacion real, permalink por pasaje, estado en la
URL, historial del navegador, numeracion global y fallo de portapapeles VISIBLE.

Entrada:  index.html md5 9881bb62a5394ce596b208d398ec0c4c
          (el desplegado LIMPIO, sin las dos inyecciones de la tanda anterior)
Salida:   index.html con los 10 reemplazos exactos aplicados. Un solo <script>.

Si un ancla no aparece exactamente una vez, ROJO y NO escribe nada. El script
no adivina: mide el archivo que le dan.
"""
import hashlib, sys

VIEJO = "9881bb62a5394ce596b208d398ec0c4c"

CSS = """
/* --- paginacion, enlace directo por pasaje y fallo de copia visible --- */
.paginacion{display:flex;flex-wrap:wrap;align-items:center;gap:.35rem;margin:2.4rem 0 .4rem;padding-top:1.3rem;border-top:1px solid var(--linea)}
.paginacion button{font-family:var(--mono);font-size:.72rem;letter-spacing:.04em;color:var(--graf);background:transparent;border:1px solid var(--linea);padding:.34rem .6rem;cursor:pointer;transition:border-color .15s,color .15s}
.paginacion button:hover:not(:disabled){border-color:var(--sello);color:var(--sello)}
.paginacion button:disabled{opacity:.32;cursor:default}
.paginacion button.on{border-color:var(--vino);color:var(--vino)}
.paginacion .hueco{font-family:var(--mono);font-size:.72rem;color:var(--graf);opacity:.55;padding:0 .1rem}
.paginacion .tope{font-family:var(--mono);font-size:.66rem;color:var(--graf);margin-left:auto;border-bottom:1px dotted var(--linea-fuerte);cursor:help}
.acciones button.falla{border-color:var(--vino);color:var(--vino)}
.cargo.apuntado{outline:2px solid var(--sello);outline-offset:6px}
</style>"""

ESTADO = """let filtros = {}, ultima = "", pagina = 1;
const POR_PAGINA = 12, TOPE_OFFSET = 10000;
const TOPE_PAGINA = Math.floor(TOPE_OFFSET / POR_PAGINA) + 1;

/* --- el estado vive en la URL: consulta, pagina, filtros y pasaje abierto.
   Un enlace pegado en un escrito tiene que volver al MISMO pasaje, no a la
   portada. Y el boton atras del navegador tiene que deshacer la pagina. --- */
function urlEstado(q, p, f, abrir){
  const u = new URL(location.origin + location.pathname);
  if (q) u.searchParams.set("q", q);
  if (p && p > 1) u.searchParams.set("p", String(p));
  for (const k in (f || {})) u.searchParams.set(k, f[k]);
  if (abrir) u.searchParams.set("abrir", abrir);
  return u.toString();
}
function sincronizar(q, p, f, abrir, reemplazar){
  const url = urlEstado(q, p, f, abrir);
  if (url === location.href) return;
  try{
    if (reemplazar) history.replaceState({q: q, p: p}, "", url);
    else history.pushState({q: q, p: p}, "", url);
  }catch(e){}
}
function leerEstado(){
  const s = new URLSearchParams(location.search);
  const f = {};
  for (const g of GRUPOS) if (s.get(g[0])) f[g[0]] = s.get(g[0]);
  const p = Math.max(1, Math.min(TOPE_PAGINA, parseInt(s.get("p") || "1", 10) || 1));
  return {q: (s.get("q") || "").trim(), p: p, filtros: f, abrir: s.get("abrir") || ""};
}"""

AYUDAS = """/* --- navegador de paginas: sin esto el abogado ve 12 de 1.741 y cree que eso
   es todo lo que hay. La API corta en 10.000 pasajes y eso se DICE. --- */
function navegador(paginas){
  if (paginas <= 1) return "";
  const ventana = [];
  const a = Math.max(1, pagina - 2), b = Math.min(paginas, pagina + 2);
  if (a > 1) ventana.push(1);
  if (a > 2) ventana.push(null);
  for (let i = a; i <= b; i++) ventana.push(i);
  if (b < paginas - 1) ventana.push(null);
  if (b < paginas) ventana.push(paginas);
  const partes = [];
  partes.push('<button type="button" data-pag="' + Math.max(1, pagina - 1) + '"' + (pagina <= 1 ? " disabled" : "") + ">\\u2190 anterior</button>");
  for (const p of ventana){
    if (p === null) partes.push('<span class="hueco">\\u2026</span>');
    else partes.push('<button type="button" data-pag="' + p + '"' + (p === pagina ? ' class="on" aria-current="page"' : "") + ">" + nf(p) + "</button>");
  }
  partes.push('<button type="button" data-pag="' + Math.min(paginas, pagina + 1) + '"' + (pagina >= paginas ? " disabled" : "") + ">siguiente \\u2192</button>");
  if (paginas >= TOPE_PAGINA)
    partes.push('<span class="tope" title="La API corta el desplazamiento en ' + nf(TOPE_OFFSET) + ' pasajes. Mas alla de la pagina ' + nf(TOPE_PAGINA) + ' hay que afinar la consulta, no seguir avanzando.">tope de la API</span>');
  return '<nav class="paginacion" aria-label="Paginas de resultados">' + partes.join("") + "</nav>";
}

/* --- portapapeles: si falla, se DICE. Un "copiado" falso hace que el abogado
   pegue en el escrito lo que tenia antes en el portapapeles. --- */
async function copiar(b, texto, ok){
  const t = b.dataset.rotulo || b.textContent;
  b.dataset.rotulo = t;
  let bien = false;
  try{
    if (navigator.clipboard && navigator.clipboard.writeText){
      await navigator.clipboard.writeText(texto); bien = true;
    }
  }catch(e){ bien = false; }
  if (!bien){
    try{
      const ta = document.createElement("textarea");
      ta.value = texto; ta.setAttribute("readonly", "");
      ta.style.position = "fixed"; ta.style.top = "-1000px"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      bien = document.execCommand("copy");
      ta.remove();
    }catch(e){ bien = false; }
  }
  b.classList.toggle("falla", !bien);
  b.textContent = bien ? ok : "no se pudo copiar";
  b.title = bien ? "" : "El navegador bloqueo el portapapeles. El enlace esta en la barra de direcciones: copialo de ahi.";
  setTimeout(() => { b.textContent = t; b.classList.remove("falla"); b.title = ""; }, bien ? 1600 : 3400);
}

/* --- permalink: abre el pasaje exacto que pidio el enlace --- */
function abrirPasaje(clave){
  const art = Array.from(document.querySelectorAll("[data-clave]")).find(a => a.dataset.clave === clave);
  if (!art) return false;
  art.classList.add("apuntado");
  art.scrollIntoView({behavior: "smooth", block: "center"});
  const b = art.querySelector("[data-leer]");
  if (b) b.click();
  return true;
}

/* --- buscar --- */"""

R = [
 # 1. CSS de la paginacion
 ("\n</style>", CSS),
 # 2. estado + helpers de URL
 ('let filtros = {}, ultima = "";', ESTADO),
 # 3. quitar un filtro vuelve a la pagina 1
 ('  if (lp) lp.onclick = () => { filtros = {}; buscar(ultima); };',
  '  if (lp) lp.onclick = () => { filtros = {}; buscar(ultima, 1); };'),
 # 4. tocar una faceta vuelve a la pagina 1
 ('    if (ultima) buscar(ultima); else pintarRail(fac, inicial);',
  '    if (ultima) buscar(ultima, 1); else pintarRail(fac, inicial);'),
 # 5. numeracion GLOBAL y clave del pasaje
 ("""function ficha(r, i){
  const tit = [r.tipo_norma, r.numero].filter(Boolean).join(" ") || (r.titulo || r.uid);""",
  """function ficha(r, i){
  const n = (pagina - 1) * POR_PAGINA + i + 1;
  const clave = r.uid + "|" + r.nro;
  const enlace = urlEstado(ultima, pagina, filtros, clave);
  const tit = [r.tipo_norma, r.numero].filter(Boolean).join(" ") || (r.titulo || r.uid);"""),
 # 6. el numero de orden es el global, no el de la pagina
 ("""  return `<article class="cargo" style="animation-delay:${i*38}ms">
    <div class="orden">${String(i+1).padStart(2,"0")}</div>""",
  """  return `<article class="cargo" data-clave="${esc(clave)}" style="animation-delay:${i*38}ms">
    <div class="orden">${String(n).padStart(2,"0")}</div>"""),
 # 7. boton de enlace directo en cada ficha
 ("""          <button type="button" data-cita="${esc(citaFormal(r))}">copiar cita</button>""",
  """          <button type="button" data-cita="${esc(citaFormal(r))}">copiar cita</button>
          <button type="button" data-enlace="${esc(enlace)}" title="Enlace directo a este pasaje: abre esta misma b\u00fasqueda, en esta p\u00e1gina, con el texto desplegado.">copiar enlace</button>"""),
 # 8. ayudas antes de buscar
 ("/* --- buscar --- */", AYUDAS),
 # 9. buscar acepta pagina y pide offset
 ("""async function buscar(q){
  q = (q || "").trim();
  if (!q) return;
  ultima = q; $("#q").value = q;""",
  """async function buscar(q, p, opc){
  q = (q || "").trim();
  if (!q) return;
  opc = opc || {};
  ultima = q;
  pagina = Math.max(1, Math.min(TOPE_PAGINA, parseInt(p || 1, 10) || 1));
  $("#q").value = q;"""),
 # 10. offset en la llamada
 ("""  u.searchParams.set("q", q); u.searchParams.set("limit", "12");""",
  """  u.searchParams.set("q", q); u.searchParams.set("limit", String(POR_PAGINA));
  u.searchParams.set("offset", String((pagina - 1) * POR_PAGINA));"""),
 # 11. la medicion dice el rango global y la pagina
 ("""    $("#medicion").innerHTML = nf_
      ? `<b>${nf(d.total_pasajes)}</b> pasajes para el t\u00e9rmino \u00b7 mostrando <b>${d.devueltos}</b> con el filtro \u00b7 <b>${d.ms}</b> ms${esc(fl)}`
      : `<b>${nf(d.total_pasajes)}</b> pasajes \u00b7 mostrando ${d.devueltos} \u00b7 <b>${d.ms}</b> ms`;""",
  """    const paginas = Math.max(1, Math.min(TOPE_PAGINA, Math.ceil((d.total_pasajes || 0) / POR_PAGINA)));
    const desde = d.total_pasajes ? (pagina - 1) * POR_PAGINA + 1 : 0;
    const hasta = (pagina - 1) * POR_PAGINA + (d.devueltos || 0);
    $("#medicion").innerHTML =
      `<b>${nf(d.total_pasajes)}</b> pasajes${nf_ ? " para el t\u00e9rmino" : ""}${esc(fl)} \u00b7 mostrando <b>${nf(desde)}\u2013${nf(hasta)}</b> \u00b7 p\u00e1gina <b>${nf(pagina)}</b> de <b>${nf(paginas)}</b> \u00b7 <b>${d.ms}</b> ms`;"""),
 # 12. render con paginacion, permalink, copia con error real y URL sincronizada
 ("""    $("#registro").innerHTML = d.resultados.map(ficha).join("");
    document.querySelectorAll("[data-leer]").forEach(b => b.onclick = () => leer(b.dataset.leer, b.dataset.nro, b));
    document.querySelectorAll("[data-cita]").forEach(b => b.onclick = async () => {
      try{ await navigator.clipboard.writeText(b.dataset.cita); }catch(e){}
      const t = b.textContent; b.textContent = "cita copiada \u2713";
      setTimeout(() => b.textContent = t, 1600);
    });""",
  """    $("#registro").innerHTML = d.resultados.map(ficha).join("") + navegador(paginas);
    document.querySelectorAll("[data-leer]").forEach(b => b.onclick = () => leer(b.dataset.leer, b.dataset.nro, b));
    document.querySelectorAll("[data-cita]").forEach(b => b.onclick = () => copiar(b, b.dataset.cita, "cita copiada \u2713"));
    document.querySelectorAll("[data-enlace]").forEach(b => b.onclick = () => copiar(b, b.dataset.enlace, "enlace copiado \u2713"));
    document.querySelectorAll("[data-pag]").forEach(b => b.onclick = () => buscar(ultima, parseInt(b.dataset.pag, 10)));
    sincronizar(q, pagina, filtros, "", !!opc.reemplazar);
    if (opc.abrir) abrirPasaje(opc.abrir);"""),
 # 13. pagina fuera de rango: cae en la ultima que existe, no en el vacio
 ("""    if (!d.resultados.length){
      $("#registro").innerHTML = `<div class="aviso"><h2>Sin coincidencias para \u00ab${esc(q)}\u00bb${fl?" con esos filtros":""}.</h2>""",
  """    if (!d.resultados.length && d.total_pasajes > 0 && pagina > 1){
      return buscar(q, Math.min(TOPE_PAGINA, Math.ceil(d.total_pasajes / POR_PAGINA)), {reemplazar: true});
    }
    if (!d.resultados.length){
      $("#registro").innerHTML = `<div class="aviso"><h2>Sin coincidencias para \u00ab${esc(q)}\u00bb${fl?" con esos filtros":""}.</h2>"""),
 # 14. una consulta nueva arranca en la pagina 1
 ("""$("#form").addEventListener("submit", e => { e.preventDefault(); buscar($("#q").value); });
$("#sugeridas").addEventListener("click", e => {
  if (e.target.tagName === "BUTTON"){ filtros = {}; buscar(e.target.textContent); }
});""",
  """$("#form").addEventListener("submit", e => { e.preventDefault(); buscar($("#q").value, 1); });
$("#sugeridas").addEventListener("click", e => {
  if (e.target.tagName === "BUTTON"){ filtros = {}; buscar(e.target.textContent, 1); }
});"""),
 # 15. arranque desde la URL y boton atras
 ('censo(); $("#q").focus();',
  """/* --- arranque: manda la URL. Y atras/adelante del navegador tienen que
   devolver la pagina que el abogado estaba leyendo. --- */
window.addEventListener("popstate", () => {
  const e = leerEstado();
  filtros = e.filtros;
  if (e.q) buscar(e.q, e.p, {reemplazar: true, abrir: e.abrir});
  else {
    ultima = ""; pagina = 1;
    $("#q").value = ""; $("#medicion").textContent = "";
    $("#registro").innerHTML = INICIO;
    censo();
  }
});
const INICIO = $("#registro").innerHTML;
censo();
const arranque = leerEstado();
filtros = arranque.filtros;
if (arranque.q) buscar(arranque.q, arranque.p, {reemplazar: true, abrir: arranque.abrir});
else $("#q").focus();"""),
]

VERDES = ['u.searchParams.set("offset"', "data-enlace", "data-pag=", "data-clave",
          "popstate", "execCommand", "function navegador", "function copiar",
          "function abrirPasaje", "TOPE_PAGINA", "leerEstado", "sincronizar"]

def main(ruta):
    h = open(ruta, encoding="utf8").read()
    a = hashlib.md5(h.encode()).hexdigest()
    print("entrada md5", a, len(h), "bytes")
    if a != VIEJO:
        print("ROJO: no es la base limpia esperada", VIEJO)
        return 1
    for i, (v, n) in enumerate(R, 1):
        c = h.count(v)
        if c != 1:
            print("ROJO: ancla", i, "aparece", c, "veces:", v[:60].replace("\n", " "))
            return 1
        h = h.replace(v, n, 1)
        print("  ancla", i, "aplicada")
    for t in VERDES:
        if t not in h:
            print("ROJO: falta en la salida:", t)
            return 1
    if h.count("<script") != 1:
        print("ROJO: hay", h.count("<script"), "bloques de script; el limpio tiene 1")
        return 1
    for prohibido in ("paginacion_inject", "permalink_inject"):
        if prohibido in h:
            print("ROJO: quedo una inyeccion:", prohibido)
            return 1
    open(ruta, "w", encoding="utf8").write(h)
    print("VERDE salida md5", hashlib.md5(h.encode()).hexdigest(), len(h), "bytes")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "index.html"))
