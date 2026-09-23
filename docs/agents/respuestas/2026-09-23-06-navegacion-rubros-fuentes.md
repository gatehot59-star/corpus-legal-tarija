# Navegación por rubros y fuentes

## Pedido
Construir una navegación del Corpus para acceder al catálogo por fuente y rubro, además de la búsqueda textual.

## Qué se construyó

- Panel `Explorar por fuente y rubro` en la mesa de lectura.
- Filtro por fuente: GENESIS TSJ, Gaceta Oficial de Tarija y LexiVox nacional.
- Filtro por rubro/materia: Administrativa, Civil, Comercial, Constitucional, Penal, Familia, Trabajo, Tributaria y los demás valores presentes.
- Filtro por tipo de norma: Ley, Código, Auto Supremo, Sentencia, Resolución y otros valores presentes.
- Paginación del catálogo a 20 documentos por página.
- Cada resultado lleva a su locator exacto autorizado, con colección y versión, no a una ruta inventada.
- La navegación reutiliza la verificación de snapshot y filtra por los UIDs autorizados antes de mostrar metadata.

## Medición

```text
Found 45 test(s).
Ran 45 tests in 0.821s
OK
Servicio staging: active
Health público: HTTP 200
Chromium: facets pobladas, catálogo completo visible, filtro LexiVox aplicado
Primer locator navegable: collection=89701639-ffaf-41be-9c94-5d291d1e3c6f, version=6d34496cfcfba071ede1193ccbaa4506ea3a400ef45d19a2acb469507b8e19ae
```

## Alcance

La navegación usa la colección real adaptada de staging y mantiene el aislamiento por usuario. Ben no tiene grant de la colección real, por lo tanto no recibe metadata de sus documentos.

## NO MEDIDO

No se mergeó esta feature a `main`; queda en PR para revisión. No cambia el límite de producción ni crea cuentas reales.

--- METODO TITAN ---
Accion delicada: SI (metadata protegida y frontera de autorización)
Modo aplicado: TITAN FULL
Rubrica: 93/100 provisional, pendiente de revisión y checks del PR
N/A declarados: producción, cuentas reales, SMTP y carga no son objeto de esta feature
Review externo: pendiente en el PR; silencio no es aprobación
Instrumento: VM tunnel + suite Django + Chromium público; evidencia cruda arriba
