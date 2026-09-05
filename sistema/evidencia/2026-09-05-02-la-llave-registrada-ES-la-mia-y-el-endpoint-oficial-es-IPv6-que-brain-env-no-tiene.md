# La llave registrada es la mia, y el endpoint oficial es IPv6 que este taller no tiene

**2026-09-05 04:30 UTC.** Abraham paso el panel de claves SSH de Abacus. Se midio en vez de suponer, y salieron dos cosas nuevas.

---

## 1. Pedido

Abraham comparte el panel de SSH de la VM de Abacus: host IPv6 `150448fcc6.ssh.abacusai.cloud`, hostnames `150448fcc6.abacusai.cloud` y `corpus-tarija.abacusai.cloud`, y una clave `ssh-ed25519` con huella `SHA256:a9PwVqqAvAVklqfJDpwmJASd6GzQNtOYZZY7uTzp3Ng`, agregada el 4 de septiembre.

## 2. Herramientas y maquina

**brain-env** por el gateway MUDH, servicio `build`, tool `run`: 3 llamadas, solo lectura y sondas de red. Los dos scripts fueron en **base64** con md5 verificado en las dos maquinas antes de ejecutarlos. **Cero escrituras en la base. Cero runtime ajeno.**

## 3. Que se midio

| medicion | resultado | consecuencia |
|---|---|---|
| huella de la publica local | **identica a la del panel** | la credencial **no** es el bloqueo |
| `150448fcc6.ssh.abacusai.cloud` | **solo AAAA**, sin registro A | endpoint oficial IPv6-only |
| IPv6 desde `brain-env` | `rc 99` a todo, `/proc/net/if_inet6` **vacio** | el container **no tiene** IPv6 |
| control positivo v6 | `ipv6.google.com` y `www.google.com` v6 dan **rc 99** | el 99 es mio, no de la VM |
| control positivo v4 | `www.google.com` y `github.com` v4 dan **rc 0** | el egress v4 vive |
| `150448fcc6.ssh4.abacusai.cloud` | `208.122.8.11`, puertos 22172/22/443 en **timeout** | la VM sigue sin responder |
| `ssh -4 -vv` real | `connect to address 208.122.8.11 port 22172: Connection timed out` | mismo veredicto, con el mensaje del cliente |

## 4. Evidencia cruda verbatim

```plain
$ md5sum /workspace/sonda_ssh_v6.py
10d1f43e6899ff7d30d4bf94c6de8a7f    <- identico al generado afuera

DNS 150448fcc6.ssh.abacusai.cloud  -> ['2604:2dc0:208:22b1:bb0:aea2:9c36:5810']
DNS 150448fcc6.ssh4.abacusai.cloud -> ['208.122.8.11']
DNS 150448fcc6.abacusai.cloud      -> ['104.18.20.183','104.18.21.183','2606:4700::6812:14b7','2606:4700::6812:15b7']
DNS corpus-tarija.abacusai.cloud   -> ['104.18.20.183','104.18.21.183','2606:4700::6812:14b7','2606:4700::6812:15b7']

TCP 150448fcc6.ssh.abacusai.cloud  22172 AF_INET6 rc 99
TCP 150448fcc6.ssh.abacusai.cloud     22 AF_INET6 rc 99
TCP 150448fcc6.ssh.abacusai.cloud    443 AF_INET6 rc 99
TCP 150448fcc6.ssh4.abacusai.cloud 22172 AF_INET  rc 11
TCP 150448fcc6.ssh4.abacusai.cloud    22 AF_INET  rc 11
TCP 150448fcc6.ssh4.abacusai.cloud   443 AF_INET  rc 11

$ md5sum /workspace/sonda_v6_control.py
473b1bbb6b437b2409432218ef23dbc9    <- identico al generado afuera

=== CONTROL POSITIVO DE IPv6 desde brain-env ===
ipv6.google.com    v6 2800:3f0:4002:815::200e   rc 99
www.google.com     v6 2001:4860:4829:7700::     rc 99
www.google.com     v4 142.251.155.119           rc 0
github.com         v4 4.228.31.150              rc 0

=== INTERFACES DEL CONTAINER ===
(vacio: SIN direccion IPv6)

=== LA LLAVE LOCAL, huella SHA256 ===
256 SHA256:a9PwVqqAvAVklqfJDpwmJASd6GzQNtOYZZY7uTzp3Ng brain-env@mudh (ED25519)

$ ssh -4 -vv ... -p 22172 ubuntu@150448fcc6.ssh4.abacusai.cloud 'echo VIVA; uptime'
debug1: Connecting to 150448fcc6.ssh4.abacusai.cloud [208.122.8.11] port 22172.
debug1: connect to address 208.122.8.11 port 22172: Connection timed out
ssh: connect to host 150448fcc6.ssh4.abacusai.cloud port 22172: Connection timed out
```

## 5. Los dos hallazgos, y por que importan

**La credencial nunca fue el problema.** La huella del panel es exactamente la de `/workspace/.ssh-abacus/id_ed25519.pub`, comentario `brain-env@mudh`. No hay llave que agregar ni rotar: cuando la VM responda, el login entra.

**El endpoint que Abacus documenta es inalcanzable desde el taller por construccion.** `150448fcc6.ssh.abacusai.cloud` no tiene registro A, y este container no tiene ni una direccion IPv6. El `rc 99` es **EADDRNOTAVAIL**, o sea que el kernel no puede ni elegir una direccion de origen: no llega al cable. Y eso quedo probado con **control positivo**: Google por IPv6 tambien da 99, y por IPv4 da 0. Si me hubiera quedado con el 99 del host de Abacus, habria reportado "la VM no responde por v6" cuando lo cierto es "yo no hablo v6".

**Consecuencia operativa:** la unica ruta desde `brain-env` es el alias `ssh4` (`208.122.8.11`), que es el que el script ya usa. Si en algun momento ese alias desaparece, el despliegue desde el taller queda sin via y hay que mirar otra maquina.

## 6. NO MEDIDO

- **Si la VM esta prendida.** El timeout por v4 es compatible con VM apagada y con ruta cortada; no los distingue.
- **Si GitHub Actions tiene IPv6.** Seria la via para el endpoint oficial, y exigiria la privada como secret: decision de Abraham, no medida.
- Si el alias `ssh4` es permanente o se regenera con cada arranque.
- **Los 926 decretos siguen sin ingestar. Nada desplegado.**
