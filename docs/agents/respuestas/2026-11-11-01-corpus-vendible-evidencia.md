# Corpus vendible: evidencia reproducible y corrección de transporte

11 de noviembre de 2026, ART. Recibo del informe docs/auditorias/2026-11-11-01-corpus-vendible-sigc-fuentes-y-bloqueos.md.

## 1. Pedido

Revisar qué falta para vender Corpus; identificar los sistemas públicos legales utilizados en Tarija, incluida la incorporación de 2026, y recomendar información útil para abogados y estudios. Alcance acotado, no censo exhaustivo, autorización de merge ni implementación.

## 2. Herramientas y máquinas

GitHub y Nexus; shell brain-env; SSH de sólo lectura a la VM; HTTP público y navegador efímero; sandbox auxiliar para preparar instrumentos. Las pruebas usan funciones capturadas de la revisión desplegada c0e44af31a54bc2f0ba8304fc6572467082b69d6 y fixtures ficticios. Siete archivos fuente se contrastaron con ese commit público. Main inicial: 802540d2b97f44ca6e3084aad456053f984ca4b9.

No se cambiaron producto, servicios, cuentas, bases vivas ni credenciales. No se ejecutaron OCR, GPU, Actions, cobros, ingestas ni ofertas. Las escrituras externas se limitan al informe, este recibo, Doc y reporte de continuidad. El navegador se cerró; no se dejó ningún trabajo en segundo plano por esta revisión.

## 3. Qué se midió

Dos fixtures nuevos de 60 documentos. Positivo doc001: encontrado. Consulta ausente: vacía. FTS directo doc060: encontrado. Application.search doc060: vacío, FALLA por restringir candidatos a la primera página de 50. Lectura recompuesta: 12.033/12.033 caracteres exactos, PASA. Descarga: 10.000/12.033, FALLA. Desde página 1 el siguiente enlace rotulado 2 muestra página 3, FALLA. Ambos oráculos rechazan los mutantes pertinentes: pérdida de un resultado y eliminación de un carácter. Conexiones cerradas explícitamente; hash físico del fixture conservado antes/después.

La corrida diagnóstica salió 0 y su estado es completed_with_product_failures: exit 0 no significa producto aprobado. La prueba sustituye ORM, autenticación, DTO, transacciones, render y transporte; no valida HTTP autenticado de extremo a extremo.

## 4. Evidencia cruda y recuperación exacta

El primer commit documental, 13c09d989fa03860a69daf0a334f109808683d7d, preserva correctamente el informe de 21.923 bytes, SHA256 fed88b94d8d75bd7acc1e70fa1c335b0b62c782b9a21e588d72f2f046ee10b9d. Su payload de evidencia sufrió 25 inserciones durante la transferencia manual. Se detectó al recuperarlo; no se atribuye al producto. No se reescribe la historia ni se oculta el error.

Esta revisión convierte ese objeto histórico inmutable en entrada de una recuperación determinista: quita ocho inserciones conocidas, verifica longitud y SHA256 originales, descomprime el paquete y repone siete fuentes desde el commit público desplegado. No vuelve a medir producción ni modifica el clon. Todas las capturas originales permanecían intactas y se compararon directamente con las recuperadas.

Formato original: corpus-evidence-git-dictionary-v1. El paquete guarda el probe completo salvo siete textos idénticos a fuentes Git, y guarda completos core-check.json y core-run.json. Reponer los textos y serializar json.dumps(ensure_ascii=False, indent=2), sin newline final, recupera probe.json exacto. Los scripts y fixtures están incluidos en las capturas. No se descartaron stdout/stderr del ensayo al comprimir. Las exclusiones de privacidad de la captura son intencionales: secretos, credenciales, filas privadas de cuentas/feedback y causas personales.

### Identidades exactas

- Base64 publicado inicialmente: 15.073 caracteres, SHA256 30fe012ecdf922078ff87cb8cb58cf512677e18c6964ba4e3154e825b47dee56.
- Base64 original recuperado: 15.048 caracteres, SHA256 644fedf22323c578ec0d3b7a2c33c6886030069c6e0b0841f0c536deab3ee933.
- evidence-delta.json: 46.646 bytes, SHA256 3c8269bb6b8c3846ba8ecffd7e5925b6d623ea616cd09a056252b02dfde9bbb0.
- probe.json: 84.373 bytes, SHA256 20898a6a6d6ddefddb3e4e2c0dbefb5a623183aad27c4582fe787f0de81f7af6.
- core-check.json: 16.826 bytes, SHA256 5849e56eacf3568c25094c2f41bc65973e6bf402325877ec0117333a0de3c3be.
- core-run.json: 5.166 bytes, SHA256 ed5f433e90de65023f6375da5c80502129e439b2b204b1ae9d0db4c184534bd6.
- probe.py: 5.519 bytes, SHA256 bc6f30ee96bc8f3a521f18bf6a2a5deb4494e84eb823e1b97c3427b103cf1f73.
- check_core.py: 11.731 bytes, SHA256 31dfbac65d400087e4168129b39af66e9dcb03f55ce4f93a583d13b43dc0f194.
- recover_evidence.py, debajo: 2.997 bytes, SHA256 ef94b6eb4abd97f037d0a3184a8fde11d3c9a0d2cc0b538bb4fb846255bc5a0e, incluyendo newline final.

### Recuperador completo, ejecutado

Requiere Python 3 y un clon que contenga los dos commits nombrados. Guardar exactamente este bloque como recover_evidence.py y pasar la ruta del clon como único argumento. Sólo lee objetos Git y escribe un temporal nuevo; no hace red ni ejecuta las pruebas o el probe recuperados. No usar Python con -O: las aserciones de integridad deben estar habilitadas.

<!-- RECOVERY SCRIPT BEGIN -->
```python
"""Recover complete Corpus audit captures from immutable public Git objects.
No production access, mutations, credentials or network requests are performed.
The supplied clone must contain the two commits explicitly named below.
"""
import base64
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import zlib

REPO = sys.argv[1]
TRANSPORT_COMMIT = '13c09d989fa03860a69daf0a334f109808683d7d'
TRANSPORT_PATH = 'docs/agents/respuestas/2026-11-11-01-corpus-vendible-evidencia.md'
SOURCE_COMMIT = 'c0e44af31a54bc2f0ba8304fc6572467082b69d6'
EXPECTED_BASE64 = '644fedf22323c578ec0d3b7a2c33c6886030069c6e0b0841f0c536deab3ee933'
EXPECTED_DELTA = '3c8269bb6b8c3846ba8ecffd7e5925b6d623ea616cd09a056252b02dfde9bbb0'
DELETIONS = [(243,244,'O'),(404,410,'tayNNT'),(553,555,'Pr'),(706,707,'P'),(708,711,'JqP'),(738,743,'+T1+T'),(858,863,'mGetd'),(872,874,'Ne')]

def git_bytes(commit, path):
    """Read a named immutable object without touching the working tree."""
    return subprocess.check_output(['git','-C',REPO,'show',commit+':'+path])

def checked(raw, expected, size):
    """Fail closed on either byte length or SHA-256 mismatch."""
    assert len(raw)==size, ('BYTE_LENGTH',len(raw),size)
    assert hashlib.sha256(raw).hexdigest()==expected, 'SHA256_MISMATCH'
    return raw

receipt = git_bytes(TRANSPORT_COMMIT,TRANSPORT_PATH).decode()
encoded = ''.join(receipt.split('<!-- EVIDENCE BEGIN -->\n',1)[1].split('\n<!-- EVIDENCE END -->',1)[0].split())
checked(encoded.encode(),'30fe012ecdf922078ff87cb8cb58cf512677e18c6964ba4e3154e825b47dee56',15073)
for start,end,inserted in reversed(DELETIONS):
    assert encoded[start:end]==inserted, 'TRANSPORT_EDIT_MISMATCH'
    encoded=encoded[:start]+encoded[end:]
checked(encoded.encode(),EXPECTED_BASE64,15048)
raw_delta=checked(zlib.decompress(base64.b64decode(encoded,validate=True)),EXPECTED_DELTA,46646)
bundle=json.loads(raw_delta)
assert bundle['git_dictionary']['commit']==SOURCE_COMMIT
probe=bundle['probe']['json_without_dictionary_text']
for entry in bundle['git_dictionary']['files']:
    raw=checked(git_bytes(SOURCE_COMMIT,entry['path']),entry['sha256'],entry['bytes'])
    probe['vm']['source_files'][entry['path']]['text']=raw.decode()
raw_probe=checked(json.dumps(probe,ensure_ascii=False,indent=2).encode(),bundle['probe']['sha256'],bundle['probe']['bytes'])
output=pathlib.Path(tempfile.mkdtemp(prefix='corpus-evidence-recovered-'))
(output/'probe.json').write_bytes(raw_probe)
for entry in bundle['literal_files']:
    raw=checked(entry['utf8'].encode(),entry['sha256'],entry['bytes'])
    (output/entry['name']).write_bytes(raw)
(output/'probe.py').write_text(probe['probe_source'])
(output/'check_core.py').write_text(json.loads((output/'core-check.json').read_text())['instrument_source'])
print(json.dumps({'status':'EXACT_RECOVERY','output':str(output),'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(output.iterdir())}},indent=2))
```
<!-- RECOVERY SCRIPT END -->

### Corrida de recuperación, salida íntegra

Comando exacto: python3 /workspace/corpus-sale-20261111-s19d42t3/recover_evidence.py /workspace/corpus-sale-publish-4244t8l3/repo

returncode: 0. stderr: vacío. stdout:

```json
{
  "status": "EXACT_RECOVERY",
  "output": "/tmp/corpus-evidence-recovered-wnchi_ka",
  "files": {
    "check_core.py": {
      "bytes": 11731,
      "sha256": "31dfbac65d400087e4168129b39af66e9dcb03f55ce4f93a583d13b43dc0f194"
    },
    "core-check.json": {
      "bytes": 16826,
      "sha256": "5849e56eacf3568c25094c2f41bc65973e6bf402325877ec0117333a0de3c3be"
    },
    "core-run.json": {
      "bytes": 5166,
      "sha256": "ed5f433e90de65023f6375da5c80502129e439b2b204b1ae9d0db4c184534bd6"
    },
    "probe.json": {
      "bytes": 84373,
      "sha256": "20898a6a6d6ddefddb3e4e2c0dbefb5a623183aad27c4582fe787f0de81f7af6"
    },
    "probe.py": {
      "bytes": 5519,
      "sha256": "bc6f30ee96bc8f3a521f18bf6a2a5deb4494e84eb823e1b97c3427b103cf1f73"
    }
  }
}
```

Comparación directa adicional contra las capturas originales, sin depender del hash declarado por el recuperador:

```json
{"probe.json": true, "core-check.json": true, "core-run.json": true}
```

Se conservaron errores propios: transferencia inicial del instrumento de prueba rechazada antes de ejecutarlo; repetición por porciones verificada; preparación multilínea rechazada antes de ejecución; push CLI sin credencial rechazado sin cambio remoto; primer payload documental con 25 inserciones detectadas; un intento de transferir el recuperador con zlib inválido, sin ejecución. La transferencia corregida verificó el SHA del script y produjo la corrida arriba. Ninguno de esos errores se presenta como fallo de Corpus.

## 5. Archivos generados y cierre

Informe: docs/auditorias/2026-11-11-01-corpus-vendible-sigc-fuentes-y-bloqueos.md. Evidencia: este archivo, con sus capturas completas recuperables desde objetos inmutables existentes en la historia. No se commitearon binarios derivados ni bases sensibles. Este commit sólo corrige el recibo propio; el informe original permanece sin cambios.

Gate I: PASA para los casos aislados declarados; los oráculos detectaron las violaciones pertinentes. Gate II: PASA para el informe acotado. Gate III: el informe remoto y las capturas originales ya se recuperaron y compararon; la última lectura de esta corrección, el Doc público y el reporte Nexus se registran en el cierre documental. No confundir éxito del recuperador con aprobación del producto.

## 6. NO MEDIDO

Integración autenticada de Corpus, seguridad integral, carga/SLA, restauración, exactitud/vigencia de toda la colección, número de usuarios afectados, demanda/ventas/costes, migración completa de sistemas judiciales, estado autenticado SIGC/ROMA/Éforo. No se acredita una revisión por otro operador. No se autorizan arreglos, merge, despliegue ni sustitución del OCR.

--- METODO TITAN ---
Accion delicada: NO; corrección documental propia, sin producto.
Modo aplicado: TITAN FULL, revisión acotada.
Rubrica: informe 37/40 -> 92,5/100, no madurez del producto.
N/A declarados: 60 puntos de criterios de producto.
Review externo: no realizado; mismo GPT-6 Astra en funciones de revisión y verificación.
Instrumento: probe.py, check_core.py y recover_evidence.py ejecutados; capturas completas recuperables arriba.
Maquina: brain-env; VM de lectura; navegador efímero; sandbox auxiliar.
Artefactos: informe Git + este recibo + Doc público y continuidad Nexus en el cierre.
