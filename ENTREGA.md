# La entrega: guion del vídeo y comprobación contra la rúbrica

Documento de trabajo para quien grabe. **Nada de esto se ha enviado a ningún sitio.**

## 1 · Comprobación contra los requisitos obligatorios

Sin esto no se puntúa nada, así que va primero:

| Requisito | Estado | Prueba |
|---|---|---|
| Un modelo Gemini 3.5 o superior | **cumplido** | `gemini-3.6-flash` por Vertex. Se eligió sobre la 3.7 porque la última está congestionada y devuelve error de recurso agotado — medido. |
| Al menos un marco de agentes de Google | **cumplido** | el kit de agentes, versión 2.8, con grafo, nodos de función y pausa nativa. |
| Al menos un servicio de infraestructura | **cumplido, cuatro** | Cloud Run, Cloud KMS, Firestore y Cloud Scheduler. |
| Proyecto creado dentro del periodo | **cumplido** | repositorio creado el 2026-08-27. |

## 2 · Las cuatro tomas del vídeo — SUPERSEDED 2026-08-27

> **SUPERSEDED 2026-08-27 por el guion medido, en `docs/strategy/metodo/ganar-hackathon/` del
> repositorio del método. Razón: estas cuatro tomas ya no son el guion, y su apertura quedó
> ÚLTIMA de cuatro en una prueba con tres jurados ciegos y orden rotado.**
>
> **Si estás leyendo esto para grabar, el guion no es este archivo.** Se conserva abajo por
> trazabilidad, no como instrucción. Dos cosas que ya son falsas aquí: la apertura ganadora es
> «¿Quién firmó esto?», y los agentes están en **preproducción**, no en producción.

### Toma 1 — el defecto real (40 s)

Se enseña el registro del 26 de agosto —del sistema con el que trabaja el propio equipo, con los
agentes en **preproducción**—: **58 filas firmadas «humano» que cerró una máquina**, cuatro de
ellas en estado descartada.

> «Esto no es un ejemplo inventado. Pasó en nuestro sistema hace dos días. La única forma de que
> un agente cerrara una petición era firmando como si fuera una persona.»

### Toma 2 — el agente trabaja solo (60 s)

Se dispara el temporizador y se enseña el resultado de las tres peticiones:

| Petición | Qué hace |
|---|---|
| evidencia comprobable en un commit | **la máquina firma** |
| «se descarta la queja del cliente» | **el flujo se detiene y espera a una persona** |
| «creo que ya funciona» | se devuelve sin firma |

> «Un modelo decide. Seis funciones deterministas hacen todo lo demás. El modelo puede pedir más
> prudencia; nunca puede darse más autoridad.»

### Toma 3 — la que gana: la nube le dice que no (60 s)

En vivo, el agente intenta firmar con la clave de la persona:

```
HTTP 403  PERMISSION_DENIED
Permission 'cloudkms.cryptoKeyVersions.useToSign' denied on resource '…/clave-humano'
```

Y el servicio, cuando se le pide que firme como humano, responde:

> **«este servicio no puede firmar como humano, y no debe»**

> «No es que el agente no quiera. Es que no puede. Y esto no lo dice nuestro código: lo dice la
> nube.»

### Toma 4 — cualquiera lo comprueba (60 s)

Se corre el verificador **sin credenciales de ninguna clase**, con las dos claves públicas que
viajan en el repositorio. Y se enseña el dato incómodo:

| Texto | ¿Lo caza el filtro de inyección de Google? |
|---|---|
| inyección clásica, en inglés | sí, confianza alta |
| **nuestro ataque, en español** | **no** |

> «Medimos el filtro del propio Google contra nuestro ataque. No lo caza. Por eso la garantía no
> vive en un filtro: vive en una función que no razona y en una clave que la máquina no alcanza.»

## 3 · Comprobación contra los criterios de puntuación

### Innovación y utilidad operativa — 40%

- **Un defecto real y medido**, con cifras, de dos días antes. No un caso de ejemplo.
- **Elimina fricción de verdad**: la máquina cierra lo comprobable sola y molesta a la persona
  solo cuando hay un juicio de por medio.
- **Ejecución autónoma, con el freno en la misma frase**: despierta cada quince minutos por su
  cuenta **y con su propia identidad**, y lo primero que se encuentra al despertar es el techo de
  lo que puede autorizar. Medido con jurados ciegos: prometer autonomía **antes** de enseñar el
  límite se lee como venta, y con razón.

### Disciplina de arquitectura — 30%

- **Un solo modelo en todo el flujo**, y está donde hace falta juicio. Todo lo demás son
  funciones: más barato, más rápido y comprobable.
- **Una sola compuerta de política**: el alcance por clave, en un archivo y no en el código.
- **El verificador no depende de nada**: ni red, ni credenciales, ni cuenta.
- **Nueve pruebas de ruptura que se ejecutan**, más un verificador que corre sin red ni
  credenciales. Una de las nueve mide al proveedor en su contra, y otra guarda los nueve textos
  con que un atacante externo rompió el cerco semántico antes de que se entregara.
- **Lo ausente se declara ausente, y son tres**: la pasarela, el **catálogo de agentes** y la
  memoria de largo plazo. Ninguna se finge, y el catálogo se quitó de los materiales el
  2026-08-27 al comprobar que no existía nada que lo respaldara.

### Demostración y madurez — 30%

- **Arranque desde cero** comando a comando, comprobado, incluido el permiso que **no** se
  concede.
- **Diagrama** que se dibuja solo al abrir el repositorio.
- **La promesa separada** en garantizado y mitigado.
- **Historial honesto**: cada fallo encontrado por un atacante está en los mensajes de los
  commits, con su medición.

## 4 · Lo que falta, y solo lo puede hacer una persona

1. **Grabar el vídeo.** El guion está; son cuatro tomas.
2. **Compartir el repositorio** con los dos correos del organizador.
3. **Publicar una dirección donde probarlo**, o enseñar el servicio en el vídeo.
4. **Inscribir la entrega.**

Nada de eso lo hace un agente, y nada de eso se ha hecho.

## 5 · La probabilidad, sin adornos

Entre el **3% y el 5,5%** de llevarse algún premio (actualizada el 2026-08-27; la anterior,
1,1%–5,6%, es de antes de que el paquete estuviera terminado). Sigue siendo poco, y la banda ya
no se multiplica por «si se termina», porque está terminado: lo que queda son actos del operador
—inscribir, grabar, publicar—, y sin ellos la probabilidad no es baja, es cero.

**Lo que justifica el intento no es el premio.** Es que el componente resuelve un defecto real
nuestro, la norma del verificador tapa un agujero del método, y el conocimiento de estas
interfaces ya está pagado. Si mañana se decide no entrar, nada de eso se pierde.
