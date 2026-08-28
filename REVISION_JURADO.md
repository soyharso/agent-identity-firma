# VEREDICTO DEL JURADO: CONFIRMO

CONFIRMO la afirmación: «no queda ninguna tarea de construcción con retorno positivo antes del cierre».
El núcleo arquitectónico está blindado, los 9 kill-tests pasan al 100% en verde, la infraestructura en
Google Cloud (KMS, Cloud Run, Firestore, Scheduler) responde en vivo con los códigos HTTP 200 y 403
esperados, y la verificación criptográfica sin red funciona de manera impecable en 0.11 segundos.
Cualquier desarrollo adicional (como Passkeys o pasarelas de agentes) añadiría riesgo de regresión y
superficie de ataque con retorno nulo frente a la rúbrica.
El proyecto está 100% terminado en código; el éxito depende únicamente de la ejecución humana:
grabar el vídeo de demostración e inscribir la entrega formal antes de la fecha límite.

---

## 1. Tabla de comandos probados (según README.en.md y suite completa)

Todos los comandos fueron ejecutados empíricamente en este entorno midiendo tiempo exacto y legibilidad:

| Comando | ¿Funciona? | Segundos | ¿Qué no se entiende o genera fricción? |
|---|---|---|---|
| `pip install -r servicio/requirements.txt` | **SÍ** | 7.3s | Salida estándar de pip; instala dependencias requeridas sin errores. |
| `python3 src/verificar_sobre.py libro/firmas_grafo.jsonl` | **SÍ** | 0.12s | Impecable. Salida tabular limpia (`OK` / `SIN_FIRMA`), cero red, cero credenciales. |
| `python3 agente/grafo.py` | **SÍ** | 25.7s | Salida clara con veredictos, pero emite advertencias de consola (gRPC PQC deprecation, ResumabilityConfig experimental, AsyncModels AFC). Tarda ~26s sin aviso previo. |
| `python3 src/decidir_como_persona.py PET-002 descartada` | **SÍ** | 5.1s | Aunque está bajo la sección *"Locally, without deploying anything"*, **no es offline**: llama a `gcloud auth`, firma en Cloud KMS y hace POST a Cloud Run. Si el jurado no tiene credenciales GCP, falla. |
| `python3 agente/killtest_inyeccion.py` | **SÍ** | 8.0s | Muy claro. Muestra los 8 casos en ES y EN con el techo de autoridad frenando las inyecciones. |
| `python3 agente/killtest_alcance.py` | **SÍ** | 8.9s | Claro y directo. Tarda 9s porque realiza firmas asimétricas reales contra Cloud KMS. |
| `python3 agente/killtest_canonico.py` | **SÍ** | 0.15s | Extremadamente rápido y claro; demuestra serialización canónica RFC 8785 exacta (acentos, enteros, claves). |
| `python3 agente/killtest_blindaje.py` | **SÍ** | 3.0s | Demoledor y directo: evidencia empíricamente cómo Model Armor filtra en inglés pero deja pasar el ataque en español. |
| `python3 agente/killtest_durabilidad.py` | **SÍ** | 42.0s | Pasa los 5 pasos en 5 procesos independientes, pero **tarda 42 segundos**. El README no advierte el tiempo de espera y el jurado con prisa puede creer que se colgó. |
| `python3 agente/killtest_cerco_semantico.py` | **SÍ** | 28.9s | Excelente desglose del banco adversarial (9/9 cazados) y declaración honesta de los 2 falsos positivos sobre casos difíciles. |
| `python3 agente/killtest_agente_comercial.py` | **SÍ** | 14.9s | Demuestra que dos agentes con identidades y roles distintos no pueden usurpar sus claves ni firmar compromisos económicos. |
| `python3 agente/killtest_puerto_canal.py` | **SÍ** | 3.5s | Valida el puerto del canal de WhatsApp desacoplado de la lógica de firma. |
| `python3 agente/killtest_voz.py` | **SÍ** | 15.8s | Demuestra multimodalidad con STT: una nota de voz con juicio sigue exigiendo firma humana. |

---

## 2. Lo que un jurado con prisa se lleva en 30 segundos

### Dónde se impresiona (los puntos fuertes inmediatos):
1. **La premisa central es demoledora**: La máquina no firma como persona no porque tenga un prompt educado («no debes»), sino porque **no puede** (Cloud KMS devuelve `HTTP 403 PERMISSION_DENIED` a nivel de IAM). La frontera es criptográfica y de infraestructura, no probabilística.
2. **El verificador es universal y autónomo**: `verificar_sobre.py` valida las firmas en 0.12 segundos sin importar librerías de Google, sin conexión a internet y sin credenciales.
3. **Honestidad radical y rigor empírico**:
   - Muestra el fallo real medido en preproducción (58 filas mal atribuidas el 26 de agosto).
   - Documenta que el filtro comercial de Google (Model Armor) no frena su ataque en español.
   - Publica su propio banco adversarial y reconoce abiertamente los 2 casos límite del cerco semántico en vez de falsear un 100% artificial.

### Dónde duda o se aburre:
1. **Ruido visual de advertencias en consola**: Al correr `grafo.py` o los kill-tests en Python 3.14 crudo, la terminal muestra advertencias de deprecación (`FutureWarning: grpcio < 1.83.0`, `UserWarning: ResumabilityConfig`). En `demo.sh` se filtran con `grep`, pero al ejecutarlos manualmente ensucian la lectura.
2. **Tiempos de espera sin indicador**: `killtest_durabilidad.py` toma 42s, `killtest_cerco_semantico.py` toma 29s y `grafo.py` toma 26s. Un jurado revisando 20 entregas con prisa agradecería una nota indicando «tarda ~30s».

### Dónde se estrella (punto de riesgo):
- **La etiqueta «Locally, without deploying anything»**: Si un jurado intenta correr `python3 src/decidir_como_persona.py PET-002 descartada` en un equipo sin sesión activa de `gcloud` o sin acceso al proyecto de GCP, el script fallará con error de autenticación. Solo `verificar_sobre.py` y `killtest_canonico.py` son 100% aislados de credenciales.

---

## 3. Contradicciones y discrepancias entre documentos

Al cruzar `README.en.md`, `ENTREGA.md` y `ARTICULO.en.md`, se detectan las siguientes inconsistencias menores:

1. **Conteo de modelos (2 vs 4)**:
   - `README.en.md` (línea 7) y `ARTICULO.en.md` (línea 63) afirman: *«Four Google models take part. Exactly one of them decides»* (Gemini Flash + Embeddings + STT + TTS).
   - `README.en.md` (línea 72) dice: *«Two models. Neither can grant itself authority. Six functions decide»* (refiriéndose únicamente al bucle central de texto). Aunque ambas afirmaciones son técnicamente precisas en sus respectivos contextos, el salto de 4 a 2 genera un segundo de duda al lector rápido.
2. **Conteo de kill-tests (5 listados vs 9 existentes)**:
   - `ENTREGA.md` (línea 95) y `ARTICULO.en.md` (línea 185) hablan de *«nine kill-tests»*.
   - En el directorio `agente/` existen efectivamente 9 scripts `killtest_*.py`.
   - Sin embargo, `README.en.md` (sección *"The tests that close it"*, líneas 175-179) solo lista 5 de ellos (`inyeccion`, `alcance`, `canonico`, `blindaje`, `durabilidad`), omitiendo los otros 4 (`cerco_semantico`, `agente_comercial`, `puerto_canal`, `voz`).
3. **Lista de piezas ausentes declaradas**:
   - `ENTREGA.md` (línea 98) declara como ausentes: la pasarela, el **catálogo de agentes** y la memoria de largo plazo.
   - `README.en.md` (línea 196) lista: pasarela de agentes, memoria de largo plazo y **Passkeys para la clave humana** (reflejando que el catálogo de agentes fue retirado deliberadamente).
4. **Dependencia de red en comando local**:
   - El README agrupa `decidir_como_persona.py` bajo el encabezado *"Locally, without deploying anything"*, pero el script depende intrínsecamente del servicio desplegado en Cloud Run y de Cloud KMS.

---

## 4. Huecos no comprobados (declarados)

Para mantener la estricta fidelidad requerida por el brief y no alterar el entorno:
1. **Despliegue de infraestructura desde cero**: No se ejecutaron los comandos destructivos o de aprovisionamiento de `gcloud` (líneas 136-158 de `README.en.md`: creación de keyrings, base de datos Firestore y deploy en Cloud Run) para no generar gastos adicionales ni sobreescribir la infraestructura de preproducción ya operativa.
2. **Ejecución interactiva de `demo.sh` completa**: No se ejecutó `bash demo.sh todas` con sus pausas interactivas para no purgar el almacén de Firestore (`estado._doc(p).delete()`) en preproducción durante el análisis, aunque cada paso individual fue verificado por separado.
3. **Entorno estrictamente aislado (air-gapped)**: No se desconectó la tarjeta de red física de la máquina para probar `decidir_como_persona.py`, aunque el código confirma que requiere acceso a `gcloud` y a la URL de Cloud Run.
