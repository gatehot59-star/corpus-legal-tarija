# Corrección: apagar Actions no es requisito causal del ensayo

20-sep-2026 ART. Pedido: Challenge whether disabling Actions is actually necessary. Sustituye exclusivamente el requisito de apagar/encender Actions durante la preparación de docs/adr/2026-09-20-docs-only-trigger-test.md, commit16ae405779c61380589932ad11fb7f6fcdcbfda4. El ADR anterior queda como antecedente, no como requisito vigente en ese punto. Ninguna configuración real fue modificada.

## Conclusión

**No hace falta deshabilitar Actions para preparar este laboratorio con el único workflow previsto.** Convertí una precaución opcional en un bloqueo obligatorio sin demostrar el camino de activación. La falta de un control administrativo para deshabilitar Actions no demuestra que el ensayo sea imposible.

Se releen los YAML exactos: original de main645d1732bec136bcc518070db42ff93437f95fd6 y candidato dePR21 en3b92dc432f285c00d5a45e717883c5c6e3fe46f9. Ambos declaran únicamente pull_request y workflow_dispatch. No hay push, create, schedule, workflow_run, repository_dispatch ni pull_request_target. Publicar archivos o crear ramas sin abrir PR y sin dispatch no satisface esos eventos. Actions habilitadas significa capacidad de ejecutar, no ejecución automática de cada archivo subido.

Esto depende de que TODA revisión publicada desde la primera contenga solo el workflow aprobado, de que nadie abra PRs ni emita dispatch durante la preparación y de que no aparezca automatización externa que los emita. No garantiza ausencia de eventos concurrentes de terceros. En un repositorio público un tercero puede abrir PR: leer ejecuciones y asociaciones, y detener nuevos eventos propios ante actividad no atribuible al ensayo.

## Secuencia corregida, sin toggle administrativo

1. Crear laboratorio vacío, sin fork, plantilla ni README automático, como ya fue aprobado; comprobar identidad/visibilidad y que no haya contenido preexistente inesperado.
2. Preparar y revisar snapshot local de288archivos, excluyendo ANTES de cualquier publicación los otros seis workflows. No publicar primero todo el repo para quitarlos después. El único workflow es clean-snapshot.yml exacto, sin push ni create.
3. Publicar las bases sin PR abierto y sin workflow_dispatch. Recuperar árboles/blobs y verificar ruta única de workflow, hashes, eventos, permisos y jobs. Repetir la comprobación para ambas bases y los heads antes de abrir PRs.
4. Consultar runs por API. Cualquier ejecución durante preparación requiere identificar evento/origen; no declararla imposible ni seguir a ciegas. Cero runs observado es evidencia acotada, no certificado de aislamiento.
5. Abrir deliberadamente los cuatroPRs y observar opened/synchronize conforme al diseño. Si Actions están deshabilitadas por política, eso sí sería un bloqueo real de ejecución a resolver al encontrarlo; no exigir que estén apagadas primero.

La copia inicial no dispara los otros seis workflows porque nunca se publican en el laboratorio. El historial de Corpus tampoco se importa. No hace falta cambiar on, permisos, jobs ni el sujeto experimental para conseguir esta preparación.

## Tres cuestiones distintas, no mezclar

**Disparo accidental de nuestro workflow durante preparación:** resuelto por condiciones de eventos y secuencia, sin toggle. Inspección del YAML real más semántica documentada, no ensayo remoto todavía.

**Privilegios efectivos del workflow concreto:** contents:read, checkout fijado, persist-credentials:false, runner ubuntu-24.04, sin environment ni workflow reutilizable. El archivo completo no referencia secretos personalizados ni configura env con ellos. Esto limita el camino observado, pero GITHUB_TOKEN sigue existiendo y checkout lo usa; no afirmar cero credenciales. No modificar el workflow para quitar ese token porque cambiaría el sujeto.

**Configuración administrativa global:** ausencia de webhooks/Apps, reglas heredadas o secretos configurados sigue NO MEDIDA. Apagar Actions tampoco prueba ninguna de esas ausencias ni impide que un webhook externo actúe. Los secretos personalizados se proporcionan a acciones mediante referencias/contexto/entradas; secretos de environment requieren que el job referencie ese environment. No confundir 'no se consumen aquí' con 'no existen'. No se elimina silenciosamente del diseño el requisito administrativo restante ni se certifica aislamiento completo por esta corrección.

La autorización ya recibida para el lote en comentario80170047153775 se conserva, incluido merge condicional solo dePR21 en head3b92dc432f285c00d5a45e717883c5c6e3fe46f9 después de ensayo concluyente/checks vigentes y sin bypass. Esta revisión no requiere repetir esa misma aprobación ni la convierte en autorización incondicional de merge. Este turno cuestiona el requisito: no crea el laboratorio ni ejecuta/mergea.

## Instrumento ejecutado y evidencia

Python3 con PyYAML BaseLoader en brain-env. Fuente lógica exacta del guard y de la comparación ejecutada; los comandos git show leen los SHA declarados, no un YAML inventado. No se incorporó el mutante al repo ni se lanzaron runs:

```python
import subprocess, yaml, copy, json
r = '/workspace/corpus-legal-tarija-qa'
p = '.github/workflows/clean-snapshot.yml'
raw = {}
def guard(d):
 assert set(d['on']) == {'pull_request','workflow_dispatch'}, 'unexpected_trigger'
 assert d['permissions'] == {'contents':'read'}, 'token_permissions'
 for job in d['jobs'].values():
  assert job['runs-on'] == 'ubuntu-24.04', 'runner'
  assert 'environment' not in job and 'uses' not in job, 'environment_or_reusable'
for label,sha in [('old','645d1732bec136bcc518070db42ff93437f95fd6'),('new','3b92dc432f285c00d5a45e717883c5c6e3fe46f9')]:
 d=yaml.load(subprocess.check_output(['git','-C',r,'show',sha+':'+p]),Loader=yaml.BaseLoader)
 guard(d); raw[label]={'sha':sha,'events':list(d['on']),'guard':'pass'}
 mutant=copy.deepcopy(d); mutant['on']['push']=''
 try: guard(mutant)
 except AssertionError as e: raw[label]['push_mutant']={'rejected':True,'reason':str(e)}
 else: raise AssertionError('push mutant survived')
print(json.dumps(raw,indent=2))
print('LIMIT: static YAML discrimination; no remote laboratory event emitted')
```

Salida completa, exit0, stderr vacío:

```text
{
  "old": {
    "sha": "645d1732bec136bcc518070db42ff93437f95fd6",
    "events": [
      "pull_request",
      "workflow_dispatch"
    ],
    "guard": "pass",
    "push_mutant": {
      "rejected": true,
      "reason": "unexpected_trigger"
    }
  },
  "new": {
    "sha": "3b92dc432f285c00d5a45e717883c5c6e3fe46f9",
    "events": [
      "pull_request",
      "workflow_dispatch"
    ],
    "guard": "pass",
    "push_mutant": {
      "rejected": true,
      "reason": "unexpected_trigger"
    }
  }
}
LIMIT: static YAML discrimination; no remote laboratory event emitted
```

El falsador podía rechazar exactamente la precondición afirmada: se agrega push a la copia y falla unexpected_trigger en ambos sujetos. No prueba la API de GitHub, ausencia de Apps ni futuras carreras. Git ls-remote confirmó main645d1732, PR21rama3b92dc43 y diseño16ae4057 antes de la corrección; ningún cambio de producto observado.

## Fuentes consultadas en vivo

[GitHub: on especifica los eventos](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).
[GitHub: eventos que disparan workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).
[GitHub: proporcionar secretos a un workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets).
[GitHub: secretos de environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).
[GitHub: token accesible a acciones y mínimo privilegio](https://docs.github.com/en/actions/reference/security/secure-use).

--- METODO TITAN ---
Accion delicada:NO, corrección documental de premisa; no configuración modificada. Modo:TITAN LIGERO. Rubrica:N/A. Instrumento:lectura de YAML reales, guard estructural y dos mutantes push rechazados; fuente/salida arriba. Review externo:pendiente. Estado:REQUISITO DE APAGAR ACTIONS REFUTADO COMO NECESARIO; ENSAYO REMOTO Y MERGE NO EJECUTADOS.
