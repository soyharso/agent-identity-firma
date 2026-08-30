# RUNBOOK DE GRABACIÓN — CLEVERIA · v3

**Fecha:** 2026-08-30 · **Versión:** 3.0 · **Cierre:** 31-ago 17:00 hora del Pacífico

> **La v2 decía que había tres planes de grabación incompatibles. Ya no**, y por una razón mejor
> que la que teníamos.
>
> **Leído el 2026-08-30 en la página oficial de novedades: no existe ninguna regla sobre toma
> única, cortes ni edición.** Las únicas exigencias del vídeo son cuatro minutos como máximo,
> público en YouTube o Vimeo, en inglés, y que se vea el backend corriendo en Google Cloud.
> **La toma única era una restricción que nos pusimos solos.**
>
> Se mantiene igualmente para la demostración, pero ya no como obligación: como **argumento**. Y
> el resto del vídeo usa escenas, fundidos, títulos e imágenes sin ninguna culpa.
>
> ### Y un aviso de los organizadores que cambia las prioridades
>
> > *«Judges aren't required to download or run your project. They may score entirely from your
> > video, your text description, and your repo.»*
>
> **Los jueces pueden puntuar sin ejecutar nada.** Tres consecuencias:
>
> 1. **El rótulo de toma única vale más de lo que parece.** Si no van a correr el proyecto, lo
>    único que separa una demostración real de una recreación es lo que se ve y lo que se afirma.
> 2. **La descripción escrita pesa tanto como el vídeo.** No es un trámite.
> 3. **«Corre las pruebas tú mismo» es un adorno**, no una prueba. Sigue estando bien decirlo —
>    pero no cuentes con que alguien lo haga: **lo que no se vea en el vídeo, no existe**.
>
> Súbelo con horas de margen: los organizadores avisan de que YouTube y Vimeo tardan «desde unos
> minutos hasta varias horas» en procesar.

---

## 0. Las dos capas

| Capa | Qué es | Cómo se graba |
|---|---|---|
| **Envoltorio** | apertura, títulos, arquitectura, cierre | escenas de OBS, fundidos, imágenes |
| **Demostración** | el agente trabajando, el 403, el verificador | **una toma corrida por bloque, sin cortes dentro** |

Sobre la demostración va un rótulo discreto: `unedited — single take`. Un jurado que ve ese
rótulo justo sobre la parte que importa **confía más en todo lo demás**, no menos.

---

## 1. Lo que ya funciona, comprobado el 2026-08-30

Con la sesión de Google Cloud abierta, las cinco tomas corren:

| Toma | Estado | Qué prueba |
|---|---|---|
| `bash demo.sh 1` | ✅ | la cola, con las peticiones que exigen persona marcadas |
| `bash demo.sh 2` | ✅ | el despertador dispara y la flota dictamina en la nube |
| `bash demo.sh 3` | ✅ **el corazón** | **403 real de Cloud KMS**, con el recurso completo |
| `bash demo.sh 4` | ✅ **sin credenciales** | el verificador sin red y las pruebas de ruptura |
| `bash demo.sh 5` | ✅ | Cloud Run, Scheduler, el llavero y sus políticas |

**La toma 3 es el vídeo entero.** Esta línea no la puede imprimir un `print()`:

```
"error": "PERMISSION_DENIED",
"message": "Permission 'cloudkms.cryptoKeyVersions.useToSign' denied on resource
            'projects/…/keyRings/firmas/cryptoKeys/clave-humano'"
```

Trae el recurso con nombre y apellido, y lo devuelve Google, no nosotros.

> ### ✅ El correo del operador ya no sale en cámara
> Hasta el 2026-08-30, `/decidir` devolvía el correo completo en el campo `by`, y esa respuesta
> se ve en la toma 3 de un vídeo público. Ahora devuelve solo el dominio: lo que importa ahí no
> es *quién* es la persona, sino que **fue una persona y el servicio pudo comprobarlo**. La
> identidad completa sigue dentro del sobre firmado, que es donde debe estar para auditar.
>
> **Compruébalo igualmente antes de grabar** — corre la toma 3 y mira la salida. Este dato ha
> reaparecido tres veces en sitios distintos.

---

## 2. Antes de encender la cámara

1. **Sesión de nube abierta** — `gcloud auth print-identity-token | head -c 20` debe devolver algo.
2. **Corre las once pruebas** y deja el resumen listo: `./pruebas_de_ruptura.sh` (unos 2½ minutos).
3. **Siembra la cola**: `python3 sembrar_demo.py --borrar && python3 sembrar_demo.py`.
4. **Ensayo en frío de la toma 3**, que es la que no se puede repetir mal.
5. **Modo no molestar**, sin notificaciones ni segundas ventanas.
6. **Fuente grande, contraste alto**, y **sin rutas de tu disco, usuarios ni clientes en pantalla**.

---

## 3. OBS — ya instalado y con las siete escenas montadas

> **Hecho el 2026-08-30.** OBS Studio no estaba en esta máquina: se instaló (`flatpak --user`,
> versión 32.2.2) y se dejó **una colección de escenas ya armada**, con las cinco piezas de
> `assets/slides/` colocadas en su sitio. No hay que crear ninguna fuente a mano.

**Para usarla**: abre OBS → menú **Colección de escenas** → **Cleveria_Hackathon**.

| # | Escena | Qué lleva dentro | Se usa en |
|---|---|---|---|
| 1 | **Portada** | `portada.png` a pantalla completa | 0–3 s y antes del cierre |
| 2 | **Portal del cliente** | pantalla + marca de agua | la entrada del caso y la voz |
| 3 | **Demostración — toma única** | pantalla + **rótulo `unedited — single take`** + marca de agua | **toda la demostración** |
| 4 | **Libro de autoridad** | pantalla + marca de agua | la auditoría |
| 5 | **Consola de Google Cloud** | pantalla + marca de agua | junto al 403 |
| 6 | **Arquitectura** | pantalla + marca de agua | el bloque de arquitectura |
| 7 | **Cierre** | `cierre.png` a pantalla completa | los últimos 20 s |

El rótulo va arriba a la izquierda y la marca de agua abajo a la derecha, al 50 % de opacidad, ya
posicionados para 1920×1080. Las escenas 2 a 6 comparten **la misma fuente de pantalla**: se
cambia de escena, no de captura, y por eso el salto es instantáneo.

**Lo único que queda por hacer a mano, y son dos minutos:**

1. **Ajustes → Salida → Grabación**: formato `mkv`, codificador por hardware si aparece, calidad
   *Indistinguible*. El `mkv` no se corrompe si la máquina se cae a mitad de grabación; un `mp4`
   sí. Se convierte a `mp4` al final con **Archivo → Remuxar grabaciones**.
2. **Ajustes → Vídeo**: base y salida en **1920×1080**, a **30 fps**. Más resolución no suma y
   pesa; más fotogramas tampoco, porque aquí no hay movimiento rápido.
3. **Ajustes → Atajos**: asigna una tecla a *Iniciar grabación* y otra a cada escena. Cambiar de
   escena con el ratón se ve en el vídeo.

Fundido de 0,4 s entre escenas —ya configurado—. **Corte seco dentro de la demostración, nunca
fundido**: un fundido en medio de una prueba es exactamente lo que hace dudar de si se cortó algo.

> Si la captura de pantalla sale en negro, es que la sesión es Wayland y no X11. Cambia la fuente
> «Pantalla» por **Captura de pantalla (PipeWire)** y concede el permiso que pide el sistema.

---

## 4. El orden de grabación, que no es el del vídeo

Graba primero lo difícil, con la máquina fresca y tú también:

1. **La toma 3 completa, de una pasada.** El 403, la firma de la persona, el cierre verificado.
   Si sale, el resto es cuesta abajo. **El paso a paso está en la §4.1, aquí abajo.**
2. **La toma 4**, y enséñala **desconectando la red de verdad**. Es gratis y es la prueba más
   fuerte, porque el jurado puede repetirla en su casa.
3. **Las tomas 1, 2 y 5.**
4. **El portal**, con una nota de voz real.
5. **La narración al final**, sobre el metraje ya montado. Así el ritmo lo pone la imagen.

---

### 4.1 La toma 3, paso a paso

Es la única que no se puede repetir mal, así que va escrita entera. Dura entre **50 y 80
segundos** de reloj: casi todo es la espera del despertador, que **no se corta** — es la prueba de
que el trabajo se reanuda solo.

**Antes de pulsar grabar** (fuera de cámara, en otra terminal):

```bash
gcloud auth print-identity-token | head -c 20   # tiene que devolver algo
python3 sembrar_demo.py --borrar && python3 sembrar_demo.py
bash demo.sh 3                                  # ENSAYO EN FRÍO, entero
```

> **Si el token está vacío, no grabes.** Sin sesión de nube, el guion imprime una respuesta de
> ejemplo con el rótulo `CANNED SAMPLE — DO NOT RECORD`. Grabarlo sería enseñar como prueba algo
> que no ocurrió, y es justo lo contrario de lo que el vídeo defiende. Vuelve a sembrar antes de
> la toma buena: el ensayo deja `PET-002` ya cerrada.

**En cámara** — escena 3 de OBS, terminal a pantalla completa, y una sola orden:

```bash
bash demo.sh 3
```

| Momento | Qué aparece | Qué se narra |
|---|---|---|
| 1 | El rótulo del bloque: *the cloud boundary — IAM & Cloud KMS* | «Un mismo servicio, dos llaves.» |
| 2 | **`200` con su propia clave** | «Con la suya, firma.» |
| 3 | **`403 PERMISSION_DENIED`** sobre `clave-humano`, con el recurso completo | **Aquí se para de hablar.** Deja el 403 en pantalla dos segundos enteros. Es el plano del vídeo. |
| 4 | La persona firma desde su máquina: `decidir_como_persona.py PET-002 descartada` | «La autorización la firma una persona, con una llave que el programa no puede pedir.» |
| 5 | El despertador se dispara (`scheduler jobs run despertar-candado`) | «Nadie vuelve a tocar nada.» |
| 6 | La espera, hasta 90 s, sondeando | **No la cortes.** «El trabajo se reanuda solo.» |
| 7 | `PET-002 closed → signer=HUMANO` | «Y se cierra con la firma de la persona, no con la del programa.» |

**Lo que puede salir mal, y qué hacer:**

- **El paso 6 agota los 90 segundos.** El despertador corre cada quince minutos; si acaba de
  pasar, la reanudación tarda. Repite la toma, no la edites.
- **Sale un correo o una ruta del disco.** Corta y repite: `/decidir` ya devuelve solo el dominio,
  pero este dato ha reaparecido tres veces en sitios distintos.
- **`PET-002` ya estaba cerrada** (por el ensayo). Vuelve a sembrar.

**Después de la toma 3, y en este orden**: la toma 4 desconectando la red de verdad, luego 1, 2 y
5, luego el portal con una nota de voz, y la narración al final.

## 5. El montaje

- **Los primeros 10 segundos deciden si te siguen viendo.** Van directos a la cola trabajando.
  Sin logotipo antes, sin título antes.
- **Corta toda espera.** Donde el sondeo tarde, corte de salto y sigue.
- **Subtítulos en inglés siempre**, aunque se narre en inglés: muchos jurados ven sin sonido.
- **Ningún panel de identidad de la nube con nombres propios.**

---

## 6. Piezas visuales — ya preparadas

Todas en `assets/slides/`, listas para arrastrar a OBS:

| Pieza | Archivo | Cómo se usa |
|---|---|---|
| **Portada** | `portada.png` (1920×1080) | escena 1, primeros 3 s y antes del cierre |
| **Cierre** | `cierre.png` (1920×1080) | escena 7, la tesis en los últimos 20 s |
| **Rótulo de toma única** | `rotulo_toma_unica.png` (640×100, con transparencia) | **superpuesto durante toda la demostración**, esquina superior izquierda |
| **Marca de agua** | `marca_agua.png` (260×108, al 50 %) | esquina inferior derecha, todo el vídeo |
| **Diagrama que se construye** | `ARCHITECTURE_animado.svg` | fuente de navegador; al recargar, las cuatro capas aparecen en cascada de 0,8 s |

El diagrama animado **no toca el original**: es el mismo `ARCHITECTURE.svg` con una hoja de
estilo que escalona la aparición de sus grupos. El que ve el jurado en el repositorio sigue
siendo el estático.

**Lo que NO conviene**: imágenes generadas de relleno. En un vídeo cuya tesis es que la evidencia
se prueba, una ilustración decorativa resta.

---

## 7. La nota de arquitectura: qué enseñar para ganarla

Es el 30 %, y se gana enseñando **decisiones**, no cajas:

1. **Las tres identidades y sus alcances**, leídos de `claves/directorio.json` — que se vea que el
   alcance es un dato auditable y no una condición escrita en un `if`.
2. **El 403 con el recurso completo**, que es lo que ya sale hoy.
3. **Los `import` del verificador** en pantalla: ninguno es de Google.
4. **El despertador con identidad propia**: `sa-temporizador` llamando por OIDC a `/despertar`
   cada quince minutos. **Dos cuentas de servicio para dos papeles** es justo lo que se premia.
5. **El diagrama**, ya en la rama que ve el jurado.
6. **Las once pruebas**, con la invitación a correrlas.

**El argumento que las une, y vale más que las seis por separado**: cada una existe para que
**ninguna parte del sistema pueda ampliarse a sí misma la autoridad**. Eso es lo que se narra
mientras se enseña — no la lista de servicios.

---

## 8. Comprobación final antes de subir

- [ ] Dura 4:00 o menos
- [ ] Está en inglés o lleva subtítulos en inglés
- [ ] Se ve el backend corriendo en Google Cloud
- [ ] No aparece ningún correo, ruta personal ni nombre de cliente
- [ ] El rótulo `unedited — single take` está sobre la demostración
- [ ] Público en YouTube o Vimeo
