# RUNBOOK DE GRABACIÓN — CLEVERIA · v3

**Fecha:** 2026-08-30 · **Versión:** 7.0 · **Cierre:** 31-ago 17:00 hora del Pacífico
*(v7: el banner de la toma 4 **arreglado en el código** y vigilado por una prueba — ya se graba
entera; el identificador de sesión dura una hora; menos de diez minutos entre ensayo y toma;
y son dieciséis pruebas, la del ancla no entra)*
*(v6: la toma 3 dura 13 s y no hay espera; la toma 2 acaba en aviso amarillo; el banner de la 4
miente a medias; y se retiró el residuo que aún mandaba desconectar el cable)*
*(v5: NO desconectar la red en la toma 4, la ventana del reloj :01–:11, y el plazo del cofirmante)*
*(v4: la regla de edición corregida contra la rúbrica, OBS montado, la toma 3 paso a paso)*

> ### Este documento ha mentido cinco veces, y las cinco sonaban razonables
>
> Ninguna se cazó leyéndolo: **las cinco se cazaron ejecutándolo**. Y la quinta es la que mejor
> enseña por qué: la v5 declaraba corregida la instrucción de desconectar el cable **y la
> instrucción seguía viva ochenta líneas más abajo**, justo donde se lee al terminar la toma 3.
> Corregir el sitio donde uno recuerda haberlo escrito no es corregir el documento.
>
> Si vas con prisa, lee solo los recuadros marcados ⏰ y ⚠. **Cada uno evita una toma perdida.**

> **La v2 decía que había tres planes de grabación incompatibles. Ya no**, y por una razón mejor
> que la que teníamos.
>
> **Corregido el 2026-08-30, leyendo la rúbrica y no solo el reglamento.** La v3 decía que «no
> existe ninguna regla sobre cortes ni edición». Es falso, y era un error caro: el 30 % de la
> nota lo decide *Demo & Production Readiness*, cuyo primer criterio pregunta literalmente
> «*Does the video show an **unedited, live execution** of the agent?*».
>
> Las exigencias formales siguen siendo cuatro: **4 minutos como máximo**, **público** en YouTube
> o Vimeo (*unlisted* no vale), **en inglés o con subtítulos en inglés**, y que **se vea el
> backend corriendo en Google Cloud**. Pero encima de ellas está la rúbrica, y ahí «sin editar»
> puntúa.
>
> **La toma única deja de ser una manía nuestra y pasa a ser la respuesta al criterio que más
> pesa.** El envoltorio —apertura, títulos, arquitectura, cierre— sí usa escenas y fundidos sin
> ninguna culpa: la exigencia recae sobre **la demostración**, no sobre el vídeo entero. Qué se
> puede hacer con las esperas está en la **§5.1**, con la respuesta literal del organizador.
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


> ### 📍 QUÉ SE GRABA, CÓMO Y CON QUÉ — los tres únicos archivos que importan
>
> Llegaron a convivir seis documentos diciendo qué se graba, la mitad en «propuesto». Ya no:
>
> | | Archivo | Dónde |
> |---|---|---|
> | **QUÉ** se graba y qué se dice | `2026-08-31_ESCALETA_corregida_contra_lo_medido.md` | `cleveria-dominios`, en `docs/strategy/metodo/ganar-hackathon/` |
> | **CÓMO** se graba | **este runbook**, v7 | aquí |
> | Lo que **EJECUTA** la toma | `plan_toma.txt` + `dirigir_grabacion.py` | aquí |
>
> **`VIDEO_SCRIPT.en.md` YA NO ESTÁ EN ESTE REPOSITORIO**: era anterior a las mediciones del 30
> y 31 de agosto —cinco tomas de terminal, sin el portal ni el libro de autoridad— y se movió a
> `cleveria-dominios`, junto al resto de la producción del vídeo, para no dejarlo a la vista de
> quien juzga el producto. Los guiones `GUION_video_compuesto` y `GUION_v2` quedaron
> superados, cada uno con su puntero al vigente.

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
| `bash demo.sh 4` | ✅ **grabable entera** | dos mitades de distinta naturaleza, y **el banner ya lo dice** |
| `bash demo.sh 5` | ✅ | Cloud Run, Scheduler, el llavero y sus políticas |

> ### ✅ ARREGLADO EN EL CÓDIGO — el fotograma final de la toma 4 ya no miente. Puedes grabarla entera.
>
> **Decía**: `COMPLETE — verified with no network and no credentials`, justo después de cuatro
> llamadas HTTPS **autenticadas** a Model Armor. Cierto de la primera mitad —el verificador puro,
> que es la parte fuerte— y falso de la segunda.
>
> **Dice ahora**, y sale así en pantalla:
>
> ```
> SHOT 4 COMPLETE  ·  offline verifier: no network, no credentials
> vendor-filter comparison above: 4 authenticated HTTPS calls to Model Armor
> ```
>
> **Ya no hace falta cortar antes del banner.** Y el número de llamadas no está tecleado: se lee
> de la lista de casos del propio kill-test, así que el día que alguien añada un quinto caso el
> banner dirá cinco solo.
>
> **La causa raíz, porque explica por qué nadie lo vio en todo el día**: la toma 4 era
> *enteramente* offline cuando se escribió ese banner —el comentario del código todavía lo decía—
> y dejó de serlo cuando se le añadió la comparación con el filtro del proveedor. **Nada obligaba
> al banner a enterarse.** Una afirmación absoluta sobrevivió al cambio que la volvió falsa, que
> es el pecado exacto contra el que argumenta el proyecto entero, cometido en el fotograma que un
> jurado mira más tiempo que ningún otro.
>
> Lo vigila `agente/killtest_banner_honesto.py`: ninguna toma que salga a la red puede terminar
> afirmando que no la tocó. Corre sin red y sin credenciales, en un instante, y **se probó
> rompiéndolo a propósito** — tres mutantes, los tres en rojo.
>
> **Si no hay credenciales, la mitad de red no corre y el banner vuelve al absoluto** — que ahí
> sí es cierto, porque no hubo ninguna llamada. Comprobado ejecutando.

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
2. **Corre las dieciséis pruebas** y deja el resumen listo: `./pruebas_de_ruptura.sh`
   (**204 segundos**, medidos en la corrida 16/16 de las 17:28 de hoy — no 150).
   **Tres de las dieciséis llaman a la nube de verdad**: `co-signer`, `double-fence` y
   `write-gate`. Si no hay red, salen rojas y el resumen no sirve para grabar. El resumen avisa
   solo si la corrida tiene más de una hora — córrela justo antes, no por la mañana.

   > **SON DIECISÉIS, Y LA DEL ANCLA NO ENTRA. No la metas a última hora creyendo que ayuda.**
   > Existe una prueba diecisiete, `agente/killtest_ancla_truncada.py`, que cierra el
   > truncamiento del libro y pasa sus catorce casos. Se dejó **deliberadamente fuera** de
   > `pruebas_de_ruptura.sh`: el guion, este runbook y la presentación dicen «dieciséis pruebas,
   > 204 segundos», y meterla cambia el número que la cámara enseña el día de la entrega. Corre
   > sola, en una centésima de segundo, y ahí se queda hasta que el operador decida instalarla
   > **después** de entregar. Si te la encuentras y te parece que falta: no falta, se decidió.
3. **Siembra la cola**: `python3 sembrar_demo.py --borrar && python3 sembrar_demo.py`.
4. **Ensayo en frío de la toma 3**, que es la que no se puede repetir mal.
   **El identificador de sesión de la nube vive UNA HORA.** El ensayo del 30 de agosto arrancó
   con el identificador vencido y `demo.sh` se negó a correr la toma —hizo lo correcto—, pero si
   eso pasa con la cámara encendida, se pierde la toma. Renuévalo justo antes de grabar, no al
   empezar la sesión de trabajo.
5. **Modo no molestar**, sin notificaciones ni segundas ventanas.
6. **Fuente grande, contraste alto**, y **sin rutas de tu disco, usuarios ni clientes en pantalla**.

> ### ⏰ MENOS DE DIEZ MINUTOS entre el ensayo y la toma buena
>
> El servicio en la nube **no tiene instancias mínimas** (`minScale` vacío), así que el contenedor
> se apaga tras unos quince minutos sin tráfico. Si ensayas, te vas a por un café y vuelves, la
> toma buena paga el arranque en frío delante de la cámara — y la espera no se puede cortar sin
> romper el criterio de *toma sin editar*.
>
> **El ensayo es también el calentador.** Ensaya y graba seguido.
>
> Es el único punto de la fase cero de estrategia de grabación que no había aterrizado aquí
> (fuente: `2026-08-30_FASE0_estrategia_de_grabacion.md`, fila **b** de las siete fuentes de no
> determinismo). Inferido de la configuración, no cronometrado: el propio revisor declaró que el
> clasificador de permisos le bloqueó el intento de medirlo con credencial.

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

**La captura ya va por PipeWire, y no es un detalle.** Este equipo es Fedora con GNOME sobre
Wayland: la fuente de captura X11 habría dado **pantalla negra**. Al seleccionar la escena, GNOME
enseña un diálogo pidiendo permiso para compartir la pantalla — **hay que aprobarlo a mano**, y
por eso ninguna grabación de esta casa puede lanzarse desatendida. Apruébalo antes de empezar,
con la casilla de recordar marcada.

> **Plan B si OBS falla en Wayland**, ya medido en esta casa y documentado en
> `cleveria-dominios/tools/HERRAMIENTA_grabacion_pantalla.md`: **GPU Screen Recorder** es el único
> grabador que se ha probado que funciona aquí. El grabador nativo de GNOME produce un archivo de
> 48 bytes sin fotogramas, y `wf-recorder` no sirve en GNOME.
>
> ```bash
> flatpak run --command=gpu-screen-recorder com.dec05eba.gpu_screen_recorder \
>   -w portal -f 30 -o "$HOME/Videos/toma3.mp4"     # -w portal es obligatorio
> ```
> Se cierra con `kill -INT`, nunca con `kill -9`: el archivo se escribe al cerrar. Y mientras
> graba **el archivo pesa 0 bytes**, así que mirar su tamaño no dice si está funcionando —
> lo que lo dice es la línea `update fps: NN` en su salida.

---

## 4. El orden de grabación, que no es el del vídeo

Graba primero lo difícil, con la máquina fresca y tú también:

1. **La toma 3 completa, de una pasada.** El 403, la firma de la persona, el cierre verificado.
   Si sale, el resto es cuesta abajo. **El paso a paso está en la §4.1, aquí abajo.**
2. **La toma 4 — y NO desconectes la red.**

   > **Corregido el 2026-08-30. Aquí ponía «enséñala desconectando la red de verdad, es gratis y
   > es la prueba más fuerte». Era falso y habría matado la toma en directo.**
   >
   > La toma 4 ejecuta `agente/killtest_blindaje.py`, que **llama a Model Armor por HTTPS** —
   > `modelarmor.us-central1.rep.googleapis.com`, línea 31, medido entre 0,53 y 0,67 s por
   > llamada. Con el cable fuera, esa mitad de la toma muere en cámara y no hay segunda pasada.
   >
   > Y el gesto **no aportaba nada**: lo que demuestra que el verificador funciona sin red no es
   > el cable, es **el análisis de importaciones que la propia toma imprime** — ninguna es de
   > Google. Eso se ve igual con la red puesta, y el jurado puede repetirlo en su casa.
   >
   > Lo destapó una fase cero con herramientas, ejecutando; no leyendo.
3. **Las tomas 1, 2 y 5.**
4. **El portal**, con una nota de voz real.
5. **La narración al final**, sobre el metraje ya montado. Así el ritmo lo pone la imagen.

---

### 4.1 La toma 3, paso a paso

Es la única que no se puede repetir mal, así que va escrita entera.

> ### ⏱ Dura **13 segundos**, no 80. Y no hay espera del despertador.
>
> **Corregido el 2026-08-30 midiéndolo**: `time bash demo.sh 3` → `real 0m12,5s`, con la línea
> `✓ done in 0s`. Aquí ponía «entre 50 y 80 segundos, casi todo la espera del despertador, que es
> la prueba de que el trabajo se reanuda solo». **Esa espera no existe en este guion.**
>
> La razón está en el código: `/decidir` (`servicio/main.py:112`) escribe el sobre **en el mismo
> momento** en que la persona firma, y el sondeo de `demo.sh` espera exactamente eso. Se cumple
> antes de que el despertador haga nada. La escena del reloj, la narración «el trabajo se reanuda
> solo» y el aviso de «si el paso 6 agota los 90 segundos» describían **una toma que este guion no
> produce**.
>
> **Qué hacer con eso, y es una decisión, no un arreglo:**
> - **Grábala tal cual, en 13 segundos**, y narra lo que de verdad ocurre: la persona firma y el
>   cierre queda verificado. Es cierto, es rápido, y **sobra tiempo de vídeo** — que hoy es un
>   problema que teníamos al revés.
> - Si quieres la escena de la reanudación, hay que hacer que el sondeo espere algo que **sí**
>   dependa del despertador. Eso es tocar código a horas de grabar, y no lo recomiendo.

> ### ⏰ MIRA EL RELOJ ANTES DE SEMBRAR. La ventana buena es del minuto :01 al :11
>
> El despertador de la nube corre **cada quince minutos** y está `ENABLED` — comprobado:
> `*/15 * * * *`, último disparo a las 20:15:20 de hoy. En los minutos **:00, :15, :30 y :45**
> adjudica lo que haya sembrado **fuera de cámara**, y puede **cerrar `PET-002` entre tu siembra y
> el clímax de la toma 3**: llegarías al momento bueno con el caso ya cerrado por alguien que no
> se ve.
>
> No hay que tocar nada ni apagar nada. **Siembra y arranca entre el :01 y el :11**, y el
> despertador no se cruza.
>
> **Y NO SE TE OCURRA PAUSARLO.** Es la solución que parece obvia y **rompe la toma 3**: `demo.sh`
> lo dispara a mano dos veces durante esa toma, y con el trabajo pausado `gcloud scheduler jobs
> run` devuelve `FAILED_PRECONDITION: Job.state must be ENABLED`. Perderías la toma justo en el
> momento en que se demuestra que el trabajo se reanuda solo. La ventana del reloj no es una
> comodidad: es la única mitigación que no rompe nada.

**Antes de pulsar grabar** (fuera de cámara, en otra terminal):

```bash
date +%M                                        # entre 01 y 11, o espera
gcloud auth print-identity-token | head -c 20   # tiene que devolver algo
python3 sembrar_demo.py --borrar && python3 sembrar_demo.py
bash demo.sh 3                                  # ENSAYO EN FRÍO, entero
```

> ### ⚠ Si alguien te dijo que exportaras `COFIRMANTE_TIMEOUT`, **abre una terminal nueva**
>
> Durante unas horas este runbook mandó `export COFIRMANTE_TIMEOUT=12` antes de grabar, porque el
> cofirmante daba `allow=false reason=too_slow` a 5,2 s contra un plazo de 4 y **detenía el
> flujo**: la máquina no firmaba el caso que el README promete que firma.
>
> **Esa mitigación se retiró, y hay que retirarla también de tu terminal.** El defecto no era la
> lentitud del modelo: **el cronómetro arrancaba antes de conseguir la credencial**, así que le
> cobraba a la respuesta del cofirmante el descubrimiento de credencial, el saludo del token y el
> de la conexión cifrada. Arreglado en el mismo flujo: **5,20 s → 0,78 s**, y comprobado otra vez
> aquí a **0,97 s**. El plazo de 4 segundos se queda y sobra margen.
>
> **Por qué importa grabar sin la variable**: el reclamo y el README dicen cuatro segundos. Grabar
> con doce y publicar cuatro es justo la clase de desajuste que este vídeo existe para no tener. Y
> era el peor fallo posible en un control que falla cerrado — **el que se dispara por una razón
> que no es la suya**: no abría ninguna puerta, pero enseñaba a subir el plazo.

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
| 6 | **`✓ done in 0s`** — no hay espera; el sondeo se cumple al instante | **No narres una espera que no ocurre.** Di lo que se ve: «y el cierre ya está.» |
| 7 | `PET-002 closed → signer=HUMANO` | «Se cierra con la firma de la persona, no con la del programa.» |

**Lo que puede salir mal, y qué hacer:**

- **`PET-002` sigue cerrada de un ensayo anterior, y volver a sembrar NO la resetea.** Medido:
  `sembrar_demo.py` escribe `PET-006` en adelante, en otra colección, mientras las tomas 1, 2 y 3
  leen el fichero horneado con `PET-001..005`. Y `--borrar` **no toca el estado**, que es donde
  quedó la decisión humana del ensayo. El remedio real es **correr la toma 2**, que reinicia ese
  estado, o borrar el documento a mano.
- **El `403` no sale.** Compruébalo a demanda **antes** de apostar el vídeo a una sola toma:
  `curl -s -X POST -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$URL/intentar-suplantar"`.
  Si no es reproducible ahora, no lo será en cámara.
- **Sale un correo o una ruta del disco.** Corta y repite: `/decidir` ya devuelve solo el dominio,
  pero este dato ha reaparecido tres veces en sitios distintos.
- **La toma 2 se cuelga 90 segundos y acaba con un aviso amarillo en cámara.** Medido:
  `real 3m33s`, terminando en `⚠ still not ready after 90s`. No es un fallo del sistema — su
  sondeo exige veredicto en las cuatro peticiones, y dos de ellas **esperan a una persona y no lo
  tendrán nunca**. Si la grabas tal cual, ese aviso sale en el vídeo. **Grábala sabiéndolo**, o
  corta esa toma del guion: lo que demuestra ya lo demuestra la toma 3.

**Después de la toma 3, y en este orden**: la toma 4 **con la red puesta** —ver el aviso de la
§4—, luego 1, 2 y 5, luego el portal con una nota de voz, y la narración al final.

## 5. El montaje

- **Los primeros 10 segundos deciden si te siguen viendo.** Van directos a la cola trabajando.
  Sin logotipo antes, sin título antes.
- **NO cortes las esperas de la demostración.** Acelera el bloque entero, uniformemente, y
  rotúlalo. El porqué está en la §5.1, y es lo que separa una entrega puntuada de una descartada.
- **Subtítulos en inglés siempre**, aunque se narre en inglés: muchos jurados ven sin sonido.
- **Ningún panel de identidad de la nube con nombres propios.**

### 5.1 Qué se puede hacer con las esperas, y qué no

> **Corregido el 2026-08-30. Hasta hoy este runbook decía «corta toda espera, corte de salto y
> sigue». Eso está prohibido**, y el error habría costado el 30 % de la nota.

Las bases puntúan «*Does the video show an **unedited, live execution** of the agent performing
its task?*». Preguntado en el foro si se puede acelerar la grabación para no pasar de cuatro
minutos, el organizador contestó — respuesta de *Shawni Dev*, manager, aportada por el operador:

> «Una aceleración uniforme de una ejecución real (**sin cortes, empalmes, ni añadidos ni
> eliminados**) generalmente se interpreta como “sin editar”, pero **editar, recortar o unir
> clips en exceso no lo haría**. Para mayor seguridad, mantén la ejecución continua y **añade una
> nota en pantalla si la has acelerado**.»

| Con las esperas | ¿Permitido? | Qué hacer |
|---|---|---|
| Dejarlas a 1× | **Sí**, y es lo que hay que intentar primero | rótulo `rotulo_toma_unica.png` |
| **Acelerar el bloque entero, uniforme** | Sí, **pero como último recurso** | rótulo `rotulo_toma_unica_acelerado.png` |
| Corte de salto para saltarse el sondeo | **NO** | es un corte: rompe «unedited» |
| Unir dos intentos de la misma toma | **NO** | es un empalme |
| Acelerar solo la parte aburrida | **NO** | no es uniforme |

**El orden para no pasarse de cuatro minutos, y no es el que parece.** Un disidente de otro
linaje tumbó el plan anterior con un argumento que se acoge entero: *acelerar la espera destruye
justamente la prueba que esa espera aporta*. La espera existe para enseñar que el trabajo se
reanuda solo; comprimida, un jurado escéptico ya no distingue una espera real de un empalme. Y
la respuesta del organizador dice «**generalmente** se interpreta» — es una tolerancia, no una
garantía. Así que:

1. **Recorta el envoltorio.** Títulos, diagrama, cierre. Ahí sobra tiempo y editar está permitido.
2. **Recorta contenido de la demostración** —un paso menos, un objetivo más pequeño—, que sigue
   siendo honesto.
3. **Solo entonces, acelera**, y el bloque entero.

Si la demostración a velocidad real no cabe, **el problema es de guion, no de velocidad**.

**Cómo acelerar sin equivocarse** — un solo comando sobre el bloque entero, nunca sobre un trozo:

```bash
# libopenh264, NO libx264: en este equipo x264 no está instalado (ficha de grabación del repo).
ffmpeg -i toma3.mkv -filter:v "setpts=PTS/2" -filter:a "atempo=2.0" \
       -c:v libopenh264 -b:v 6000k toma3_2x.mp4
```

**Y compruébalo mirando fotogramas, no suponiendo.** La regla de la casa, escrita después de
entregar un vídeo de 152 segundos que resultó ser una imagen fija: un vídeo que demuestra que
algo *ocurre* se valida extrayendo fotogramas del principio y del final **y nombrando qué
cambió**. El peso del archivo no vale como veredicto.

```bash
ffmpeg -ss 2  -i toma3_2x.mp4 -frames:v 1 ini.png
ffmpeg -sseof -3 -i toma3_2x.mp4 -frames:v 1 fin.png   # y míralos
```

Y el rótulo tiene que decirlo. **Usar el rótulo de 1× sobre metraje acelerado sería afirmar algo
falso justo encima de la única parte del vídeo cuyo valor entero es que se puede creer.** Los dos
rótulos se regeneran con `python3 assets/slides/generar_rotulos.py <velocidad>`.

**Comprueba que los registros siguen leyéndose después de acelerar.** El criterio que se puntúa
nombra literalmente *terminal logs*: unos registros que pasan demasiado rápido para leerse dejan
de ser prueba de nada. Si a 2× no se leen, ese bloque no se acelera.

### 5.2 Mostrar, no proclamar

El rótulo **ya no dice «UNEDITED»**, y el cambio vino de un ataque que se acoge: era una
afirmación **absoluta** puesta sobre un vídeo cuyo envoltorio sí está editado. Un jurado
adversarial no lee el matiz «no cuts *inside this block*» — lee la palabra grande, ve un fundido
dos minutos después, y la defensa se vuelve una acusación contra uno mismo. Ahora dice
**`DEMO BLOCK — ONE CONTINUOUS TAKE`**, que delimita lo que promete.

Y como la honestidad se enseña mejor de lo que se declara, **que estas tres cosas estén en
pantalla durante la demostración**, que además son lo que la regla formal exige ver:

- **El identificador del proyecto y la región** de Google Cloud, en el símbolo del sistema o en
  la propia salida (`ai-transf-lab-0827`, `us-central1`).
- **Un reloj visible** —el de la barra del sistema basta— durante la espera. Es lo que convierte
  el paso del tiempo en algo comprobable en vez de en algo afirmado.
- **Los registros corriendo**, no una pantalla quieta.

Con eso, el rótulo pasa de ser la prueba a ser un rótulo, que es lo que debe ser.

**Repite también el aviso en la descripción del vídeo**, que es lo que el organizador pidió «para
mayor seguridad»: *“The demo block is a single continuous run, played back at a uniform 2×. No
cuts, no splices, nothing added or removed.”*

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
6. **Las dieciséis pruebas**, con la invitación a correrlas.
7. **El segundo rechazo, que es nuevo y no es el mismo que el `403` de la llave.**
   `POST /intentar-escribir-directo` devuelve `403 PERMISSION_DENIED` sobre el **almacén**: el
   agente perdió la escritura y solo `sa-mediador` la tiene. Aquel `403` era sobre una llave;
   este es sobre donde las cosas pasan de verdad. **Y hay segundos para él sin quitarle nada a
   nadie**, porque la toma 3 dura 13 y no 80.
7. **La cofirma en pantalla, y esto lo pidió el organizador por escrito**: una línea por cierre
   con el nombre del modelo — `model=google/gemma-4-26b-a4b-it-maas channel=vertex allow=false
   reason=missing_human_key`. Sale sola al correr `python3 agente/grafo.py`, y también con
   `tail -3 libro/cofirmas.jsonl`. **Sin ese plano no hay bonificación por el modelo adicional**:
   pidió ver la integración, no creerla.

**El argumento que las une, y vale más que las seis por separado**: cada una existe para que
**ninguna parte del sistema pueda ampliarse a sí misma la autoridad**. Eso es lo que se narra
mientras se enseña — no la lista de servicios.

---

## 8. Comprobación final antes de subir

- [ ] **Antes de grabar**: reloj entre :01 y :11, la red **puesta**, y **sin** `COFIRMANTE_TIMEOUT` exportado
- [ ] **Se ve la cofirma en pantalla** — la línea `model=google/gemma-4-26b-a4b-it-maas
      channel=vertex allow=… reason=…`. El organizador pidió ver la integración, no creerla
- [ ] Dura 4:00 o menos
- [ ] Está en inglés o lleva subtítulos en inglés
- [ ] Se ve el backend corriendo en Google Cloud
- [ ] No aparece ningún correo, ruta personal ni nombre de cliente
- [ ] El rótulo está sobre la demostración, **y es el que corresponde a la velocidad usada**
- [ ] **Dentro de la demostración no hay ni un corte ni un empalme** (§5.1)
- [ ] Si se aceleró: el aviso está en pantalla **y** en la descripción del vídeo
- [ ] **Público** en YouTube o Vimeo — *unlisted* no cuenta y descarta la bonificación
- [ ] La descripción explica la fricción y nombra la arquitectura
