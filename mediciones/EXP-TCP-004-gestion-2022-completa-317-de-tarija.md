# EXP-TCP-004 · Gestión 2022 de la Gaceta, completa · 317 resoluciones de Tarija

**Medido:** 2026-09-05 · **Máquina:** GitHub Actions `ubuntu-latest`, 10 jobs en paralelo
**Instrumento:** `.github/workflows/censo-gaceta-tcp.yml` · datos en `mediciones/gaceta-2022/`
**Corrida:** `censo-gaceta-tcp #2`, los 10 tomos VERDES + control negativo VERDE

---

## El número

| Métrica | Medido |
|---|---|
| Tomos | **10 de 10 VERDES** |
| Sentencias constitucionales únicas | **6.138** |
| **Resoluciones con `Departamento: Tarija`** | **317** |
| Caracteres de texto nativo | **298.202.742** |
| PDF descargados | ~503 MB, cada uno con su sha256 |

**Y el 317 es sólido por construcción:** `tarija_resoluciones_unicas = 317` y `tarija_sumado_por_tomo = 317`. Los dos coinciden, o sea **cero solapamiento entre tomos**. Si un tomo repitiera resoluciones de otro, los números diferirían. No lo asumí: lo hice medir.

### Por tomo

| Tomo | SCP | Tarija | Caracteres |
|---|---|---|---|
| I s1 | 388 | 19 | 24.741.310 |
| I s2 | 888 | 54 | 60.908.942 |
| II s1 | 690 | 38 | 24.425.521 |
| II s2 | 907 | 42 | 29.886.618 |
| III s1 | 697 | 39 | 32.229.927 |
| III s2 | 867 | 41 | 36.562.082 |
| IV s1 | 668 | 30 | 25.060.959 |
| IV s2 | 945 | 42 | 34.906.629 |
| V s1 | 40 | 5 | 14.192.848 |
| V s2 | 48 | 7 | 15.287.906 |

El Tomo V tiene 40 y 48 SCP contra ~700-900 de los otros: es el tomo de cierre, con menos sentencias y más material de otro tipo. **No es un rojo**, pero el guard lo habría marcado si hubiera dado 0.

---

## ME REFUTO DOS VECES

### 1. Mi estimación estaba 40 % baja

Ayer escribí "~190 por gestión", extrapolando de 19 en el tomo I. **Son 317.** El error: tomé el tomo I como representativo y es el **más chico en sentencias** (388 contra 945 del IV s2). Sesgo de muestra de tamaño 1. Estaba declarado como estimación, y **igual salió mal en la dirección que importa**: subestimé la fuente.

### 2. "Ya no hace falta tocar el buscador" es FALSO

Lo escribí ayer como veredicto operativo. Medí los bordes del índice y se cae:

```
gaceta2016 404 · gaceta2017 404 · gaceta2023 404 · gaceta2024 404 · gaceta2025 404
```

**La Gaceta web solo cubre 2018-2022.** Mi censo del buscador cubre 1999-2019 (2.939 resoluciones). Entonces:

- **2018-2022** → Gaceta oficial, PDF con hash, texto nativo. **La vía buena.**
- **1999-2017** → solo el buscador. **La Gaceta no los publica en la web.**

Son **dos fuentes para dos tramos**, no una que reemplaza a la otra. Y el art. 19 del CPCo manda periodicidad mensual, así que la ausencia de 2023-2025 en el portal es un **hallazgo abierto**, no una decisión mía.

### Y la discrepancia con el buscador NO se resolvió

317 (Gaceta 2022) contra 380 (buscador, distrito 7, 2016). Años distintos: **no son comparables**. El tramo que ambos cubren es **2018-2019**, y ahí sí se cruza: el buscador dio 301 (2018) y 290 (2019). **Ese cruce queda NO MEDIDO** y es el próximo instrumento que puede dar rojo contra cualquiera de los dos métodos.

---

## Trampas del entorno cazadas en esta corrida

1. **`ps` NO EXISTE en brain-env.** Corrí `ps aux | grep -c censo.py`, dio `0`, y casi reporté que el proceso había muerto. Control positivo: `which ps` vacío y `ps aux | wc -l` = 1. **Un instrumento ausente devuelve cero igual que una ausencia real.** Verificado con `grep -l censo /proc/[0-9]*/cmdline`: 4 pids vivos.
2. **El shell del gateway pre-expande `$`**: un bucle `for y in 2016 2017 …; do curl …/gaceta$y/` midió **cinco veces la misma URL** y devolvió `200` cinco veces. Lo cacé porque `%{url_effective}` mostraba `/gaceta/` pelado. Rehecho con URLs literales dio los 404 reales. **Sin ese campo habría publicado que 2016 y 2023 existen.**
3. **`pdftotext` y `time` no existen en brain-env**, pero **sí** en `ubuntu-latest`. Por eso el workflow usa pdftotext con caída a pypdf.
4. **Un límite que creía cerrado y no lo estaba:** un recibo del 5-sep decía que el PAT no tenía scope `workflow`. **Desde este canal sí puedo crear y disparar workflows.** El inventario se re-mide, no se recuerda.

## Por qué esto fue a la fábrica y no al taller

El Celeron llevaba **más de 25 minutos** en un solo tomo sin terminar (pypdf, `"".join` de 25 M de caracteres). Actions cerró **los 10 tomos y el control negativo en 1m39s**. Mi instrumento local tenía un defecto propio: acumulaba todo en memoria en vez de escribir incrementalmente, que es lo que la corrida anterior sí hacía.

## Control negativo, y por qué no es decorativo

`TomoXXs92022.pdf` (tomo inventado) **no devuelve PDF**. Sin este control, un `200` no distingue existe de no existe, y este proyecto ya se comió un LexiVox que devolvía `200` con "Norma inexistente".

---

## NO MEDIDO

- **Cruce 2018-2019 Gaceta vs buscador.** Es el falsador que puede refutar a cualquiera de los dos.
- Gestiones **2018, 2019, 2020, 2021** (el workflow ya las acepta por parámetro).
- Dónde están **2023-2025**, si el art. 19 manda publicación mensual.
- **Ingesta real:** los 317 están **censados, no incorporados**. El corpus sigue en 6.079 documentos.
- Si el índice del tomo permite **partir por resolución** de forma fiable.
- `jurisprudencia.tcpbolivia.bo`: tercer host, **timeout** por curl y por navegador.

## Estado

TCP 2022: **censado, 317 de Tarija, con hash y fuente oficial**. Incorporado al corpus: **NO**.
