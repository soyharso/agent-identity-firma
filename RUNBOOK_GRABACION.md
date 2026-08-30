# RUNBOOK DE GRABACIÓN — CLEVERIA · v3

**Fecha:** 2026-08-30 · **Versión:** 3.0 · **Cierre:** 31-ago 17:00 hora del Pacífico

> **La v2 decía que había tres planes de grabación incompatibles. Ya no.** El operador revisó las
> bases el 2026-08-30 y la lectura resuelve el conflicto: **la toma única vale para la
> DEMOSTRACIÓN del funcionamiento** —ahí no puede haber edición que cambie lo que pasó— **y el
> resto del vídeo admite escenas, fundidos, títulos e imágenes**. Los cortes de tiempo están
> permitidos en todas partes.
>
> Los planes no competían: uno es el envoltorio y el otro es el corazón. Se usan los dos.

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

> ### ⚠ Antes de grabar la toma 3
> En esa misma salida aparece **el correo del operador** (`"by": "gerencia@softronica.com.co"`).
> Sale de `decidir_como_persona.py`. **Quítalo o recorta el encuadre**: el vídeo es público.

---

## 2. Antes de encender la cámara

1. **Sesión de nube abierta** — `gcloud auth print-identity-token | head -c 20` debe devolver algo.
2. **Corre las once pruebas** y deja el resumen listo: `./pruebas_de_ruptura.sh` (unos 2½ minutos).
3. **Siembra la cola**: `python3 sembrar_demo.py --borrar && python3 sembrar_demo.py`.
4. **Ensayo en frío de la toma 3**, que es la que no se puede repetir mal.
5. **Modo no molestar**, sin notificaciones ni segundas ventanas.
6. **Fuente grande, contraste alto**, y **sin rutas de tu disco, usuarios ni clientes en pantalla**.

---

## 3. Escenas de OBS

| # | Escena | Fuente | Se usa en |
|---|---|---|---|
| 1 | **Portada** | logotipo de Cleveria sobre Obsidian Navy `#06111F` | 0–3 s y cierre |
| 2 | **Portal del cliente** | navegador en `…/ui/portal` | la entrada del caso y la voz |
| 3 | **Terminal** | terminal a pantalla completa | **toda la demostración** |
| 4 | **Libro de autoridad** | navegador en `…/ui/unified` | la auditoría |
| 5 | **Consola de Google Cloud** | el llavero de Cloud KMS | junto al 403 |
| 6 | **Arquitectura** | `ARCHITECTURE.svg` a pantalla completa | el bloque de arquitectura |
| 7 | **Cierre** | fondo liso con la tesis | los últimos 20 s |

Fundido de 0,4 s entre escenas. **Corte seco dentro de la demostración, nunca fundido**: un
fundido en medio de una prueba es exactamente lo que hace dudar de si se cortó algo.

---

## 4. El orden de grabación, que no es el del vídeo

Graba primero lo difícil, con la máquina fresca y tú también:

1. **La toma 3 completa, de una pasada.** El 403, la firma de la persona, el cierre verificado.
   Si sale, el resto es cuesta abajo.
2. **La toma 4**, y enséñala **desconectando la red de verdad**. Es gratis y es la prueba más
   fuerte, porque el jurado puede repetirla en su casa.
3. **Las tomas 1, 2 y 5.**
4. **El portal**, con una nota de voz real.
5. **La narración al final**, sobre el metraje ya montado. Así el ritmo lo pone la imagen.

---

## 5. El montaje

- **Los primeros 10 segundos deciden si te siguen viendo.** Van directos a la cola trabajando.
  Sin logotipo antes, sin título antes.
- **Corta toda espera.** Donde el sondeo tarde, corte de salto y sigue.
- **Subtítulos en inglés siempre**, aunque se narre en inglés: muchos jurados ven sin sonido.
- **Ningún panel de identidad de la nube con nombres propios.**

---

## 6. Piezas visuales que faltan

| Pieza | Para qué | Coste |
|---|---|---|
| Tarjeta de portada | 3 s de identidad al abrir y cerrar | el logotipo existe; falta componerla |
| Rótulo `unedited — single take` | que el jurado sepa qué está viendo | un texto en OBS |
| Diagrama por capas | que la arquitectura se construya en pantalla | `ARCHITECTURE.svg` ya existe; se revela por grupos |
| Tarjeta de las tres identidades | las tres claves y su alcance, lado a lado | media hora |
| Marca de agua discreta | Cleveria abajo a la derecha | inmediato |

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
