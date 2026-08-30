---
ambito: >
  el ataque externo a UNA decisión concreta del frente hack-segundo-cerco: por qué el umbral del
  segundo cerco semántico vale 0,686 y no otra cosa. No cubre el resto del frente.
entrega: >
  los diez ataques del disidente con su disposición una por una —qué se acogió, qué se rechazó y
  con qué razón—, y el enlace a la petición y la respuesta crudas.
fecha: 2026-08-30
---

# Disidente de mecanismo — la elección del umbral del segundo cerco

**Búsqueda previa (C1)**: se buscó `*DISIDENTE*` por nombre y `ataqu|disidente` por contenido en
todo el repositorio. Lo único que salió fueron los propios artefactos crudos de esta llamada, más
`REVISION_JURADO.md` y `ENTREGA.md`, que son la revisión del jurado sobre la entrega entera y no
hablan del umbral. No había ningún documento previo que mejorar.

## Qué se atacó, y por qué solo eso

El brief de este frente trae un **gate de oráculo** (D5): la tarea tiene una prueba determinista
que dice sí o no, y montar disidente y juez donde hay oráculo costó 3,0× sin cazar ni un error.
Por eso **no** se montó el panel completo. Se montó un solo disidente, y contra lo único que el
oráculo **no** puede comprobar: el kill-test dice si los falsos positivos suben de dos, pero no
puede decir si el número 0,686 está bien elegido, porque ese número es una de sus entradas.

| | |
|---|---|
| Modelo | `z-ai/glm-5.3` (titular de `disidente-de-mecanismo`), vía OpenRouter, one-shot, sin herramientas |
| Petición cruda | [`_prompt_disidente_umbral.txt`](_prompt_disidente_umbral.txt) |
| Respuesta cruda | [`disidente_umbral_aislado_20260830/openrouter_aislado_2026-08-30T212040Z_1337345_z-ai_glm-5_3/`](disidente_umbral_aislado_20260830/) |
| Coste y corte | 1.161 → 18.688 tokens · USD 0,0839 · `finish=stop` |
| Veredicto | **NO SOSTENIBLE** |

Hay un primer intento en ese mismo directorio, de las 21:19:42Z, con `response.json` **vacío**: la
llamada volvió sin nada. Se deja como está en vez de borrarlo, porque una llamada que no devolvió
respuesta también es un dato sobre el canal.

## Los diez ataques y qué se hizo con cada uno

| # | Ataque, en una línea | Disposición |
|---|---|---|
| 1 | Contando los dos «difíciles» como los textos legítimos que son, las clases se **solapan** (legítimo más alto 0,768 > juicio más bajo 0,701): margen real −0,067, y ningún umbral las separa. El +0,030 aparece solo tras excluirlos. | **ACOGIDO.** La aritmética es correcta. Se escribe entera en `src/cerco_semantico.py`, junto al umbral, para que nadie lea el +0,030 como el margen contra todo el mundo. No cambia el número: esos dos casos ya estaban declarados como falsos positivos desde antes de que existiera el segundo cerco, y el límite que los produce ya estaba documentado. |
| 2 | La validación es **circular**: el umbral es el punto medio de los mismos datos con que luego se declara «9/9 y 0 molestias». Cero bits de evidencia. | **ACOGIDO EN PARTE, y es un límite del método, no de este frente.** Cierto para el «0 molestias»: es aritmética, no prueba. NO cierto para el «9/9»: las nueve evasiones las escribió un atacante externo con el encargo de evadir, sin ver el umbral, y ese banco existía antes. Lo que arregla esto es un banco *held-out* pre-registrado, que no cabe antes de las 08:00 y se propone al operador, no se improvisa. |
| 3 | Con n=9 y n=5 las tasas son desconocidas: 9/9 solo acota la caza por encima de ~72 %; 0/5 admite hasta ~45 % de falsos positivos. | **ACOGIDO COMO LÍMITE DECLARADO.** Cierto. Ninguna de las cifras de este frente debe leerse como una tasa; son conteos sobre un banco de 22 casos. Ampliar el banco a los ~200 cierres reales que pide es trabajo real y se propone; no se hace a las 21:30 del día antes. |
| 4 | Los 0,015 de colchón caben dentro del ruido de un coseno: una falta de ortografía o un sinónimo mueven más que eso. | **ACOGIDO COMO NO MEDIDO.** Plausible y sin medir, tanto a favor como en contra. Es el ataque que más barato sale de comprobar (perturbar los dos textos frontera y volver a puntuar) y el primero que habría que correr si este frente sigue. |
| 5 | Como no hay discrepancias, **las nueve evasiones también las cazaba el cerco 1**: no hay ni una muestra de un texto que evada al primero, así que el valor añadido del segundo está sin medir. | **ACOGIDO, y es el hallazgo más importante de la revisión.** Está escrito en la docstring de `techo_semantico_doble` con estas palabras: lo demostrado es que el segundo cerco **no cuesta nada** y quita el punto único de fallo, NO que cace más. Cambia lo que este frente puede reclamar. |
| 6 | La justificación era **falsa sobre sus propios datos**: 0,697 también separa los veintidós, y ningún parecido cae entre 0,686 y 0,697, así que los dos números deciden **idéntico**. La elección era observacionalmente vacía. | **ACOGIDO, y reescrito.** La frase «un umbral que solo separa los casos fáciles no separa nada» era falsa y se borró. La razón que queda es la de abajo, y es otra. |
| 7 | Regla **simétrica** (punto medio) para una pérdida **asimétrica**: un falso negativo es una máquina firmando una absolución; un falso positivo es una llamada de teléfono. | **ACOGIDO, y es lo que ahora justifica el número.** Con esa asimetría, de las dos cifras que deciden igual sobre lo medido hay que quedarse con la que deja más colchón del lado caro: 0,686 deja 0,015 contra un juicio nuevo, y 0,697 deja 0,004. Bajar más está vedado porque por debajo de 0,671 empieza a molestar sobre cierres ordinarios, que sí es fallo. 0,686 es el punto más prudente que cabe sin pagar falsos positivos. |
| 8 | El «0/5 ordinarios» es una muestra **curada** que esquiva justo el vocabulario de cierre que dispara el cerco. | **ACOGIDO COMO LÍMITE DECLARADO**, y coincide con el ataque 3: el coste operativo real solo lo dicen cierres reales sin curar. Se propone al operador. |
| 9 | Un umbral global sobre el máximo de 16 anclas mezcla 16 escalas de discriminación distintas. | **RECHAZADO PARA ESTE FRENTE, no por falso sino por fuera de alcance.** Vale igual para el cerco 1, que lleva medido y publicado desde el 27 de agosto con la misma estructura; tocarlo sería rediseñar la pieza vieja la noche antes de publicar. Se anota como trabajo posterior. |
| 10 | Cero discrepancias en 22 casos admite hasta ~13 % de discrepancia real, y apunta a errores **correlacionados** (el mismo ciego léxico en dos embeddings del mismo fabricante). | **ACOGIDO junto con el 5.** Es el mismo hallazgo por otro lado, y refuerza que lo que se reclama sea la redundancia y no la cobertura. Que los dos modelos sean del mismo fabricante es, además, una limitación que conviene decir en voz alta. |

## Qué cambió por esta revisión

Tres cosas, todas en `src/cerco_semantico.py`, y ninguna es cosmética:

1. **Se borró una justificación falsa** del umbral (ataque 6) y se puso la verdadera: la
   asimetría de las dos clases de error (ataque 7). El número no cambió; la razón sí, y antes
   era mentira.
2. **Se declaró el solapamiento** de las dos clases cuando se cuentan los dos falsos positivos
   declarados (ataque 1): margen −0,067, ningún umbral separa.
3. **Se acotó lo que este frente puede reclamar** (ataques 5 y 10): el segundo cerco demuestra
   que no cuesta nada y que quita el punto único de fallo; **no** demuestra que cace más, porque
   no hay en el banco un solo texto que evadiera al primero.

## Lo que queda sin medir, y se propone al operador

Ninguna de estas cuatro cabe antes del punto de no retorno, y ninguna es opcional si el artículo
quiere reclamar más que «tres modelos»:

- Perturbar los dos textos frontera (0,671 y 0,701) con sinónimos y erratas y volver a puntuar
  — es la más barata, y decide si el margen de 0,030 es señal o ruido (ataque 4).
- Un banco de juicios escritos para evadir **al cerco 1 concretamente**, que es el único
  experimento que mediría para qué sirve el segundo (ataques 5 y 10).
- Cierres reales sin curar contra el cerco, para saber el coste operativo de verdad (ataques 3 y 8).
- Un banco *held-out* pre-registrado, para que el umbral deje de elegirse sobre los datos con que
  luego se aprueba (ataque 2).
