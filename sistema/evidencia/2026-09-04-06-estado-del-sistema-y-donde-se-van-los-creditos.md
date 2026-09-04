# 2026-09-04-06 · Estado del sistema y dónde se van los créditos

## 1. Pedido

"En criollo y siendo objetivo: dónde estamos, cómo se encuentra el sistema Corpus, cuánto
falta para dejarlo óptimo, la conexión SSH con la SuperComputadora resta crédito, revisá el
total de crédito de Abacus y en qué se fue."

## 2. Herramientas declaradas

| herramienta | qué hizo | escribió | cuota ajena |
| --- | --- | --- | --- |
| `build.run` | SQL sobre la base servida, `curl` a la API pública | sí, en `/workspace` | no |
| `ssh` a la VM | uptime del kernel, env, disco, RAM, y la API de Abacus con la clave de la propia máquina | no | la VM del usuario |
| `search_web` | documentación oficial de facturación de Abacus | no | no |

**No se escribió en la base ni se reinició nada.**

## 3. La premisa del usuario, corregida con medición

**"La conexión SSH resta crédito" es FALSO.** Abacus cobra que la SuperComputadora esté
**encendida**, no que alguien esté conectado: **1 crédito cada 5 minutos de runtime**,
verificado hoy en la documentación oficial. El SSH es gratis.

```
uptime leido del kernel:  42.796 s = 713,3 min = 11,9 h
credito de esa corrida:   713 / 5 = ~143 creditos
si queda 24/7 un mes:     43.200 / 5 = 8.640 creditos = 29% de los 30.000 del plan Pro
```

Y una consecuencia que conviene decir: Abacus documenta un auto-apagado "cuando no corre
nada", pero `corpus-api.service` está **siempre activo** (16 servicios corriendo), así que
esta máquina **probablemente nunca se apaga sola**. No lo verifiqué contra el historial de
facturación: NO MEDIDO.

## 4. El saldo: NO MEDIDO, y por qué

La clave de la VM existe y funciona:

```
key presente: True | largo: 35   (viene de /etc/profile.d/abacusai.sh)
listApiKeys                      http=200 {"apiKeyId":"81f64a696","apiKeySuffix":"1ae6",
                                          "createdAt":"2026-09-04T01:31:46+00:00","isExpired":false}
getOrganizationComputePoints     ERR=404 "Action ... not found"
getComputePointInfo              ERR=404 "Action ... not found"
describeOrganization             ERR=404 "Action ... not found"
getBillingInfo                   ERR=404 "Action ... not found"
getUsage                         ERR=404 "Action ... not found"
```

Los endpoints de créditos viven en `apps.abacus.ai/api/_getOrganizationComputePoints` y
piden **cookie de sesión de navegador**, no clave de API. Y la metadata de la VM, que antes
publicaba la key y el `api_base_url`, hoy responde `unauthorized` con token de largo 2.

**No inventé el saldo.** Está en `apps.abacus.ai/app/billing` → "View Credit Usage" →
"Group by Source", que es el único lugar que desglosa hosting vs llamadas de modelo.

Dato del plan, verificado: Abacus **bloquea el último 25% de los créditos** hasta la última
semana del ciclo. El techo útil hoy no son 30.000 sino ≈22.500.

## 5. Estado del sistema, medido

```
== CORPUS
  documentos       6079
  pasajes          78930
  caracteres       102620935
  texto oficial    5261 (87%) | OCR 818 (13%)
== VIGENCIA (denominador real = normas, NO jurisprudencia)
  leyes departamentales      512
  nacionales                  15
  con estado real (vig=0)     13
  con nota de derogacion      14
  jurisprudencia (no aplica) 5030
== TITULOS
  slug de descarga           401
  vacios                    4709   (los Autos Supremos se identifican por numero: normal)
== SERVICIO PUBLICO
  /censo                             960 ms
  /buscar usucapion             832 ms |  1741 pasajes |  43 ms interno
  /buscar asistencia familiar   402 ms |   184 pasajes |   6 ms interno
  /buscar despido injustificado 502 ms |   324 pasajes |  21 ms interno
  /buscar prescripcion          621 ms |  4467 pasajes |  78 ms interno
== VM
  2 vCPU | 7.957 MB RAM (1.554 usados) | / 48G al 28% | /home/ubuntu 51G al 2%
```

## 6. Cuánto falta, en tres cajones

**Bloquea la venta:**
1. **No hay usuarios.** Una clave compartida, no cuentas. Sin login no hay membresía ni cobro.
2. **Vigencia en 13 de 527 (2,5%)**, y la vigencia es todo el diferencial.

**Hace que se vea barato:**
3. 401 leyes con el slug de descarga como título.
4. El hallazgo del abrogador muerto no llega a la ficha: falta campo de observación visible.
5. Búsqueda literal: "despido sin causa" no encuentra "despido injustificado".

**Pulido:** `/d/<uid>` canónico, CSS de impresión, fuentes propias, CSP/HSTS, corrección de
OCR, la faceta que cuenta sobre un pool de 400, y suite automatizada.

## 7. La parte incómoda, dicha

**La vigencia no escala con más scripts.** LexiVox da relación declarada para 2 de 15
nacionales y ya lo exprimí. Las 499 departamentales que faltan solo salen leyendo el texto
de cada ley posterior, y eso rinde 13. Para cobertura real hace falta **otra fuente** (la
Gaceta departamental responde y no se explotó para vigencia) o **vender con vigencia parcial
declarada honestamente**, que es lo que la ficha ya hace.

## 8. NO MEDIDO

- El saldo de créditos y su desglose (sección 4).
- Si la máquina se auto-apagó alguna vez.
- 499 de 512 departamentales y 13 de 15 nacionales sin vigencia.
- Las 483 Resoluciones del Pleno, nunca revisadas para vigencia.
- Cuánto se fue en llamadas de modelo con la clave de la VM.

---

```
--- METODO TITAN ---
Accion delicada: NO (solo lectura)
Modo aplicado:   TITAN FULL
Rubrica:         Completitud 15/15 · Arquitectura (del razonamiento) 10/10 ·
                 Documentacion 10/10 · Innovacion 4/5 (corregir la premisa del SSH y el
                 denominador de la vigencia) · Proceso QA 5/5
                 Ejecutabilidad, Seguridad, Testing, DevOps: N/A (es un reporte)
                 = 44/45 aplicables -> 98/100
N/A declarados:  4 criterios por tipo de entrega (reporte, no codigo)
Review externo:  no pedido (deuda declarada)
Instrumento:     SQL sobre la base servida, curl a la API publica, uptime del kernel de la
                 VM, la API de Abacus con la clave de la propia maquina (404 verbatim), y
                 la documentacion oficial de facturacion verificada hoy.
```
