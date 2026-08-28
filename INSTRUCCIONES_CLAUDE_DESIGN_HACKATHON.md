# Manual integral de Claude Design para la entrega de Cleveria.ai

## Propósito

Usar Claude Design como director creativo, editor técnico y control de calidad para todos los
materiales del **All Things Agentic Hackathon** sin inventar capacidades ni convertir el proyecto
en una pieza publicitaria.

La narrativa única de toda la entrega es:

> **The agent can work. It cannot sign as a person.**

La misma afirmación, los mismos números y los mismos nombres de servicios deben aparecer de forma
consistente en vídeo, artículo, README, Devpost, diagrama, demo y publicaciones.

## Regla de fuentes de verdad

Adjuntar al proyecto de Claude Design:

- `README.en.md`
- `ARTICULO.en.md`
- `ENTREGA.md`
- `VIDEO_SCRIPT.en.md`
- `PRESENTACION_JURADO.en.md`
- `STORYBOARD_JURADO.en.md`
- `BRAND_CLEVERIA.en.md`
- `INSTRUCCIONES_CLAUDE_DESIGN_CLEVERIA.md`
- `src/`, `agente/`, `servicio/` y los resultados de los kill-tests
- capturas sanitizadas de Cloud Run, Cloud KMS, Firestore y el verificador

Claude no debe tratar un texto antiguo como autoridad si contradice los scripts o resultados
medidos más recientes. La versión vigente debe marcarse explícitamente como fuente de verdad.

## Arquitectura de marca

- **Cleveria.ai**: producto técnico y marca protagonista.
- **QNOWA**: escenario operativo/caso de uso; nunca fingir que el canal está integrado si no lo
  está.
- **Softronica.co**: operador, propietario y disclosure final.

No usar las tres marcas en el título, apertura del vídeo ni hero principal. Mostrar QNOWA solo
cuando explique el contexto real de las 58 filas. Mostrar Softronica en créditos, descripción
legal y página del operador.

## Prompt maestro

```text
Actúa como director/a creativo/a, editor/a técnico/a y productor/a senior de una entrega de
hackathon para jueces expertos en sistemas agénticos.

Debes convertir la evidencia adjunta en un paquete coherente para Cleveria.ai. Cleveria es un
harness de identidad y autoridad para agentes autónomos. Su tesis es:
"The agent can work. It cannot sign as a person."

La categoría objetivo es Fortified Enterprise Fleet. El material debe demostrar utilidad
operativa, arquitectura disciplinada, ejecución en Google Cloud y preparación de producción sin
afirmar que los agentes están en producción. La medición de 58 atribuciones humanas incorrectas y
4 dismissals ocurrió en preproducción y debe conservar esa precisión.

Usa primero evidencia: IAM/KMS, Cloud Run, Firestore, Cloud Scheduler, el error 403, firmas,
verificador offline y kill-tests. La tesis se dice después de establecer el hecho o en la misma
secuencia causal, nunca como un eslogan vacío.

No inventes clientes, certificaciones, usuarios, integraciones, métricas, premios, disponibilidad
en producción ni garantías que no estén en los archivos. Separa siempre GUARANTEED de MITIGATED.
Declara lo que no está construido: Agent Gateway, memoria de largo plazo y la integración completa
de WhatsApp con este lock.

Evita robots, cerebros, escudos, candados genéricos, neón, glitches, stock photography, música
dramática, frases de venta y promesas de autonomía total. La identidad visual debe usar el sistema
Cleveria adjunto.

Para cada propuesta entrega: objetivo, audiencia, mensaje, evidencia utilizada, texto final,
riesgos de interpretación y checklist de aceptación. No produzcas variantes decorativas sin
explicar la decisión.
```

## Flujo obligatorio en Claude Design

### Paso 1 — Auditoría de elegibilidad

```text
Audita la entrega contra las reglas adjuntas del hackathon.

Clasifica cada requisito como PASS, NEEDS EVIDENCE, BLOCKED o UNKNOWN:
- Gemini 3.5 o superior;
- Google Agent Framework;
- Google Cloud infrastructure;
- categoría única;
- proyecto nuevo durante el periodo;
- repositorio accesible;
- URL hospedada o instrucciones de prueba;
- README reproducible;
- diagrama de arquitectura;
- vídeo en inglés o con subtítulos;
- backend visible en Google Cloud;
- vídeo máximo de cuatro minutos;
- disclosure de software/código previo;
- propiedad intelectual y licencias;
- ausencia de credenciales o PII.

Devuelve una matriz con archivo, línea o captura que prueba cada requisito. No marques PASS por
inferencia.
```

### Paso 2 — Mensaje y posicionamiento

```text
Compara tres posicionamientos:
1. seguridad/agentes no pueden usurpar autoridad humana;
2. automatización de flujos empresariales;
3. multimodalidad por voz.

Puntúalos para Innovation & Operational Utility, Architectural Discipline & Tech Stack y Demo &
Production Readiness. Usa solo evidencia existente. Recomienda uno principal y dos secundarios.
No cambies de categoría ni conviertas el producto en un chatbot.
```

Decisión recomendada: posición principal **frontera criptográfica de autoridad**, utilidad
secundaria **cierre de trabajo basado en evidencia**, diferenciador secundario **voz sin cambio
de autoridad**.

## Vídeo de demostración

### Prompt de producción

```text
Escribe el paquete final de un vídeo de máximo 3:50, en inglés, con subtítulos en inglés y una
sola toma corrida de evidencia técnica.

Estructura:
0:00–0:12: 58 machine-attributed closures, 4 dismissed, PREPRODUCTION.
0:12–0:38: Cleveria.ai y la frontera que se va a probar.
0:38–1:18: scheduler, Firestore y tres resultados: machine-signed, human-required, unsigned.
1:18–2:08: intento real contra la clave humana y HTTP 403 de Cloud KMS.
2:08–2:42: firma humana en su máquina y verificador independiente offline.
2:42–3:24: kill-tests, Model Armor y limitaciones honestas.
3:24–3:48: Cloud Run/KMS/Firestore claramente visibles.
3:48–3:50: tesis y disclosure.

Para cada plano entrega timecode, captura, texto hablado, texto en pantalla, subtítulo, nivel de
audio y riesgo de privacidad. El primer frame debe ser evidencia, no un logo animado.
```

### Apertura aprobada

> “Fifty-eight records said human although a machine had closed them. Four were dismissals. We
> found the defect in preproduction, where it belongs: before a customer could be affected.”

### Cierre aprobado

> “The machine does the work it can prove. The person keeps the judgement. Cleveria turns that
> boundary into IAM, keys, and a verifier anyone can run.”

### Revisión ciega de los primeros 30 segundos

```text
Evalúa estos tres primeros cortes como tres jurados ciegos independientes.
Ordénalos sin conocer cuál defendemos y responde:
- cuál genera mayor confianza;
- qué evidencia esperas ver después;
- qué frase parece venta o exageración;
- qué dato no entiendes;
- si la apertura comunica el problema antes que la marca.

Elige una variante solo si al menos dos de tres jurados coinciden en el mismo defecto o ventaja.
```

### Producción visual y sonora

- Captura nativa GNOME Shell con `Ctrl+Alt+Shift+R`.
- `ffmpeg` para subtítulos quemados.
- `whisper` solo para verificar tiempos; escribir el `.srt` en inglés manualmente.
- `libopenh264` en este entorno, no `libx264`.
- Terminal a 28–36 px; navegador a 125% o más.
- Música por defecto: ninguna.
- Si se usa: instrumental CC0, 70–78 BPM, debajo de -30 dB, silenciada durante el `403`.
- No usar sonidos de “hacking”, glitches, risers ni wipes.
- Ocultar tokens, correos, IDs, nombres de clientes y claves.

No instalar `mcp-video`: la investigación existente lo identificó como un stub de 443 bytes sin
grabación funcional.

## Artículo técnico

### Prompt de redacción

```text
Edita un artículo técnico en inglés de 900–1.300 palabras para un jurado de agentes autónomos.
Título obligatorio o equivalente medido:
"Fifty-eight machine closures wore a human signature. We found them in preproduction."

Orden:
1. defecto medido y contexto de preproducción;
2. por qué no era un problema que se resolviera con un prompt;
3. diseño de la frontera IAM/KMS;
4. flujo de decisión, pausa, firma y verificación;
5. arquitectura de modelos: solo Gemini adjudica;
6. nueve kill-tests y banco adversarial;
7. limitación de Model Armor y mitigaciones;
8. qué no está construido;
9. lecciones y reproducción.

Distingue con encabezados o tabla entre garantizado y mitigado. No escribas como nota de prensa.
No uses "lie", "absolved itself", "unhackable", "production-ready" ni "fully autonomous".
Conserva números solo cuando exista una prueba adjunta.
```

### Control del artículo

- Título y apertura no deben prometer autonomía antes del freno.
- “Preproduction” debe aparecer donde se describen las 58 filas.
- No decir que QNOWA usa ya el lock completo.
- No presentar Agent Gateway o memoria de largo plazo como construidos.
- Incluir comandos reales y distinguir offline/cloud.
- Enlazar el diagrama y el repositorio.
- Mantener el artículo en inglés o preparar traducción fiel.

## README y repositorio

```text
Reestructura README.en.md para un juez con 60 segundos y un ingeniero que quiere reproducirlo.

Orden:
1. una línea de producto y la tesis;
2. categoría y requisitos Google usados;
3. Quick Judge Path;
4. arquitectura visual;
5. demostración de 403;
6. verificador offline;
7. flujo Cloud-backed;
8. kill-tests con duración y dependencia;
9. guarantees vs mitigations;
10. limitaciones y piezas no construidas;
11. setup completo;
12. licencia, procedencia y disclosure.

No pongas decidir_como_persona.py bajo una sección que diga "sin deploy" si requiere gcloud,
Cloud KMS o Cloud Run.
```

### Quick Judge Path recomendado

```text
python3 src/verificar_sobre.py libro/firmas_grafo.jsonl
python3 agente/grafo.py
python3 agente/killtest_canonico.py
python3 agente/killtest_inyeccion.py
python3 agente/killtest_alcance.py
```

Marcar claramente cuáles pruebas requieren credenciales y cuáles son offline. Mantener los nueve
kill-tests enumerados, aunque el recorrido corto muestre solo los más decisivos.

## Diagrama de arquitectura

```text
Genera un diagrama 16:9 y SVG editable basado exclusivamente en README.en.md:

Cloud Scheduler → Cloud Run/agent identity → deterministic authority ceiling → Gemini adjudication
→ deterministic router
→ machine key / human pause / unsigned return
→ human signature on human machine
→ offline verifier
→ Firestore durable record

Dibuja límites de confianza, principals IAM, estado persistente y rutas de fallo. Etiqueta la
ausencia de Agent Gateway y long-term memory como "not built", no como componentes existentes.
Usa azul para agente, ámbar para pausa, verde para verificación y rojo solo para 403.
```

## Página de Devpost

```text
Redacta todos los campos de Devpost en inglés con tono técnico y factual.

Incluye:
- problema real y medición 58/4;
- solución Cleveria.ai en una frase;
- categoría Fortified Enterprise Fleet;
- Gemini 3.6 Flash, embedding model, STT/TTS;
- Google ADK;
- Cloud Run, Cloud KMS, Firestore y Cloud Scheduler;
- cómo la máquina es bloqueada por IAM;
- qué puede probar un juez;
- limitaciones honestas;
- URL de demo, repositorio, diagrama y vídeo;
- disclosure: Cleveria.ai harness, QNOWA operational scenario, built and operated by
  Softronica.co.

No uses claims de cliente, escala, certificación o producción sin evidencia.
```

### Texto corto aprobado

> Cleveria.ai is an agent identity harness for workflows where a machine must act without being
> able to impersonate human judgement. It signs only what it can prove, pauses when a person must
> decide, and lets anyone verify the resulting record independently.

## Demo hospedada y pruebas

```text
Diseña la experiencia de prueba para un juez que no conoce el proyecto.

Entrega:
- landing de una pantalla;
- botón o comando "Run the proof";
- tres casos precargados;
- resultado machine-signed / human-required / unsigned;
- enlace a verifier;
- enlace a arquitectura;
- estado de disponibilidad;
- instrucciones de credenciales mínimas;
- mensaje explícito si un servicio cloud no está disponible.

Nunca simules una respuesta cloud ni presentes un mock como ejecución real. Si hay un fallback
local, etiquétalo "offline verifier" y no "live deployment".
```

## Contenido opcional y redes

### Artículo de construcción

```text
Escribe un post público de 700–1.000 palabras sobre cómo se construyó Cleveria para el hackathon.
Incluye una frase explícita: "I created this piece of content for the All Things Agentic
Hackathon." Cuenta tres fallos encontrados y corregidos, no solo éxitos. No divulgues secretos,
PII ni información de clientes.
```

### Publicación social

```text
Escribe tres opciones de post técnico para LinkedIn/X, máximo 280 caracteres cada una.
Incluye #AllThingsAgenticHackathon. Deben mencionar una evidencia concreta (58/4, IAM 403,
verificador offline o voz) y evitar "revolutionary", "unhackable" y "fully autonomous".
```

### Modelo adicional

No añadir Gemma, Veo o Lyria por decoración. Si se integra un modelo adicional:

1. debe tener una función visible y necesaria;
2. debe aparecer en el código y en el vídeo;
3. debe documentarse con versión y coste;
4. debe fallar de forma segura;
5. debe probarse desde un entorno limpio.

Un bonus pequeño no justifica una integración inestable que dañe la puntuación base.

## Revisión adversarial final

```text
Revisa el paquete completo como:
1. juez de Stage One;
2. juez de innovación;
3. juez de arquitectura;
4. juez de demo;
5. ingeniero que intenta reproducirlo;
6. revisor de propiedad intelectual;
7. revisor de accesibilidad y privacidad.

Devuelve una tabla:
severity | artifact | exact text/visual | issue | evidence required | surgical fix

Busca especialmente:
- requisitos obligatorios ausentes;
- diferencias entre vídeo, artículo y README;
- producción vs preproducción;
- números sin fuente;
- marcas que sugieren patrocinio;
- logos de terceros;
- claims de seguridad absoluta;
- comandos que no funcionan;
- credenciales o PII;
- subtítulos ilegibles;
- duración superior a cuatro minutos.
```

## Paquete final y nombres

```text
submission/
  README.en.md
  ARTICULO.en.md
  VIDEO_SCRIPT.en.md
  ARCHITECTURE.svg
  ARCHITECTURE.png
  demo/
  assets/
    cleveria-logo.svg
    cleveria-mark.svg
    cleveria-brand-guide.pdf
  evidence/
    verifier-output.txt
    killtests-summary.txt
    cloud-403.png
    iam-policy-sanitized.png
  video/
    cleveria-demo.mp4
    subtitles-en.srt
  disclosure/
    provenance.md
    licenses.md
```

Conservar los archivos editables y hashes del vídeo, artículo y capturas que se entreguen.

## Gate final antes de pulsar Submit

- [ ] Una sola categoría seleccionada.
- [ ] Gemini 3.5 o superior demostrable.
- [ ] Google Agent Framework demostrable.
- [ ] Google Cloud visible en vídeo o demo.
- [ ] Repositorio accesible y reproducible.
- [ ] README con spin-up instructions.
- [ ] Diagrama incluido.
- [ ] Vídeo en inglés o con subtítulos ingleses.
- [ ] Vídeo menor de cuatro minutos.
- [ ] Apertura basada en el defecto medido.
- [ ] `403` claramente legible.
- [ ] Artículo, README y vídeo usan las mismas cifras.
- [ ] “Preproduction” no se transformó accidentalmente en “production”.
- [ ] Garantías y mitigaciones están separadas.
- [ ] Lo no construido está declarado.
- [ ] Demo sin secretos ni PII.
- [ ] Licencias revisadas.
- [ ] URL del repositorio y vídeo funcionan en ventana privada.
- [ ] Se guardó copia exacta de la entrega.
- [ ] Se publicó el contenido opcional solo si está aprobado.

## Regla de decisión

Cuando Claude proponga una opción más espectacular y otra más verificable, elegir la verificable.
La puntuación se gana haciendo que el jurado recuerde una cadena causal:

> **Defecto medido → Cleveria boundary → IAM/KMS 403 → pausa humana → verificación independiente.**
