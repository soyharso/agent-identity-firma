---
doc_kind: handoff
estado: vigente
fecha: 2026-08-29
perfil: P1
ambito: >
  aplicar al artículo y al texto de la última versión del vídeo la misma técnica que ya cambió la
  apertura: generar variantes, medirlas con jurados ciegos baratos y quedarse con la ganadora.
entrega: >
  la tabla de variantes con su orden según tres jurados independientes, la ganadora escrita entera,
  y el motivo textual que dieron los jurados.
---

# BRIEF — clev-articulo-medido

**Búsqueda previa (C1)**: `ls docs/strategy/handoffs/` da 111 archivos y
`find docs -iname '*BRIEF*articulo*' -o -iname '*BRIEF*medido*'` no devuelve nada: **no existe
ningún brief de artículo ni de medición de texto**. La técnica sí está corrida y documentada, en
[`../metodo/ganar-hackathon/2026-08-28_GUION_video_compuesto.md`](../metodo/ganar-hackathon/2026-08-28_GUION_video_compuesto.md)
§6, sobre la apertura del vídeo. **Esto no la reinventa: la repite sobre otro texto.**

## Objetivo

**Que el artículo y el texto de la última versión del vídeo dejen de elegirse por gusto.** Se
generan variantes de lo que más manda —el título y el primer párrafo—, se miden con jurados ciegos,
y se entrega la ganadora con el motivo que dieron.

## Por qué esta técnica y no una opinión

Corrida el 2026-08-28 sobre la apertura del vídeo: cuatro variantes, tres jurados ciegos de tres
fabricantes, orden rotado. **La apertura que el equipo daba por buena quedó última para dos de los
tres**, y los dos dieron el mismo motivo. Coste: tres llamadas baratas y quince minutos.

## Lo que hay que hacer, en orden

1. **Leer, sin editarlo**, el artículo `ARTICULO.en.md` del repositorio entregable.
2. **Escribir tres variantes** del título y del primer párrafo, con ángulos distintos entre sí. Una
   tiene que ser **la actual, sin tocar**, o la comparación no sirve.
3. **Medir con tres jurados ciegos** de tres fabricantes distintos:
   `bash tools/run_llm_openrouter.sh --model <modelo> --user-file <prompt> --max-tokens 8000
   --sin-contrato --out-dir <destino>`. Modelos baratos: `deepseek/deepseek-v4-flash`,
   `z-ai/glm-5.2`, `qwen/qwen3.8-max`.
   **Rotar el orden de presentación en cada jurado**, o se ordena por posición y la medición no
   vale.
4. **Preguntar cuatro cosas**: que las ordene de mejor a peor; qué espera leer tras la mejor; por
   qué abandonaría la peor; y **si alguna le suena a venta o a exageración**. Esta última es la que
   más ha pagado hasta ahora.
5. **Escribir el resultado** en `docs/strategy/metodo/ganar-hackathon/produccion-video/`: la tabla
   de órdenes, la ganadora entera, y las frases textuales del motivo.

## Dos correcciones de contenido que hay que aplicar sí o sí

1. **NO se dice «producción».** Los agentes de esta casa **no están en producción: están en
   preproducción**, y precisamente para evitar problemas peores. Cualquier frase del artículo o del
   vídeo que diga o insinúe que el sistema corre en producción **es falsa y se corrige**. El defecto
   de las 58 firmas se midió en la operación real de la casa, antes de poner agentes en producción,
   y así hay que decirlo.
2. **Nunca prometer autonomía antes de enseñar el freno.** Un jurado ciego marcó como venta la
   frase «puede cerrar tareas solo, todo el día». Si una frase promete autonomía, el límite va en la
   misma frase.

## Ownership de rutas

**Trabaja solo en** `docs/strategy/metodo/ganar-hackathon/produccion-video/` y en su directorio
temporal.

**Lee, no edita**: el artículo del repositorio entregable, el guion compuesto y la ficha de vídeos
ganadores.

## Frontera de seguridad, y es dura

- **No toca `~/Desarrollos/agent-identity-firma`.** Es del frente `clev-transferencia-metodo-ce`,
  que construye ahí ahora mismo. Se lee, no se escribe.
- **No toca ningún repositorio de `~/Casos`.**
- **No publica nada.** Ni el artículo, ni redes, ni la entrega. Publicar es acto del operador.
- **No decide**: mide y entrega. Si aparece una decisión de criterio, se devuelve a
  `clev-ganar-hackathon`.
- **Si un gancho o el clasificador bloquea algo, se reporta y se para.** No se rodea por consola.

## Perfil declarado: P1

Trabajo acotado y con verificación, sin panel de modelos. Se declara aunque la palabra producción
aparezca solo para prohibirla, porque el medidor lo exige y porque un piso que solo dispara contra
quien es sincero no es un piso.

## Concurrencia, recursos y presupuesto

- **N_max: 1.** No hay clases paralelizables: las tres llamadas de una misma medición ya van a la
  vez dentro del mismo paso.
- **Recursos**: su directorio de salida y las llamadas a modelos baratos por la interfaz aislada.
- **Presupuesto y regla de parada**: **se para** cuando la ganadora esté escrita con su tabla, o si
  las tres llamadas no dan tres respuestas legibles en dos intentos. Modelos baratos únicamente.

## Ruteo de roles

**Un solo rol, `ejecutor`.** No hay divergentes ni juez que convocar: los jurados de esta medición
no juzgan el proyecto, solo ordenan textos, y por eso valen modelos baratos. El modelo por papel
sale del censo y no se decide en caliente.

## Reglas vigentes de esta corrida

- El vídeo es una sola toma corrida sin editar, con subtítulos en inglés quemados.
- Ningún nombre, marca ni dato de cliente, ni en pantalla ni en el texto.
- **Preproducción, no producción.**

## Cierre

Terminar con `FLOTA clev-articulo-medido: LISTO PARA CERRAR ✅`, la tabla de órdenes y la ganadora.
Y emitir la fila de telemetría con `python3 tools/metodo/scorecard.py emit --run
articulo-medido-2026-08-29 --frente clev-articulo-medido --perfil P1 --canal openrouter`, anotando
**qué modelo hizo de jurado en cada una de las tres llamadas**: sin eso, el evaluador no puede
actualizar lo que cada modelo vale en este papel.
**No cerrar la ventana**: eso lo hace el operador.

<!-- mejorar_brief: PASS 2026-08-27T20:48:53-05:00 -->

---

## Nota de esta ventana (añadida al copiar el brief aquí)

Estás en un **worktree propio del repositorio entregable**, rama `articulo-medido`. El artículo que
hay que medir está aquí mismo: `ARTICULO.en.md`. **Puedes editarlo en esta rama** — no toca el
checkout donde el otro frente sigue trabajando, que es de lo que se trata.

El lanzador de modelos NO está en este repositorio. Se llama por ruta absoluta:

```
bash /home/softboy/Desarrollos/experimentos/cleveria-dominios/.claude/worktrees/clev-ganar-hackathon/tools/run_llm_openrouter.sh \
  --model deepseek/deepseek-v4-flash --user-file <prompt.txt> --max-tokens 8000 \
  --sin-contrato --out-dir <destino>
```

Escribe tu resultado en `MEDICION_articulo.md`, en la raíz de este worktree. **No hagas merge ni
push**: cuando termines, avisa y el operador decide qué se lleva a la rama principal.
