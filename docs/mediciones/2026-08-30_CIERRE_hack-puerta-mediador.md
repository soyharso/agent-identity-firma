---
ambito: >
  la puerta de escritura del entregable: qué se construyó para que un cierre sin sobre firmado
  no pueda cambiar el registro, qué se midió antes y después, y qué queda pendiente.
entrega: >
  el endpoint mediador con la reserva de un solo uso dentro, la prueba de ruptura que demuestra
  que el agente ya no puede escribir directo, y las doce anteriores todavía en verde.
---

# El sobre firmado deja de ser un recibo — medición del frente `hack-puerta-mediador`

**Fecha**: 2026-08-30 · **Rama**: `worktree-hack-puerta-mediador`, desde `b415034` ·
**Entorno**: preproducción, proyecto `ai-transf-lab-0827`. Nada de esto es producción.

Registro crudo con el que rehacer cada número:
[`docs/mediciones/puerta_mediadora.jsonl`](puerta_mediadora.jsonl). Cada línea lleva su
comando.

## Qué es un sobre, en una frase

Un **sobre** es el papelito firmado que acompaña a un cierre. Dice qué petición se cierra, en
qué estado queda, el resumen del texto que se juzgó y cuándo se decidió. Va firmado con una
clave de Cloud KMS: la del agente, o la de la persona. El **verificador** lo comprueba sin red y
sin credenciales, así que cualquiera puede repetirlo. Y **el registro** es lo duradero: el
documento de Firestore donde vive el estado de cada petición.

## La frase que antes no se podía decir

**Sin sobre válido, no ocurre nada.**

Hasta hoy el agente tenía `roles/datastore.user` —el permiso de ESCRIBIR en Firestore— y
escribía el estado él mismo. El sobre
firmado se producía, se guardaba y probaba **después** quién cerró qué — pero nada rechazaba un
cierre que llegara sin él. Era un recibo, no una puerta.

Medido, no argumentado (M1 y M2 del registro crudo). HTTP (el código con que la nube contesta
a cada llamada) dice 200 cuando algo se hizo y 403 cuando no había permiso para hacerlo.

| Momento | El agente desplegado intenta escribir Firestore directo | Respuesta de la nube |
|---|---|---|
| Antes | `POST /intentar-escribir-directo` | **HTTP 200 · `written: true`** |
| Después | el mismo comando | **HTTP 403 `PERMISSION_DENIED`** · `written: false` |

Y no lo sostiene el código, que cualquiera puede editar: lo sostiene el permiso. Si alguien
borrara las comprobaciones del verificador, el agente seguiría sin poder escribir, porque la
credencial que haría falta ya no la tiene su identidad.

## Cómo quedó

Una sola imagen, dos servicios. Lo que los separa no es el código: es con qué identidad corren.

| Servicio | Identidad | Permiso sobre el registro | Qué hace |
|---|---|---|---|
| `candado-firma` | `sa-agente-curador` | `roles/datastore.viewer` — **solo lee** | el agente: dictamina, firma con su clave, pide |
| `mediador-cierre` | `sa-mediador` | `roles/datastore.user` — **el único que escribe** | verifica el sobre y solo entonces escribe |

El mediador expone exactamente dos entradas, y la diferencia entre ellas es toda la puerta:

- **`/aplicar-cierre`** — verifica el sobre **contra esta petición** y solo entonces escribe. Es
  lo único en todo el sistema que puede escribir `sobre`, `firma` y `hash_contenido`.
- **`/anotar`** — el trámite: reservar, apartar para una persona, anotar una decisión, anotar el
  desenlace de una pasada que no firmó nada. Tiene **prohibido** tocar esos campos, y la
  prohibición no depende de quien llame: el diccionario que se escribe se construye campo por
  campo en `src/estado.py::anotar_local`.

Los dos cierres que el encargo señalaba están desviados:
`agente/grafo.py:registrar()` (veredicto y sobre de la máquina) y `servicio/main.py:/decidir`
(firma humana). Las reservas y las lecturas se quedaron como estaban, salvo por ir ahora por el
mediador, que es quien tiene la credencial.

## El agujero medido, que no estaba en el encargo

`/decidir` verificaba la firma humana **sin decirle al verificador para qué petición se estaba
presentando**, y luego la guardaba bajo el `peticion_id` del cuerpo de la llamada. Medido (M4):

```
sobre firmado para : PET-VECINO
presentado en      : PET-DESTINO
ANTES (/decidir)   : OK              ← se habría guardado bajo PET-DESTINO
AHORA (la puerta)  : CONTEXTO_AJENO  ← "la firma es válida, pero aprobaba otro caso"
```

Es el ataque más plausible de todos porque no exige romper nada: basta con copiar una aprobación
humana que ya existe. La firma es buena, el firmante está en el directorio, el hash cuadra
consigo mismo y el estado está en alcance. Lo único que lo delata es que **no era para ese
caso**, y esa comprobación no se estaba haciendo en el camino de escritura. El verificador ya
sabía hacerla —`peticion_esperada` existe desde antes y su propio comentario dice que la pone
quien verifica, nunca el sobre—; lo que faltaba era llamarla.

## La reserva de un solo uso: por qué no es `reservar()` a secas

El encargo pedía «llamar a `estado.reservar()` antes de aplicar». No sirve, y se comprobó
corriéndolo: `reserva_hash` **ya la tiene puesta** el despertar —la pasada que arranca cuando el
temporizador llama a `/despertar` y procesa lo que haya pendiente— antes de llamar al modelo
(`grafo.correr_para_servicio`). Es su candado para no gastar el modelo dos veces. Así que pedirla
otra vez dentro de la puerta devuelve `False` en el **primer cierre legítimo**.

Lo que hay es `estado.reservar_cierre()`: el mismo patrón transaccional, diez líneas, marcado con
la huella de la **firma** en vez del hash del texto. Dos sobres distintos no comparten huella. No
es un contador nuevo ni un nonce nuevo; es la misma reserva aplicada a otra cosa. El ataque A6 lo
mide: el primer sobre escribe, el segundo no reescribe la firma y el registro no cambia.

## Las pruebas

`./pruebas_de_ruptura.sh` — 13/13 en verde, 147 s, invocación estándar, 2026-08-30 16:45:46 -05.
Eran doce y ahora son trece: **ninguna de las doce anteriores se debilitó ni se retiró**, se
añadió una. Cada una intenta romper una promesa concreta del sistema y falla al intentarlo.

| # | Prueba | Qué rompe |
|---|---|---|
| 1 | canonical-json | la norma que fija cómo se convierte un dato en bytes para poder firmarlo (RFC 8785), byte a byte, acentos y enteros incluidos |
| 2 | signature-replay | una aprobación humana auténtica no se puede mover de caso |
| 3 | act-binding | dos resoluciones idénticas no producen sobres intercambiables |
| 4 | channel-port | el canal de WhatsApp está desacoplado de la firma |
| 5 | managed-filter | el filtro del proveedor no caza nuestro ataque en español |
| 6 | prompt-injection | 8 inyecciones, 4 idiomas, frenadas por el techo |
| 7 | key-scope | una clave no puede autorizar un estado fuera de su alcance |
| 8 | fleet-identity | dos agentes no pueden prestarse la clave |
| 9 | voice | un juicio dictado por voz sigue exigiendo firma humana |
| 10 | semantic-fence | 9/9 cazados, 2 falsos positivos declarados |
| 11 | durability | 5 pasos, 5 procesos, sobrevive a una muerte abrupta |
| 12 | co-signer | una segunda familia de modelos tiene que coincidir; su silencio cierra la puerta |
| **13** | **write-gate** | **7 cierres falsos rechazados; el registro no cambia** |

La decimotercera, con detalle (`python3 agente/killtest_puerta.py`):

```
  ✓ A1 · cierre SIN sobre                        rechazo=SIN_SOBRE             registro_intacto=True
  ✓ A2 · sobre SIN firma                         rechazo=SIN_SOBRE             registro_intacto=True
  ✓ A3 · firma auténtica del caso de al lado     rechazo=CONTEXTO_AJENO        registro_intacto=True
  ✓ A4 · sobre retocado para que encaje          rechazo=FIRMANTE_DESCONOCIDO  registro_intacto=True
  ✓ A5 · la MÁQUINA cierra 'descartada'          rechazo=FUERA_DE_ALCANCE      registro_intacto=True
  ✓ A6 · el mismo sobre, dos veces               1ª escribió=True 2ª=False     registro_intacto=True
  ✓ A7 · el trámite intenta colar una firma      firma_en_registro=la del sobre verificado
  ✓ el AGENTE DESPLEGADO escribe Firestore directo  http=403 PERMISSION_DENIED registro_intacto=True
```

El criterio no es lo que la puerta **contesta**: es lo que el registro **es** después. Una puerta
que dice «no» y escribe igual no pasa esta prueba.

El último ataque lo lanza el **servicio desplegado, con su propia identidad**, contra la interfaz
de Firestore a pelo — sin `src/estado.py`, sin mediador y sin verificador. Es la hermana de
`/intentar-suplantar`, y vale por lo mismo: quien empuja la puerta es el mismo proceso que
correría en producción, y lo que se lee es lo que la nube le contestó a él. Si un día
contestara 200, esta ruta lo enseñaría igual.

## El orden en que se hizo, que era la regla dura

1. Construir la puerta y desviar los dos cierres, con el rol todavía puesto.
2. `demo.sh 1-5` en verde y **las doce anteriores en verde** (M6: 12/13 — la decimotercera roja a
   propósito, porque es justo lo que mide).
3. **Solo entonces**, y en este orden, que importa: primero se le **concede**
   `roles/datastore.viewer` (leer) y después se le **quita** `roles/datastore.user` (leer y
   escribir). Al revés habría un momento en que el agente no puede ni leer, y el agente lee
   todo el rato: reconstruye el estado del dominio en cada pasada.
4. Re-pasar `demo.sh 1-5` (M10) y las trece (M8). Idénticos a antes, sin el permiso de escribir.

## Lo que hay que saber para deshacerlo

Un `gcloud` de diez segundos, tal como decía el encargo:

```bash
gcloud projects add-iam-policy-binding ai-transf-lab-0827 \
  --member="serviceAccount:sa-agente-curador@ai-transf-lab-0827.iam.gserviceaccount.com" \
  --role="roles/datastore.user" --condition=None
```

**Pero IAM —el sistema de permisos de Google Cloud— tarda en propagar**: medido (M3), entre 60 y 80 segundos desde que el comando vuelve
hasta que el servicio nota el cambio. Quien lo re-otorgue no debe creerle a la primera lectura.

Si además hiciera falta volver al mundo anterior del todo, `MEDIADOR_URL` fuera del servicio
`candado-firma` devuelve las escrituras al proceso del agente.

## Interferencia medida entre frentes — esto le sirve al operador antes de grabar

`agente/killtest_durabilidad.py` escribe el documento **`peticiones/PET-002` de la base real**.
El 2026-08-30 lo estaban escribiendo a la vez, sobre el mismo documento:

- este frente,
- `hack-libro-encadenado`,
- `hack-segundo-cerco` (corriendo el banco entero),
- y el trabajo de Cloud Scheduler `despertar-candado`, cada 15 minutos, por su cuenta.

**Síntoma**: el paso 5 sale `NO PASA` sin que nadie haya roto nada — aparece en `PET-002` una
firma que el proceso no escribió. `hack-libro-encadenado` lo confirmó con medición propia:
aislado pasa 3 de 3; dentro del banco falla 2 de 2.

**Mitigación**, en `src/estado.py`, con el valor por defecto intacto:

```bash
COLECCION_PETICIONES=peticiones_puerta ./pruebas_de_ruptura.sh
```

La corrida registrada en `libro/pruebas_de_ruptura.json` (M8) es la **estándar**, sin aislar y
con el temporizador activo: 13/13. O sea que el banco pasa igual — pero si un día sale un rojo en
`durability`, esto es lo primero que hay que mirar, y no un defecto del producto.

## Lo que NO se hizo, dicho y no maquillado

- **`README.md`, `ENTREGA.md` y `DEVPOST_SUBMISSION.md` no describen la puerta.** No dicen nada
  falso —no la mencionan—, pero tampoco cuentan lo que hoy es la pieza que convierte el recibo en
  una garantía. Están fuera de la frontera de escritura de este frente. **Decisión del operador.**
- **`demo.sh` no la enseña.** La toma 3 sigue enseñando el 403 de la clave humana, que es el
  argumento de la firma. El 403 de la **escritura** —que es el argumento de la puerta— existe y se
  puede llamar en vivo (`/intentar-escribir-directo`), pero no está en ninguna toma. `demo.sh`
  está fuera de la frontera de escritura de este frente. **Decisión del operador.**
- **`demo.sh` toma 2 espera 90 segundos por una condición que no se puede cumplir.** Espera a que
  las cuatro peticiones tengan veredicto. Dos de ellas se detienen a esperar a una persona, y un
  flujo detenido nunca llega al nodo que escribe el veredicto. El resultado es un
  `⚠ still not ready after 90s` amarillo en cámara. **Es anterior a este frente**: la ruta de la
  pausa tampoco llegaba antes al registro. Y `demo.sh` no es de este frente. **Decisión del
  operador.**
- **El libro en disco sigue escribiéndose con `FIRMAS.open("a")`.** El frente
  `hack-libro-encadenado` migró ese punto a `libro_cadena.anexar(FIRMAS, fila)` en su propia rama;
  `src/libro_cadena.py` no existe en esta, así que importarlo aquí habría tumbado el banco entero.
  Regla de conflicto acordada con ese frente y confirmada por él palabra por palabra: **se queda el
  cuerpo de `registrar()` de este frente. Dentro, la escritura del libro en disco es
  `libro_cadena.anexar(FIRMAS, fila)`, sin `FIRMAS.parent.mkdir(...)`. La aplica quien fusione
  segundo.** El orden importa: la escritura del libro va **antes** de la bifurcación, para que
  quede rastro también de lo que la puerta rechazó.

## Palancas del método, con su rastro

Salida literal de la herramienta sobre este documento, para que la cifra no dependa de cómo la
cuente esta prosa:

```
$ python3 tools/comunicacion/lint_claridad.py docs/mediciones/2026-08-30_CIERRE_hack-puerta-mediador.md
INFLESZ=76.0 (umbral 55.0) · 13.7 pal/frase · largas>40: 0 · siglas sin glosa: 0
PASA
```

- **Lint de claridad** sobre este mismo documento
  (`tools/comunicacion/lint_claridad.py`): **PASA**. INFLESZ (el índice que mide lo fácil de leer
  que es un texto en español; más alto, más fácil) da 76,0 sobre un umbral de 55,0, con 13,7 palabras por frase. Ninguna frase pasa de 40
  palabras y no queda ninguna sigla sin glosa. Dos correcciones
  entraron por él: HTTP y RFC 8785 no estaban glosadas, y ahora lo están. Se intentó declarar un
  waiver por «sigla canónica» y **la herramienta lo rechazó**: la puerta de claridad está activa
  desde 2026-08-17, así que el hallazgo se corrige, no se declara.

- **Lector ingenuo** (subagente barato, sin contexto, sobre este informe y sobre el texto de
  cierre). Veredicto: entendió la pieza central —«se construyó una puerta para que un agente no
  pueda escribir sin un documento firmado válido»— y devolvió **nueve cosas que no se entendían y
  tres dudosas**. Cuatro se corrigieron y están arriba:
  1. **«sobre» no se definía en ninguna parte.** Se añadió la sección «Qué es un sobre».
  2. **«el despertar» aparecía sin explicar quién es.** Ahora se dice.
  3. **«el banco solo creció» no decía de qué banco.** Ahora dice que eran doce y son trece.
  4. **El orden de la permuta de permisos parecía invertido** («si le quitan `user` primero,
     queda sin poder escribir»). Se reescribió diciendo cuál se concede y cuál se quita.

  Lo que **no** se corrigió, y por qué. `PET-002`, `CONTEXTO_AJENO`, `FUERA_DE_ALCANCE` y los
  demás códigos de rechazo son vocabulario del propio sistema. Quien lee este documento los usa a
  diario, y glosarlos aquí duplicaría el directorio de claves y el verificador, que es donde
  viven.

- **Kill-test de mundo real EJECUTADO antes de cerrar**: `agente/killtest_puerta.py`, y no contra
  un doble — el último ataque lo lanza el servicio desplegado con su identidad real contra la
  nube real.

- **Registro crudo re-evaluable**: [`docs/mediciones/puerta_mediadora.jsonl`](puerta_mediadora.jsonl),
  doce mediciones con su comando.

- **Disidente y juez: NO se montaron, y es una decisión declarada del arnés**, no un olvido. El
  perfil de este frente trae el gate de oráculo (D5). Esta tarea tiene oráculo determinista: el
  código de salida de trece pruebas, la respuesta de la nube, y el contenido del documento antes
  y después. Donde hay oráculo, la medición de la casa dio 3,0× de coste y 0 errores cazados por
  la disidencia. Se verificó con el oráculo y se cerró.
