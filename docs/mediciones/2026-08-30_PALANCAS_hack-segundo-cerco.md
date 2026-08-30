---
ambito: >
  el rastro material de las palancas del método en el frente hack-segundo-cerco: cuáles se
  aplicaron, cuál se apagó a propósito y con qué autoridad. No repite las mediciones del cerco,
  que están en su propio documento.
entrega: >
  la medida del lint de claridad sobre el texto de cierre, lo que devolvió el lector ingenuo y
  qué se cambió por ello, y la declaración firmada de por qué no hubo juez.
fecha: 2026-08-30
---

# Palancas del método — hack-segundo-cerco

**Búsqueda previa (C1)**: se buscó `*PALANCAS*` y `*LINT*` por nombre y `lector ingenuo|INFLESZ`
por contenido en todo el repositorio. Solo salieron los artefactos del disidente de este mismo
frente y `ENTREGA.md`, que es el documento de entrega del hackathon y no habla del método. No
había nada previo que mejorar.

## Lo aplicado

| Palanca | Rastro |
|---|---|
| Disidente de otro linaje, one-shot aislado | [`2026-08-30_DISIDENTE_umbral_cerco_2.md`](2026-08-30_DISIDENTE_umbral_cerco_2.md) y las dos llamadas crudas en `disidente_umbral_aislado_20260830/` |
| Kill-test de mundo real ejecutado | `agente/killtest_cerco_doble.py`, corrido dos veces y dentro de las trece de `pruebas_de_ruptura.sh` |
| Registro crudo re-evaluable | [`cerco_doble.json`](cerco_doble.json): los dos parecidos de cada uno de los 22 textos, con modelo y umbral |
| Huella estructural de las invocaciones externas | `disidente_umbral_aislado_20260830/*/request.json` y `response.json` |
| Lint de claridad | ver abajo |
| Lector ingenuo | ver abajo |

## Lint de claridad sobre el texto de cierre

El texto que se le entrega al operador se escribió a un archivo y se midió con
`tools/comunicacion/lint_claridad.py` del repositorio `cleveria-dominios`. Tres pasadas:

| Pasada | INFLESZ | Frases de más de 40 palabras | Resultado |
|---|---|---|---|
| primera | 77,6 | 3 | FALLA |
| tras partir las frases largas y enmarcar las salidas literales | 83,2 | 0 | PASA |
| tras los arreglos del lector ingenuo, medida de nuevo | 82,5 | 0 | **PASA** |

Se intentó declarar un waiver con motivo `medidor-cuenta-tabla` para las salidas literales de las
dos mediciones, y **la herramienta lo rechazó**: la puerta de claridad está activa desde el
2026-08-17 por una tasa de exenciones del 30 % sobre un umbral del 20 %, sellada por el operador,
y mientras esté activa el hallazgo se corrige en vez de declararse. Se corrigió: las salidas
literales van en bloques de código, que el medidor ya excluye por su cuenta.

## Lector ingenuo

Un subagente barato y sin ningún contexto del proyecto (`claude-haiku`) leyó el texto de cierre
antes de entregarlo. Devolvió cuatro cosas y **tres cambiaron el texto**:

1. «¿Qué es el banco?» — no estaba dicho en ninguna parte. Se añadió, en la segunda línea, de qué
   se compone el banco de 22 textos.
2. Contradicción aparente: «el segundo cerco no caza nada nuevo» contra «quita el punto único de
   fallo». Tenía razón en que el texto no explicaba cómo conviven. Se explicó: hoy dan el mismo
   resultado, pero si el primer modelo se retira o cambia de versión, el segundo sigue en pie.
3. «¿Está cableado el cerco en el grafo o no?» — el texto lo daba a entender a medias. Se
   reescribió el apartado para decirlo en la primera línea: **el sistema en marcha sigue usando
   un solo cerco**, y falta una línea en un archivo que es de otro frente.
4. «El título dice LISTO PARA CERRAR pero hay trabajo pendiente: ¿cierra o espera?» — se añadió un
   apartado que dice qué se espera del operador y que las mediciones pendientes son sugerencias,
   no requisitos.

## La palanca que NO se montó, y con qué autoridad

**No hubo juez, ni panel completo.** Lo apaga el **gate de oráculo (D5) del propio brief**: esta
tarea tiene un oráculo determinista —el kill-test dice PASA o NO PASA— y la corrida CF1 midió que
montar disidencia donde hay oráculo cuesta 3,0× y caza 0 errores.

Lo que sí se montó, y por eso no es un apagón total: un disidente **contra lo único que el
oráculo no puede comprobar**, que es si el umbral 0,686 está bien elegido — porque ese número es
una de las entradas del oráculo, no una de sus salidas. Y acertó: tumbó la justificación, que era
falsa.

**Fase cero no se montó como palanca aparte** por la misma razón, y porque el diseño venía
prescrito en el brief hasta el detalle de la regla de combinación. No había diseño propio que
atacar antes de ejecutar; lo que había que atacar era el número, y eso es lo que se atacó.
