# El corpus dentro de la suite · y por qué sigue siendo independiente

**Fecha:** 2026-09-10 · **Decide:** Abraham

---

## LO PRIMERO, y es una decisión explícita

> **`corpus-legal-tarija` es un PRODUCTO INDEPENDIENTE y debe seguir mejorando por su cuenta.**

No es la capa de datos de otro producto. Tiene su propia hoja de ruta, sus propios usuarios y su propia deuda técnica, y se sigue trabajando **aunque el resto de la suite se detenga**.

## La suite

| Parte | Repo | Estado |
|---|---|---|
| **1 · El corpus** | este | **VIVO en producción**, 6.079 documentos |
| **2 · Custos Legis Tarija** | [`custos-legis-tarija`](https://github.com/gatehot59-star/custos-legis-tarija) | recién fundado, **cero código** |

**La dependencia va en un solo sentido:** Custos Legis consume el corpus; el corpus **no** depende de Custos Legis. Si Custos Legis se cancela, el corpus sigue siendo vendible. Al revés, no.

## Qué se le puede pedir al corpus desde la suite

Solo mejoras que le sirven **a cualquier consumidor**, incluido el que usa el corpus solo:

1. **Vigencia usable** (hoy 13 de 527 leyes)
2. **Títulos reales** (hoy 432 de 1.034 son basura extraída del cuerpo)
3. **`materia` poblada** (hoy vacía al 100 %)
4. **Jerarquía normativa explícita** (nacional / departamental / municipal)
5. **Corpus municipal de Tarija** (hoy inexistente)

## Qué NO entra acá nunca

| NO | Por qué |
|---|---|
| **Multi-tenancy / RLS** | el corpus sirve datos **públicos**: no tiene inquilinos |
| **Documentos confidenciales de bufetes** | este repo es **público**. Meter un expediente privado acá sería un incidente |
| **Casos, plazos, estado procesal, facturación** | nada de eso es normativa |

**Regla de decisión:** ¿le sirve a alguien que **solo** usa el corpus? → entra. ¿Solo le sirve a un bufete con expedientes activos? → va a Custos Legis.

## El contrato por el que se consume

```
GET /buscar?q=...&limit=&offset=
GET /texto?uid=&nro=
GET /estado
GET /openapi.json
GET /agente/manifiesto
GET /api/v1/procedencias/{uid}
```

Y los **límites declarados** que un consumidor honesto tiene que respetar: la búsqueda es **literal** (sin expansión semántica), las facetas cuentan sobre **una muestra de 400 pasajes**, y el desplazamiento **corta en 10.000**.

## La hoja de ruta del corpus NO cambia por esto

Sigue siendo la misma, y en este orden:

1. **Un abogado usando el sistema una hora.** Cero abogados desde el 3-sep.
2. **Vigencia inversa a pedido** (el 86 % de las abrogaciones no nombra su objeto: la vigencia completa no existe con esta fuente).
3. **Títulos**: la hipótesis del slug falló **dos veces con el mismo número**. Antes de un cuarto intento hay que medir la forma real de las URLs.
4. **`materia`**, vacía al 100 %.
5. **Re-censar la Gaceta 2022 con el parser v3**: sus 317 son cota inferior.
6. **Cero pruebas automatizadas.** Mañana un cambio lo rompe en silencio.
