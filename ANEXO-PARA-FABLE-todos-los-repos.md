# ANEXO al reporte para Fable 5.1 · el paquete completo

**Medido:** 2026-09-09 18:04 UTC
**Por qué existe:** Abraham tiene razón. El reporte anterior apuntaba a **un** repo, y un auditor externo necesita **todo el terreno**, más la advertencia de qué no va a poder leer.

---

# 1 · QUÉ PUEDE CLONAR FABLE, Y QUÉ NO

Ocho repos en la cuenta `gatehot59-star`. Medido por API, no de memoria:

| Repo | Visibilidad | Lenguaje | Issues | Creado | ¿Fable lo lee? |
|---|---|---|---|---|---|
| **corpus-legal-tarija** | **público** | Python | 1 | 03-sep | **SÍ** ← el sujeto auditado |
| **siao** | **público** | Python | 0 | 05-sep | **SÍ** |
| **correai** | **público** | Go | 5 | 07-sep | **SÍ** |
| **cashgo** | **público** | — | 1 | 07-sep | **SÍ** |
| **icca-engine** | **público** | — | 6 | 22-ago | **SÍ** |
| **drosophila-fep-connectome** | **público** | Python | 5 | 23-ago | **SÍ** |
| **mudh-mobile** | **PRIVADO** | Kotlin | **50** | 16-ago | **NO** |
| **dualbrain** | **PRIVADO** | C | 0 | 25-ago | **NO** |

```bash
# los seis que Fable puede clonar sin credencial
for r in corpus-legal-tarija siao correai cashgo icca-engine drosophila-fep-connectome; do
  git clone --depth 20 https://github.com/gatehot59-star/$r
done
```

## Los dos privados: qué hacer

`mudh-mobile` y `dualbrain` **no son clonables** por un auditor externo. Tres opciones, y la decisión es de Abraham:

1. **Pasarlos a público.** Es un toggle. `mudh-mobile` tiene el método de trabajo, el inventario de máquinas y 50 issues: es el repo con más contexto de todos.
2. **Extraer lo auditable** a un anexo público (yo lo escribo, pero entonces **yo elijo qué mostrar**, y eso contamina la auditoría).
3. **Declararlos fuera de alcance** y que Fable audite solo lo público, con el hueco escrito.

**Mi recomendación: la 1 para `mudh-mobile`**, porque la opción 2 me deja curando la evidencia sobre la que me juzgan, y eso es exactamente el patrón que un auditor externo viene a romper.

**Advertencia de seguridad antes de tocar nada:** `mudh-mobile` tiene un **PAT de GitHub en texto plano** en la URL del remoto de mi copia de trabajo. No sé si también hay secretos **dentro** del historial. Antes de hacer público ese repo hay que correr un escaneo de secretos sobre el historial completo. **NO MEDIDO por mí** y es bloqueante para la opción 1.

---

# 2 · TRES COSAS QUE ME REFUTAN, y aparecieron al medir esto

## R1 · `siao` ya es PÚBLICO y yo lo declaré privado

El 6-sep escribí en dos entregas que `siao` era **privado**, y usé eso como argumento técnico ("en privado el runner es la mitad de máquina"). **Hoy es público.** Cambió y no lo verifiqué: repetí un dato de hace tres días como si fuera estado actual.

**Consecuencia concreta:** mi propia advertencia sobre cuota de Actions en `siao` **ya no aplica**, y el runner ahí es gratis e ilimitado. Un dato mio vencido que seguía circulando.

## R2 · Aparecieron DOS repos que no sabía que existían

`correai` (Go, 5 issues) y `cashgo`, **los dos creados el 7-sep**. Yo estuve ausente del 6 al 9 y **el proyecto siguió sin mí**. No tengo idea de qué hay adentro y no lo voy a suponer.

**Para la auditoría importa** porque si `correai` comparte código o infraestructura con el corpus, eso es superficie que mi reporte **no cubre**.

## R3 · `mudh-mobile` pasó de 48 a 50 issues

Lo medí en 48 el 6-sep. Hoy son **50**, y su último push es de **hoy 17:37 UTC**, veinte minutos antes de que yo escribiera el reporte. **Hubo trabajo ahí hoy y no lo leí antes de reportar.**

---

# 3 · CONTEXTO MÍNIMO DE LOS OTROS REPOS

Lo pongo para que Fable sepa dónde mirar, **no** como afirmación de contenido. Lo que no medí hoy va marcado.

| Repo | Qué es | ¿Medido hoy? |
|---|---|---|
| `siao` | SO móvil AI-first: la IA es el sistema, Android baja a inquilino en LXC. 21 commits en sus primeras 19 h. Cero código de producto | sí, leí `README` y `CONTEXTO-SIAO.md` el 6-sep |
| `mudh-mobile` | Agente en Android, contenedor proot, Zod Gate, kernel TS. **Tiene el método de trabajo y el inventario de las máquinas** | no, solo el conteo de issues |
| `icca-engine` | Sitio de dos caras (humanos + agentes), licencia RSL 1.0, Puerta de Cómputo | **NO MEDIDO** |
| `drosophila-fep-connectome` | Paper publicado (Zenodo 19136948) + erratum, 40 nulls | **NO MEDIDO** |
| `dualbrain` | Motor C99, benchmarks. Privado | **NO MEDIDO** |
| `correai` | Go, 5 issues, creado el 7-sep | **NO MEDIDO, no sé qué es** |
| `cashgo` | creado el 7-sep | **NO MEDIDO, no sé qué es** |

---

# 4 · EL SISTEMA VIVO, para que Fable lo ataque de verdad

No hace falta clonar nada para auditar el producto:

```bash
curl -s https://150448fcc6.abacusai.cloud/estado | python3 -m json.tool
curl -s 'https://150448fcc6.abacusai.cloud/buscar?q=prescripcion+adquisitiva&limit=3'
curl -s https://150448fcc6.abacusai.cloud/openapi.json | head -40
curl -s https://150448fcc6.abacusai.cloud/agente/manifiesto
```

**Y sobre todo: el frontend.** `https://150448fcc6.abacusai.cloud/` es lo que vería un abogado. Ahí están los **432 títulos basura** y la `materia` vacía al 100 %, a la vista. Un auditor que solo lee código se los pierde.

**Sin autenticación, a propósito y por decisión de Abraham.** Si Fable encuentra cómo romperlo o extraer más de lo que la API declara, **eso es un hallazgo de primera** y quiero el detalle.

---

# 5 · Y UNA PREGUNTA QUE AGREGO POR ESTO MISMO

Al anexo del terreno se le suma un punto de ataque que el reporte no tenía:

**A9 · ¿Siete proyectos abiertos en 24 días es capacidad o es dispersión?**

Medido: 8 repos, el más viejo del 16-ago. **Dos nacieron el 7-sep**, mientras el corpus llevaba tres días sin un commit y con cero abogados usándolo.

No es una pregunta técnica y por eso es la más difícil de contestar desde adentro. **Yo no puedo evaluarla sin conflicto de interés**, porque cada proyecto nuevo es trabajo para mí. Que la conteste el externo.
