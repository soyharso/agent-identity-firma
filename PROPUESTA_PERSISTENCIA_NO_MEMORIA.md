# Propuesta adversarial: “Persistence is not memory”

## Veredicto

El concepto es adecuado como **marco explicativo** para el artículo y el vídeo, pero no como
pretexto para añadir Memory Bank, vector search o una plataforma completa antes del hackathon.

La afirmación defendible es:

> **The process does not remember. The workflow facts survive.**

El agente crea un `InMemoryRunner` nuevo; Firestore conserva los hechos mínimos necesarios para
continuar: petición, estado, reserva, pausa, decisión y firma. Eso es persistencia de estado de
dominio, no memoria conversacional ni memoria semántica.

## Inventario honesto

| Capacidad | Estado | Cómo presentarla |
|---|---|---|
| Estado de sesión ADK | Implementado como memoria efímera | Se pierde al morir el proceso |
| Estado durable del workflow | Implementado en Firestore | Es la fuente autoritativa de continuidad |
| Recuperación tras reinicio | Implementada y probada con cinco procesos | El proceso nuevo reconstruye; no recuerda |
| Idempotencia | Implementada con reserva/transacción | Evita duplicar trabajo o firmas |
| Verificador offline | Implementado | Verifica firma y alcance; el texto requiere suministrarse |
| Embeddings | Parcial | Cerco semántico contra anclas estáticas; no es memoria |
| Vector Search | No construido | No mencionarlo como función |
| Memory Bank | No construido | No usar este término salvo para explicar su ausencia |
| Auditoría | Parcial | Firestore + JSONL local; el JSONL no es durable en Cloud Run |
| OpenTelemetry | No construido | No prometer observabilidad empresarial completa |
| Agent Gateway/Registry | No construido | Declararlo explícitamente |
| WhatsApp conectado al lock | No construido | El puerto existe, la integración no |

## Decisión para el artículo

### Título

**Persistence Is Not Memory: What Survives When the Agent Dies**

### Subtítulo

**Firestore preserves workflow facts. The model session does not—and that is the safety boundary.**

### Estructura recomendada

1. **La caída**: el proceso desaparece durante una pausa humana.
2. **La distinción**: sesión, persistencia, auditoría y memoria semántica.
3. **El mecanismo**: nuevo `InMemoryRunner`, lectura de Firestore y reanudación segura.
4. **La prueba**: cinco procesos independientes y decisión sin firma que vuelve a pausar.
5. **La frontera criptográfica**: KMS, alcances y firma humana fuera del servicio.
6. **El papel del modelo**: puede pedir más prudencia, nunca ampliar autoridad.
7. **Hallazgos adversariales**: inyección bilingüe, serialización y limitaciones del filtro.
8. **Lo que no se construyó**: Memory Bank, vector search, gateway, registry, WhatsApp y passkeys.
9. **Lecciones**: persistir hechos mínimos es distinto de hacer que el modelo “recuerde”.

### Texto central

> “We did not persist the conversation and we did not try to make the model remember. We persisted
> only the facts required to continue safely: which request this was, what was evaluated, who
> must decide, and which signature was verified.”

### Claims prohibidos

- “The agent has enterprise memory.”
- “We built Memory Bank.”
- “The agent remembers previous decisions.”
- “Vector search retrieves historical context.”
- “The session is durable.”
- “Only a specific person can sign”, unless the human identity is cryptographically bound and
  demonstrated.

## Decisión para el vídeo

### Secuencia de cuatro minutos

| Tiempo | Prueba |
|---|---|
| 0:00–0:25 | Pausa humana y documento Firestore; etiqueta `PREPRODUCTION` |
| 0:25–1:05 | Nuevo proceso y lectura del estado durable |
| 1:05–1:45 | Decisión sin firma: el flujo no se resuelve y vuelve a pausar |
| 1:45–2:25 | Intento de firmar como humano; `403 PERMISSION_DENIED` real |
| 2:25–3:00 | Firma fuera del servicio y verificador offline |
| 3:00–3:30 | Kill-tests y cerco semántico; distinguir filtro de garantía |
| 3:30–3:48 | Cloud Run, Firestore, Scheduler y KMS |
| 3:48–4:00 | Cierre y disclosure |

### Apertura

> “The agent stopped. Then its process disappeared. The question was not whether it remembered.
> The question was what survived.”

### Explicación técnica

> “This is a new process. It has no session memory from the previous one. It reads the durable
> workflow facts from Firestore and reconstructs the safe next step.”

### Cierre

> “Persistence preserves the facts needed to continue safely. It is not memory, and it is not
> authority.”

La toma del `403` sigue siendo el centro emocional y técnico. La persistencia debe reforzar la
tesis, no competir con ella.

## Cambios de código que sí tienen retorno

### P0 — Vincular la firma con la petición y decisión correctas

Antes de aceptar `/decidir`, validar:

- `sobre["peticion_id"] == pid`;
- `sobre["estado_destino"] == decision`;
- el hash del sobre corresponde al texto actual;
- la decisión HTTP coincide con el estado firmado;
- la firma no es reutilizada en otra petición;
- el actor autenticado es el autorizado para esa ruta.

Sin estas comprobaciones, una firma humana válida podría asociarse conceptualmente con otra
petición. La frontera “la máquina no puede firmar como humano” seguiría funcionando, pero la
atribución de **qué** decidió la persona sería incompleta.

### P1 — Hacer obligatorias las identidades de las rutas

`IDENTIDAD_HUMANA` e `IDENTIDAD_TEMPORIZADOR` no deben aceptar valores vacíos. El servicio debe
fallar al arrancar si faltan y el README debe documentar los bindings de Invoker.

### P1 — Corregir el alcance del verificador

Decir exactamente:

- sin texto original: verifica firma, algoritmo y alcance;
- con `--texto-archivo`: verifica también que el contenido corresponda al hash.

### P1 — Separar auditoría durable de artefacto local

No llamar “auditoría durable” a `libro/firmas_grafo.jsonl` en Cloud Run. Presentarlo como artefacto
local de demostración o mover eventos a Firestore/Cloud Storage si queda tiempo.

### P1 — Limpiar la superficie de presentación

Marcar como legacy o excluir de la ruta del juez los archivos que usan otra arquitectura:

- `agente/agent.py` con otro modelo;
- `src/firmar_humano.py`;
- `src/firmar_agente.py`;
- `src/verificar_kms.py`.

Un juez no debe encontrar dos esquemas incompatibles sin explicación.

## Qué no construir ahora

- Memory Bank.
- Vector database o búsqueda histórica.
- Agent Gateway.
- Agent Registry.
- Integración completa de WhatsApp.
- Passkeys.
- Observabilidad completa con dashboards.

Construir esas piezas generaría más superficie de fallo y convertiría una primitiva de identidad
bien demostrada en una plataforma incompleta.

## Matriz de ataque del jurado

| Pregunta adversarial | Respuesta honesta |
|---|---|
| ¿El agente recuerda? | No; el proceso nuevo reconstruye desde Firestore |
| ¿Es Memory Bank? | No; es estado durable de workflow |
| ¿Hay vector search? | No; hay un cerco semántico contra anclas |
| ¿El JSONL sobrevive a Cloud Run? | No; la auditoría durable requiere otro almacén |
| ¿El verificador valida el texto automáticamente? | Solo si se proporciona el archivo original |
| ¿La clave identifica a una persona concreta? | No necesariamente; identifica la capacidad de firmar |
| ¿El filtro de Google es la garantía? | No; es una mitigación que tiene limitaciones |
| ¿Cubre toda la Fleet Platform? | No; cubre identidad, alcance, pausa y verificación |

## Regla de aprobación

El concepto entra en la entrega solo si cada aparición de “memory”, “durable”, “audit”,
“production” y “identity” pasa esta prueba:

1. ¿Existe una evidencia concreta en código o consola?
2. ¿La evidencia demuestra exactamente la frase?
3. ¿La frase distingue implementado, parcial y no construido?
4. ¿La afirmación conserva `preproduction` cuando corresponde?

Si una respuesta es negativa, se reduce el claim en vez de aumentar la funcionalidad.
