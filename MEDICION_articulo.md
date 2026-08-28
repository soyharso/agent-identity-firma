# Medición ciega — clev-articulo-medido

Fecha de la corrida: 2026-08-29. Se midieron por separado el título y la apertura del
artículo y el título y la apertura del vídeo. Cada jurado recibió las mismas variantes en
orden rotado: DeepSeek A-B-C, GLM B-C-A, Qwen C-A-B.

## Órdenes de los jurados

| Jurado | Modelo | Artículo, mejor → peor | Vídeo, mejor → peor |
|---|---|---|---|
| 1 | `deepseek/deepseek-v4-flash` | A → B → C | B → C → A |
| 2 | `z-ai/glm-5.2` | B → C → A | B → C → A |
| 3 | `qwen/qwen3.8-max` | B → C → A | B → C → A |

Ganadoras por respaldo conjunto: **Artículo B** (2 de 3 primeras posiciones) y **Vídeo B**
(3 de 3). La variante A del artículo quedó primera para un jurado, pero B fue la opción
mayoritaria y más técnica.

## Motivos textuales de los jurados

Para el artículo, los jurados describieron B como “very clear”, con “the boundary the service
could not cross”, y esperaron “a concrete, technical breakdown of the system architecture that
enforces this boundary”. El motivo para abandonar A fue que “it ends on a defensive, PR-style
reassurance (‘it cost nobody anything’) instead of explaining the technical root cause”.
También señalaron como exagerada la frase de A: “a machine had absolved itself and signed a
person's name to it”. En C, marcaron el título “We gave an agent a human signature” como
potencialmente engañoso porque sugiere una concesión deliberada.

Para el vídeo, B fue descrito como “very crisp” y como la apertura que “states clearly that
machine cannot judge”. Los jurados esperaron ver “the exact point where the machine is blocked,
the handoff to a human, and the audit trail”. A fue la peor porque “it frames a software
permission error as intentional deception”; citaron “Fifty-eight times it was a lie” y
“absolved itself”. C también recibió una objeción menor por “Four were self-absolutions”.

## Ganadora escrita entera

### Artículo B — corregido a preproducción

**Title: Fifty-eight machine closures wore a human signature. We found them in preproduction.**

On 26 August 2026, we counted 58 rows marked "human" even though a machine had closed them.
Four were in the dismissed state, where a complaint is thrown out. The agents were still in
preproduction, deliberately: the defect surfaced before any customer could meet it, and the
records let us measure exactly what happened.

No model chose to impersonate anyone. A default field and a missing system state made the wrong
attribution the only path available to an agent. The repair was not a better prompt. It was a
boundary the service could not cross.

### Vídeo B

**Title: Before the agent can act, the boundary has to hold**

“Fifty-eight records said 'human' although a machine had closed them. Four were dismissals. We
found the defect in preproduction, where it belongs: before a customer could be affected.”

“The machine can do the work it can prove, but it cannot make a judgement about a person. When a
task crosses that line, the flow stops and waits for a human. The same key that lets it work
prevents it from signing as one.”

## Telemetría

Se emitió la fila del run `articulo-medido-2026-08-29` declarando los tres jurados:
`deepseek/deepseek-v4-flash`, `z-ai/glm-5.2` y `qwen/qwen3.8-max`.
