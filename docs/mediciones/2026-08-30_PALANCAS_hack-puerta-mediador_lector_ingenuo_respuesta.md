---
ambito: >
  la revision del lector ingenuo sobre el informe del frente hack-puerta-mediador: que no se entendia leyendolo solo, sin acceso al codigo.
entrega: >
  la respuesta literal del lector, y la tabla de que se corrigio y que no, con la razon de cada cosa.
---

# Lector ingenuo — respuesta cruda

**Frente**: hack-puerta-mediador · **Fecha**: 2026-08-30 · **Titular del papel**: `claude-haiku`
(subagente barato, sin contexto del proyecto, sin acceso al código).

**Qué se le dio a leer**, y nada más: `docs/mediciones/2026-08-30_CIERRE_hack-puerta-mediador.md` y el borrador del texto de
cierre al operador. Instrucción explícita de NO abrir el repositorio: «si un texto solo se
entiende abriendo el código, eso es exactamente el defecto que tienes que reportar».

C1 — se buscó antes de crear este archivo, por nombre (`*abrir*`, `*acces*`, `*barat*`,
`*ingenuo*`, `*medic*`, `*clari*`, `*lint*`, `*lector*`) y por contenido («lector ingenuo»,
«subagente barato», «sin contexto», `INFLESZ`). Lo único que apareció fue
`docs/mediciones/2026-08-30_CIERRE_hack-puerta-mediador.md`, que cita el veredicto **en prosa**, y `web/app_web.py`, que usa
«sin contexto» hablando de otra cosa. La prosa dejó de contar como rastro el 2026-08-25, así que
este archivo no duplica al informe: es la evidencia material que al informe le falta.

---

## Respuesta literal del lector

### Qué entendí

Se construyó una puerta de control de escritura para que un agente no pueda escribir cambios en
una base de datos sin un documento firmado válido. La prueba muestra que antes la nube permitía
la escritura (HTTP 200), ahora la rechaza (HTTP 403). Se separaron dos servicios por identidad:
uno que solo lee, otro que verifica la firma y escribe.

### Lo que NO se entiende

1. **«sobre»** — aparece como «sobre válido», «sobre firmado», «sobre de la máquina», pero nunca
   se explica qué es este objeto. ¿Qué datos contiene? ¿Estructura?
2. **«peticion_id» y los códigos como `PET-002`, `PET-VECINO`** — no están glosados. ¿Qué
   representa cada uno? ¿De dónde salen?
3. **«el despertar»** — se menciona que «el despertar antes de llamar al modelo» pone
   `reserva_hash`, pero ¿qué es «el despertar»? ¿Quién? ¿Por qué esa palabra?
4. **`reserva_hash` vs `reservar_cierre()`** — se describe el problema (la primera ya está
   puesta), pero no se explica qué contenía originalmente ni por qué existe.
5. **`candado-firma` y `mediador-cierre` como servicios** — ¿cuál inicia la comunicación? ¿Usan
   HTTP entre ellos? ¿Comparten base de datos o van a través de una API?
6. **Códigos de rechazo (`CONTEXTO_AJENO`, `FUERA_DE_ALCANCE`, `FIRMANTE_DESCONOCIDO`)** — dónde
   se generan, quién los retorna, cómo el cliente los interpreta.
7. **`COLECCION_PETICIONES=peticiones_puerta`** — se dice que mitiga interferencias, pero ¿cómo
   funciona? ¿Es una tabla paralela?
8. **«El mismo sobre, dos veces» (A6)** — se dice «1ª escribió=True 2ª=False». ¿Es lo esperado o
   un defecto que se acepta?
9. **«Cloud Scheduler cada 15 minutos»** — ¿por qué escribía el mismo documento? ¿Qué trabajo es?

### Lo que parece contradictorio o dudoso

1. «Antes el agente tenía `roles/datastore.user`» pero luego se describe un estado «antes» donde
   escribía. Si de verdad lo tenía, ¿por qué dice al final que hay que readquirirlo? ¿O nunca lo
   había tenido?
2. «Solo entonces: `roles/datastore.viewer` primero —para no dejar al agente ciego— y
   `roles/datastore.user` fuera después.» Suena invertido: si le quitan `user` primero, queda sin
   poder escribir. ¿Se refiere al orden de la nube propagando, no al orden del comando?
3. «El banco solo creció»: crecimiento de ¿qué? ¿Pruebas nuevas? ¿Cobertura? No se aclara.

### Las tres frases que más costaría leer en voz alta

1. «El verificador ya sabía hacerla —`peticion_esperada` existe desde antes y su propio
   comentario dice que la pone quien verifica, nunca el sobre—; lo que faltaba era llamarla.»
2. «Regla de conflicto acordada con ese frente y confirmada por él palabra por palabra: se queda
   el cuerpo de `registrar()` de este frente, y dentro, la escritura del libro en disco es
   `libro_cadena.anexar(FIRMAS, fila)` —sin `FIRMAS.parent.mkdir(...)`—; la aplica quien fusione
   segundo.»
3. «IAM —el sistema de permisos de Google Cloud— tarda en propagar: medido (M3), entre 60 y 80
   segundos desde que el comando vuelve hasta que el servicio nota el cambio.»

---

## Disposición: qué se hizo con cada hallazgo

| # | Hallazgo | Disposición |
|---|---|---|
| NO-1 | «sobre» sin definir | **CORREGIDO** — sección nueva «Qué es un sobre, en una frase», al principio del informe |
| NO-3 | «el despertar» sin explicar | **CORREGIDO** — se glosa en la misma frase: la pasada que arranca cuando el temporizador llama a `/despertar` |
| DUDOSO-2 | el orden de la permuta de permisos se lee invertido | **CORREGIDO** — se reescribió diciendo cuál se **concede** y cuál se **quita**, y por qué en ese orden |
| DUDOSO-3 | «el banco solo creció» | **CORREGIDO** — ahora dice «eran doce y ahora son trece» |
| NO-2, NO-6 | `PET-002` y los códigos de rechazo | **NO SE CORRIGE** — vocabulario del propio sistema; quien lee el informe lo usa a diario, y glosarlo aquí duplicaría el directorio de claves y el verificador, que es donde vive |
| NO-4 | `reserva_hash` frente a `reservar_cierre()` | **PARCIAL** — se explica para qué sirve la primera (candado del despertar, para no gastar el modelo dos veces); no se documenta su historia entera, que es de `src/estado.py` |
| NO-5 | cómo se hablan los dos servicios | **NO SE CORRIGE** — está en `src/estado.py` y en `servicio/mediador.py`, con su comentario. El informe no es la documentación de la arquitectura |
| NO-7 | cómo funciona `COLECCION_PETICIONES` | **NO SE CORRIGE** — el informe dice qué hace y con qué comando. El cómo es una línea de `src/estado.py` |
| NO-8 | si A6 «1ª=True 2ª=False» es lo esperado | **NO SE CORRIGE** — el informe ya lo dice dos párrafos antes: «el primer sobre escribe, el segundo no reescribe la firma y el registro no cambia». Es un hallazgo de lectura, no de texto |
| NO-9 | por qué el temporizador escribe ese documento | **NO SE CORRIGE** — es el ciclo normal del producto, descrito en el README del proyecto |
| DUDOSO-1 | «¿nunca lo había tenido?» | **NO ES CONTRADICCIÓN** — el informe mide los dos estados y da el comando para revertir. Se dejó como está |
| VOZ-1, 2, 3 | tres frases difíciles de leer en voz alta | **UNA CORREGIDA** (la 2 se partió en tres oraciones). La 3 se dejó: lo que la alarga es la glosa de IAM, que hace falta. La 1 se dejó: el inciso es la cita del propio código |
