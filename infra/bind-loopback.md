# El backend del corpus escucha en `0.0.0.0`, y el login de nginx no lo cubre

**Orden de Abraham, 2026-09-10: "tocalo".**

**Y lo primero: NO LO APLIQUE.** El taller donde se escribio esto no tiene red ni
SSH a la VM. Lo que sigue son los comandos exactos y su verificacion; el disparo
es de Abraham. Decir "hecho" sin haberlo corrido seria justo el tipo de reporte
que este proyecto persigue.

## Lo medido (en la sesion del cierre, 06:31 UTC)

```
$ ss -tlnp
LISTEN 0 5    0.0.0.0:8080   users:(("python3",pid=724))
LISTEN 0 511  0.0.0.0:80     users:(("nginx",...))
```

Y en el fuente del servicio:

```python
ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
```

**Desde internet no se llega** (medido: `http://...:8080/estado` da **522**,
timeout de Cloudflare al origen; por HTTPS falla el handshake). El ingress solo
proxea 80/443, asi que el login de nginx **si** protege el acceso publico.

**El hueco:** cualquier proceso o contenedor dentro de la red de la VM le pega a
`:8080` **directo**, sin pasar por nginx. El login no lo ve. Es defensa en
profundidad que hoy no existe.

## El cambio

Una linea en el fuente del servicio del corpus:

```diff
- ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
+ # Loopback: nginx es el UNICO camino, y ahi vive el login.
+ # Si esto vuelve a 0.0.0.0, el login de nginx deja de ser obligatorio.
+ ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
```

## Aplicar

```bash
# 0. Averiguar los nombres REALES antes de tocar nada. Estan como NO MEDIDO
#    abajo justamente porque no pude verlos.
systemctl cat corpus-api | head -20      # de aca sale el ExecStart y la ruta
ss -tlnp | grep 8080                     # y de aca el pid

# 1. Backup con hash, para poder demostrar que se restauro igual
sudo cp /ruta/al/corpus_api.py /ruta/al/corpus_api.py.antes-del-bind
md5sum /ruta/al/corpus_api.py.antes-del-bind

# 2. El cambio
sudo sed -i 's/("0\.0\.0\.0", PORT)/("127.0.0.1", PORT)/' /ruta/al/corpus_api.py

# 3. Verificar que el sed HIZO algo. Un sed sin match sale 0 igual que un exito:
#    es el mismo defecto del `grep -c` que ya cazamos tres veces en esta campana.
grep -n '127.0.0.1", PORT' /ruta/al/corpus_api.py || echo "ROJO: el sed no aplico"

# 4. Reiniciar y medir
sudo systemctl restart corpus-api
sleep 2
ss -tlnp | grep 8080      # debe decir 127.0.0.1:8080, NO 0.0.0.0:8080
```

## El control positivo, y sin esto la verificacion no vale

**Un `:8080` que no responde desde la red se ve IGUAL que un servicio caido.** Asi
que despues del reinicio hay que comprobar **las dos cosas, en este orden**:

```bash
# (1) VIVO: por loopback tiene que responder 200
curl -s -o /dev/null -w 'loopback: %{http_code}\n' http://127.0.0.1:8080/estado

# (2) CERRADO: por la IP de la VM tiene que fallar o dar timeout
IP=$(hostname -I | awk '{print $1}')
curl -s -m 5 -o /dev/null -w "red interna: %{http_code}\n" "http://$IP:8080/estado" \
  || echo "red interna: sin respuesta (esperado)"
```

**Si (1) falla, el servicio se cayo y hay que revertir, no festejar el (2).** Es la
misma leccion del 503: "no llegue" y "esta cerrado" son cosas distintas, y un
instrumento que no las separa miente en la direccion comoda.

## Revertir

```bash
sudo cp /ruta/al/corpus_api.py.antes-del-bind /ruta/al/corpus_api.py \
  && sudo systemctl restart corpus-api
```

## Lo mismo, ya resuelto en la API nueva

`custos-legis-tarija/backend/api.py` nace con el default correcto:

```python
def servir(app, host="127.0.0.1", puerto=8090):
```

Loopback por defecto, salir de ahi es explicito, y si alguien pasa otro host el
servicio lo avisa por stderr al arrancar. **La leccion del corpus quedo en el
codigo, no en un documento que nadie relee.**

## NO MEDIDO

1. **La ruta exacta del fuente y el nombre del servicio.** Los pongo como
   `/ruta/al/corpus_api.py` y `corpus-api` porque **no tengo acceso a la VM desde
   este taller**. Hay que completarlos con el paso 0.
2. **Si algo dentro de la red de la VM le pega hoy al 8080.** No lo medi. El
   cambio elimina la posibilidad; no prueba que estuviera pasando.
3. **Si el backend escucha algo mas** ademas del 8080.
4. **Si el servicio arranca con `-u` o `PYTHONUNBUFFERED`.** Medido en la API
   nueva que sin eso el `print` de arranque se pierde cuando systemd mata el
   proceso. Probablemente el corpus tenga el mismo problema y no lo verifique.
