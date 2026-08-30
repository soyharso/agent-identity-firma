---
ambito: >
  el cierre del frente hack-segundo-cerco: qué se entregó, con qué medición, y qué queda en manos
  del operador. Es el texto que se le entregó al operador, guardado tal cual.
entrega: >
  las dos mediciones con su salida literal, la condición de parada comprobada, lo que cambió por
  la revisión externa, y lo que este frente NO hizo y por qué.
fecha: 2026-08-30
---

# FLOTA hack-segundo-cerco: LISTO PARA CERRAR

La condición de parada se cumple: **los falsos positivos siguen en dos.** Trece pruebas de
ruptura en verde, las doce de antes más la nueva.

Todo lo que sigue se mide sobre el mismo banco de 22 textos. Son 9 evasiones que escribió un
atacante externo, 5 cierres legítimos ordinarios, 2 cierres legítimos difíciles a propósito y
6 casos del banco viejo que llegan hasta la firma.

## Las dos mediciones

Antes, con un solo cerco (`gemini-embedding-001`, umbral 0,70):

```
  juicios que se escapan (lo grave) : 0/9
  molestias sobre cierres normales  : 0/5
  coste declarado sobre los difíciles: 2/2
```

Después, con los dos cercos y la regla de que basta uno para exigir persona:

```
  cerco 1: gemini-embedding-001 · umbral 0.7
  cerco 2: text-multilingual-embedding-002 · umbral 0.686

  juicios que se escapan (lo grave)   : 0/9
  molestias sobre cierres ORDINARIOS  : 0
  coste declarado sobre los difíciles : 2/2
  FALSOS POSITIVOS EN TOTAL           : 2   (tope que autorizó este frente: 2)
  casos en que los dos cercos discrepan: 0/22

  VEREDICTO: PASA
```

## El umbral del segundo cerco: 0,686, y no salió a ojo

El 0,70 vigente es del otro modelo y de otra escala. El nuevo sale de la separación medida sobre
el banco completo: el juicio con el parecido más bajo da 0,701, y el cierre legítimo ordinario
más alto da 0,671. El umbral va por el medio.

## Lo que cambió porque un disidente externo lo tumbó

Un modelo de otro linaje atacó la elección del umbral y devolvió NO SOSTENIBLE con diez ataques.
Tres cambiaron el trabajo:

1. **La razón que yo había escrito era falsa sobre mis propios datos.** Decía que 0,697 «solo
   separa los casos fáciles», y no es verdad. Ningún texto del banco cae entre 0,686 y 0,697, así
   que los dos números deciden idéntico. Lo que de verdad los separa es dónde queda el colchón
   para los textos que nadie ha escrito todavía. Y ahí los dos errores no valen lo mismo. Que se
   escape un juicio es una máquina firmando una absolución. Un falso positivo es una llamada a
   una persona. 0,686 deja 0,015 de colchón del lado caro; 0,697 deja 0,004. El número no cambió;
   la razón sí, y antes era mentira.
2. **Contando los dos falsos positivos declarados como los textos legítimos que también son, las
   dos clases se solapan** y no hay ningún umbral que las separe. Es el límite que ya estaba
   documentado, pero no estaba dicho junto al número.
3. **Este banco no demuestra que el segundo cerco cace más.** Como no hay ni una discrepancia,
   cada juicio que caza el segundo lo cazaba ya el primero: no hay en el banco un solo texto que
   evadiera al cerco 1. Lo demostrado es que no cuesta nada. Y que quita el punto único de fallo,
   que no es lo mismo que cazar más. Hoy los dos dan el mismo resultado. Pero si mañana el
   primer modelo se retira, cambia de versión o se cae, el segundo sigue en pie y el control no
   se queda en cero. Es una segunda muestra independiente, no más cobertura.

## Lo que no hice, y por qué

**El cerco doble existe y está medido, pero el grafo todavía no lo llama.** Dicho sin rodeos: hoy
el sistema en marcha sigue usando un solo cerco. El segundo vive en el módulo, tiene su umbral
medido y su prueba propia dentro de la suite, y cualquiera puede invocarlo; lo que falta es que
`agente/grafo.py` llame a `techo_semantico_doble` en vez de a `techo_semantico`. Es una línea.

No la hice porque ese archivo es de otro frente y el brief me prohíbe tocarlo. **Y de paso: el
brief afirma que `agente/grafo.py` no importa el cerco, y eso es falso** — lo importa en la
línea 34 y lo llama en la 152. Ya avisé a `hack-puerta-mediador` por si le toca a él. **Esa línea
la tienes que encargar tú a quien tenga el archivo**; yo no puedo.

**No monté juez ni panel completo.** El brief trae el gate de oráculo: hay una prueba determinista
que dice sí o no, y montar el panel donde hay oráculo costó 3,0 veces sin cazar un error. Monté un
solo disidente, contra lo único que el oráculo no puede comprobar: si el número 0,686 está bien
elegido, porque ese número es una de sus entradas.

## Lo que queda sin medir

Son **sugerencias, no requisitos**: la rama cierra sin ellas. Ninguna cabe antes de las 08:00.

- Perturbar los dos textos frontera con sinónimos y erratas. Dice si el margen de 0,030 es señal
  o ruido, y es la más barata.
- Un banco de juicios escritos para evadir al cerco 1 concretamente. Es lo único que mediría para
  qué sirve el segundo.
- Cierres reales sin curar contra el cerco, para saber el coste operativo de verdad.

## Qué se espera de ti ahora

Una cosa sola: **decidir si la rama entra**. Está commiteada y verde; no la fusiono yo, y no
cierro la ventana. Si entra, encarga aparte la línea del grafo a quien tenga ese archivo. Las
tres mediciones de arriba pueden esperar a después del hackathon.

## Aviso de otro frente

`hack-puerta-mediador` avisó de una colisión en Firestore con `killtest_durabilidad.py` y pausó un
job de Cloud Scheduler que lo reactivará al cerrar. Le contesté que no lo necesito activo. La
prueba de durabilidad salió verde en mis dos corridas.
