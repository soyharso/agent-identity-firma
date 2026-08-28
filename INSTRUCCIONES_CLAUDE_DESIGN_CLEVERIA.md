# Instrucciones completas para mejorar la imagen corporativa de Cleveria.ai con Claude Design

## 1. Objetivo

Crear una identidad visual coherente para **Cleveria.ai**, un harness de identidad y autoridad para
agentes autónomos. La marca debe comunicar:

> **El agente puede trabajar. No puede firmar como una persona.**

La identidad debe parecer una herramienta técnica precisa, confiable y verificable; no una agencia
de marketing, un chatbot, un proveedor genérico de ciberseguridad ni una startup que promete
“autonomía total”.

## 2. Arquitectura de marca que Claude debe respetar

| Marca | Papel | Visibilidad |
|---|---|---|
| **Cleveria.ai** | Producto técnico / harness de identidad | Protagonista |
| **QNOWA** | Escenario operativo y caso de uso | Secundario, solo cuando aporte contexto |
| **Softronica.co** | Operador, propietario y disclosure | Créditos, pie legal y página corporativa |

No mezclar las tres marcas en el logotipo principal. No crear una marca “Cleveria-QNOWA-
Softronica”. En una demo o presentación, Cleveria debe ser la única marca visible en la apertura.

## 3. Material de referencia que se debe entregar a Claude

Crear un proyecto de Claude Design y adjuntar:

1. `assets/cleveria-logo.svg`
2. `assets/cleveria-mark.svg`
3. `BRAND_CLEVERIA.en.md`
4. `PRESENTACION_JURADO.en.md`
5. `STORYBOARD_JURADO.en.md`
6. `README.en.md`
7. `ARTICULO.en.md`
8. Capturas reales, sin credenciales ni datos personales:
   - Cloud Run;
   - Cloud KMS/IAM;
   - resultado `403 PERMISSION_DENIED`;
   - verificador offline;
   - diagrama de arquitectura.

Antes de adjuntar cualquier captura, ocultar tokens, nombres de clientes, identificadores de
usuarios, correos personales, claves privadas y URLs internas.

## 4. Prompt maestro para Claude Design

Copiar este prompt al inicio del proyecto:

```text
Actúa como director/a de marca y diseñador/a senior de productos developer-first.

Rediseña la identidad corporativa de Cleveria.ai sin cambiar su tesis:
"The agent can work. It cannot sign as a person."

Cleveria.ai es un harness técnico de identidad, autorización y verificación para agentes
autónomos. El sistema demuestra una frontera criptográfica entre una máquina y una persona.
Debe comunicar precisión, sobriedad, ingeniería, trazabilidad y límites honestos.

La marca protagonista es Cleveria.ai. QNOWA es únicamente un escenario operativo. Softronica.co
es el operador y aparece solo en disclosure, créditos y contexto corporativo. No conviertas el
material en un anuncio de QNOWA ni de Softronica.

Usa como fuente de verdad los SVG, la guía de marca y el README adjuntos. No inventes funciones,
clientes, certificaciones, métricas, integraciones o disponibilidad en producción que no estén
documentadas. Los agentes están en preproducción; conserva esa precisión.

Evita robots, cerebros, escudos, candados genéricos, circuitos, servidores 3D, neón cyberpunk,
glitches, stock photography corporativa, manos estrechándose y promesas de autonomía total.
La evidencia real —IAM, KMS, Cloud Run, 403, Firestore, verificador y arquitectura— es el
principal recurso visual.

Entrega propuestas razonadas, no una colección de variaciones decorativas. Cada decisión debe
explicar qué aspecto de la tesis comunica y qué riesgo de interpretación evita.
```

## 5. Fase A — auditoría visual

Pedir primero un diagnóstico, sin diseñar todavía:

```text
Audita la identidad actual de Cleveria.ai en cinco dimensiones:
1. reconocimiento y memorabilidad;
2. credibilidad técnica;
3. legibilidad en terminal, vídeo, favicon y documentación;
4. diferenciación frente a marcas de IA y ciberseguridad;
5. coherencia entre producto, hackathon y comunicación corporativa.

Devuelve:
- fortalezas que no deben cambiar;
- problemas concretos;
- contradicciones entre marca y evidencia del producto;
- decisiones de alto impacto;
- elementos que deben eliminarse;
- una matriz impacto/esfuerzo.
No propongas todavía nuevos logos.
```

Aceptar cambios solo si resuelven un problema observable. No cambiar el logo por preferencia
subjetiva ni introducir una segunda paleta sin una justificación de legibilidad o contraste.

## 6. Fase B — sistema de identidad

```text
Conserva el concepto del logo actual: una C geométrica que se aproxima a un nodo verde de
verificación sin atravesar la frontera. Desarrolla el sistema, no un símbolo completamente
distinto.

Entrega:
- reglas de construcción y proporción;
- área de protección;
- tamaños mínimos;
- versiones horizontal, compacta, monocroma y una tinta;
- uso sobre fondo oscuro y claro;
- errores de uso;
- jerarquía entre Cleveria.ai, QNOWA y Softronica.co;
- ejemplos en GitHub README, consola, vídeo, diapositiva y favicon.

Los SVG deben permanecer editables, sin texto convertido en imágenes cuando pueda evitarse.
```

### Criterios de aceptación del logo

- Se reconoce a 24 px en el símbolo.
- El wordmark sigue siendo legible a 180 px de ancho.
- Funciona en escala de grises.
- No parece un escudo, una letra C genérica ni un botón de “play”.
- El nodo verde no se interpreta como un checkmark de marketing.
- No usa efectos que desaparezcan al exportar a vídeo o PDF.

## 7. Fase C — paleta y tipografía

Usar estos tokens como base, no sustituirlos sin una prueba comparativa:

| Token | Hex | Uso |
|---|---|---|
| `ink` | `#0B1020` | Fondo principal |
| `surface` | `#151D33` | Paneles y código |
| `text` | `#F8FAFC` | Texto principal |
| `muted` | `#A8B3C7` | Texto secundario |
| `agent-blue` | `#4285F4` | Flujo del agente |
| `agent-blue-soft` | `#8AB4F8` | Enlaces y resaltados |
| `verified-green` | `#34A853` | Verificación |
| `pause-amber` | `#F9AB00` | Espera de una persona |
| `denied-red` | `#EA4335` | Solo el `403` y denegaciones |

Prompt:

```text
Construye un sistema de color accesible con estos tokens. Comprueba contraste WCAG AA para texto
normal y grande. Devuelve valores HEX, RGB, HSL y variables CSS.

Define estados semánticos:
- machine/action;
- verified;
- human-required;
- denied;
- unknown/insufficient evidence.

No uses rojo como color dominante. No uses degradados en texto ni colores fluorescentes. Explica
qué combinaciones no deben usarse y proporciona sustitutos accesibles.
```

Tipografía recomendada:

- **Inter**: interfaz, títulos y cuerpo.
- **JetBrains Mono** o **DejaVu Sans Mono**: terminal y código.
- Fallbacks: `Arial, sans-serif` y `monospace`.
- Títulos: peso 600, no 800.
- Cuerpo: peso 400.
- Evitar cursivas decorativas, condensadas y display fonts futuristas.

## 8. Fase D — componentes corporativos

Solicitar una biblioteca de componentes con estas piezas:

```text
Diseña una UI kit de Cleveria.ai para documentación y presentaciones:
- title card;
- evidence card;
- terminal card;
- IAM policy card;
- 403 denial card;
- human handoff/pause card;
- verifier success card;
- guaranteed vs mitigated comparison;
- architecture node and connector;
- metric card;
- footer/disclosure;
- light and dark variants.

Cada componente debe incluir nombre, propósito, anatomía, estados, tamaños, espaciado, color,
tipografía, ejemplo correcto y ejemplo incorrecto. La evidencia debe tener prioridad visual sobre
la marca.
```

Sistema de espaciado:

- base de 8 px;
- radios de 8 px para paneles;
- radios de 4 px para controles técnicos;
- bordes de 1 px;
- sombras mínimas o inexistentes;
- no usar tarjetas flotantes con exceso de profundidad.

## 9. Fase E — presentación para jueces

```text
Diseña una presentación de 8 diapositivas, en inglés, para un jurado técnico con poco tiempo.
Formato 16:9, fondo ink, alto contraste, máximo una idea por diapositiva.

Orden obligatorio:
1. measured defect: 58 and 4, labelled PREPRODUCTION;
2. thesis: the agent can work, it cannot sign as a person;
3. real workflow and three outcomes;
4. IAM/KMS boundary;
5. live 403 PERMISSION_DENIED;
6. offline verifier and audit trail;
7. adversarial tests and honest limitations;
8. closing thesis, repository URL and disclosure.

No empieces con un eslogan aislado. La tesis aparece después del dato medido o en la misma
secuencia causal. No uses fotografías. Usa el diagrama, terminal, consola y resultados reales.
```

Reglas de diapositivas:

- máximo 35 palabras visibles, salvo logs;
- una cifra grande solo si tiene contexto;
- nunca ocultar `PREPRODUCTION`;
- el `403` debe ser legible a pantalla completa;
- usar la misma posición para etiquetas de estado;
- pie final: `Cleveria.ai harness · QNOWA operational scenario · Built and operated by
  Softronica.co`.

## 10. Fase F — vídeo y motion design

```text
Convierte el storyboard adjunto en un paquete de producción de vídeo de máximo cuatro minutos.
Entrega:
- lista de planos;
- texto en pantalla;
- duración de cada plano;
- transición;
- subtítulo en inglés;
- nivel de audio;
- elementos que deben ocultarse por privacidad.

Debe ser una toma corrida de evidencia técnica. Usa cortes duros y animaciones lineales. Congela
el frame del 403 al menos dos segundos. Cuando el flujo se detenga para una persona, detén también
la animación. No uses glitches, zooms dramáticos, partículas, hologramas ni música de suspense.
```

La grabación probada usa GNOME Shell, `ffmpeg` y subtítulos `.srt` quemados. No instalar ni usar
`mcp-video`, que fue identificado como un paquete stub no funcional.

## 11. Fase G — web, README y redes

Pedir tres adaptaciones, siempre derivadas del mismo sistema:

```text
Adapta Cleveria.ai a:
1. hero de landing técnica;
2. README de GitHub;
3. tarjeta social de 1200x675.

Mantén el mismo orden narrativo: defecto medido, frontera, prueba, límites. No conviertas ningún
formato en publicidad de autonomía. La publicación social debe ser técnica, factual y usar
#AllThingsAgenticHackathon solo cuando corresponda.
```

Copy aprobado para hero:

> **The agent can work. It cannot sign as a person.**

Subcopy:

> Identity and authorization boundaries for autonomous workflows, enforced by IAM, keys, and
> independent verification.

No usar:

- “fully autonomous AI”;
- “zero-risk agents”;
- “unhackable”;
- “production-ready” si la evidencia solo demuestra preproducción;
- “Google-certified”;
- “human-level judgement”.

## 12. Control de calidad con Claude

Después de cada entrega, usar este prompt:

```text
Haz una revisión adversarial de este artefacto como:
1. jurado técnico;
2. ingeniero de seguridad;
3. usuario que llega desde Google;
4. abogado de propiedad intelectual;
5. persona con daltonismo o baja visión.

Busca:
- promesas no demostradas;
- mezcla de marcas;
- claims de producción;
- logos o iconos de terceros no autorizados;
- contraste insuficiente;
- texto ilegible en vídeo;
- datos sensibles;
- apariencia de patrocinio o endorsement;
- clichés visuales de IA;
- diferencias respecto a los tokens de marca.

Clasifica cada hallazgo como bloqueante, importante o cosmético. No reescribas todavía.
```

Solo corregir primero los bloqueantes e importantes. Repetir la revisión después de corregirlos.

## 13. Entregables finales

Solicitar exportación en esta estructura:

```text
brand/
  cleveria-logo.svg
  cleveria-mark.svg
  cleveria-logo-mono.svg
  cleveria-mark-mono.svg
  cleveria-brand-guide.pdf
  cleveria-tokens.css
  cleveria-presentation.pptx
  cleveria-presentation.pdf
  cleveria-social-1200x675.png
  cleveria-favicon-512.png
  cleveria-favicon-192.png
  cleveria-title-card-16x9.png
  cleveria-disclosure.txt
```

Conservar también los archivos fuente editables. No aceptar únicamente PNG o capturas si el
logotipo puede entregarse como SVG.

## 14. Checklist antes de publicar

- [ ] Cleveria.ai es la marca protagonista.
- [ ] QNOWA aparece solo como escenario, sin fingir una integración no construida.
- [ ] Softronica.co aparece en disclosure y créditos.
- [ ] No se afirma producción cuando la evidencia es preproducción.
- [ ] No hay secretos, PII, tokens ni nombres de clientes.
- [ ] El logo funciona en claro, oscuro, monocromo y tamaño pequeño.
- [ ] El texto cumple contraste WCAG AA.
- [ ] La tesis no aparece como eslogan antes del dato que la demuestra.
- [ ] El `403` se lee sin pausar el vídeo.
- [ ] La música no compite con narración ni terminal.
- [ ] El vídeo dura menos de cuatro minutos.
- [ ] Los subtítulos en inglés están quemados y sincronizados.
- [ ] El diagrama coincide con la arquitectura real.
- [ ] Las limitaciones están separadas de las garantías.
- [ ] Se revisaron licencias de fuentes, iconos, música e imágenes.
- [ ] Se guardó una copia exacta de cada archivo enviado.

## 15. Regla final de decisión

Si una propuesta es más llamativa pero hace que el jurado dude de la evidencia, se descarta.
Elegir la variante que haga más fácil recordar y verificar esta relación:

> **Cleveria.ai → frontera de autoridad → `403` de Cloud KMS → verificador independiente.**
