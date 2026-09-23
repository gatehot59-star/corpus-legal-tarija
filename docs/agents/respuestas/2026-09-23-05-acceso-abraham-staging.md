# Acceso staging para Abraham

## Pedido
Crear un usuario Abraham y entregar el enlace de acceso al Corpus Django staging.

## Qué se hizo

- Usuario `abraham` creado/actualizado y activo en la base operativa de staging.
- Membership habilitada en `staging-real-readers`.
- Grant activo por 30 días sobre la colección real adaptada.
- Password comprobada contra Django y login público verificado con Chromium.
- El password no se guarda en este recibo ni en el repositorio.

## Acceso

- URL: `https://150448fcc6.abacusai.cloud/corpus/login/`
- Usuario: `abraham`

## Evidencia cruda

```text
username=abraham
created_or_updated True
collection 89701639-ffaf-41be-9c94-5d291d1e3c6f
password_check True
grant 1
public login -> /corpus/
```

## Límite

Es una cuenta de staging. El password solicitado es débil y debe cambiarse antes de cualquier uso productivo. No se habilitó correo real ni recuperación operativa.

--- METODO TITAN ---
Accion delicada: SI (creación de identidad y grant de acceso)
Modo aplicado: TITAN FULL
Rubrica: N/A (operación de cuenta staging, no release)
N/A declarados: producción, SMTP real y ciclo operativo de cuentas fuera de alcance
Review externo: no aplica a la operación puntual
Instrumento: VM tunnel + Django ORM + Chromium público; evidencia cruda arriba
