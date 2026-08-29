# RUNBOOK DE GRABACIÓN FINAL V2 — CLEVERIA FLEET

**Fecha:** 2026-08-28  
**Versión:** 2.0 (Rediseñado con Dashboard Rich y Diagrama HTML Interactivo)  
**Objetivo:** Guiar la grabación de la demostración de 4 minutos combinando impacto visual, evidencia determinista en vivo y narrativa tipo pitch (problema ➔ clímax ➔ revelación).

---

## 1. CHECKLIST TÉCNICO PRE-GRABACIÓN

### 1.1 Verificación de Entorno (Terminal)
- [ ] **OBS Studio instalado:** `obs --version` (recomendado ≥ 30.0).
- [ ] **Dependencias Python:** `pip3 install rich`.
- [ ] **Credenciales GCP Frescas:** `gcloud auth list` (Asegurar que la identidad de operador esté activa).
- [ ] **Opcional (Edge TTS):** Si se prefiere narración sintética, preparar clips.

### 1.2 Archivos Clave Preparados
- [ ] `demo_rich_dashboard.py` — El dashboard de 4 paneles en vivo.
- [ ] `assets/slides/architecture_interactive.html` — Diagrama animado HTML5.
- [ ] `assets/slides/slide_title_cleveria.png` — Tarjeta visual de Intro/Outro (1080p).
- [ ] `VIDEO_SCRIPT.en.md` — El guion narrativo impreso o en segunda pantalla.

### 1.3 Configuración de Escenas en OBS (Transición *Fade* de 0.8s)
1. **Intro / Outro**: Fuente de Imagen apuntando a `slide_title_cleveria.png`.
2. **Dashboard de Flota**: Captura de Ventana de Terminal en pantalla completa (fondo oscuro). **Comando a ejecutar:** `python3 demo_rich_dashboard.py`.
3. **Arquitectura Interactiva**: *Browser Source* (1920x1080) apuntando a `file:///.../architecture_interactive.html`.
4. **Consola GCP**: Captura de Ventana del navegador con zoom al 125%. Pestañas abiertas: Cloud Run, Scheduler, KMS, Firestore.

### 1.4 Calibración de Audio
- [ ] **Micrófono:** Configurado a **-6 dB**.
- [ ] **Filtros OBS:** Supresión de ruido (RNNoise o Speex) activada.
- [ ] Realizar grabación de prueba de 15 segundos y verificar que el fondo esté en absoluto silencio al no hablar.

---

## 2. SECUENCIA DE GRABACIÓN (Cronometraje de 4 Minutos)

### Acto I: El Defecto y la Cola de Ingesta
#### Shot 0: Intro Animada (0:00 – 0:10)
- **Escena OBS:** Intro / Outro.
- **Voz:** *"Companies are about to run fleets of AI agents. When one acts, who authorized it?"*
- **Acción:** `[Fade a Dashboard]`

#### Shot 1: Dashboard de Ingesta (0:10 – 0:50)
- **Escena OBS:** Dashboard (`python3 demo_rich_dashboard.py`).
- **Voz:** *"Two days ago, in preproduction, we measured 58 closures signed 'human' — but a machine closed them. Cleveria does not trust — it proves. Each agent runs with its own service identity and a key limited to 'machine work'. When a decision involves judgement about a person, the flow stops deterministically and requires a human signature."*
- **Visual:** Se ve la terminal actualizando `PET-001` a `✓ SIGNED (Machine)` y `PET-002` deteniéndose en `⏸️ AWAITING HUMAN`.
- **Acción:** `[Fade a Diagrama Interactivo]`

### Acto II: La Flota en Acción y el Clímax 403
#### Shot 2: Diagrama de Arquitectura (0:50 – 1:30)
- **Escena OBS:** Arquitectura Interactiva.
- **Acción:** Hacer clic en "Trigger Cloud Run Simulation".
- **Voz:** *"Here is how it works: the commercial agent receives a voice note, transcribes it, and detects judgement. The curator agent closes operational tickets with evidence. But when liability is at stake, the human key is required — and the cloud enforces it."*
- **Visual:** La animación avanza mostrando el trigger, la pausa HITL, el rechazo en KMS (nodo rojo) y la firma humana final (nodo verde).
- **Acción:** `[Fade a Dashboard]`

#### Shot 3: El Momento del 403 (1:30 – 2:20)
- **Escena OBS:** Dashboard (Sección *Cloud KMS Enforcement* resaltada).
- **Voz:** *"This is the moment that wins the hackathon. The agent tries to sign with the human key. Google Cloud says no. HTTP 403. Not trust. Proof. It's not that the agent won't; it can't."*
- **Visual:** Panel verde `HTTP 200 OK` vs Panel rojo masivo `HTTP 403 PERMISSION_DENIED`.
- **Acción:** Dejar asimilar 5 segundos. `[Fade a Consola GCP]`

### Acto III: Evidencia Desnuda y Cierre
#### Shot 4: Verificación 100% Offline (2:20 – 2:40)
- **Escena OBS:** Dashboard (Sección *Audit Telemetry* resaltada).
- **Voz:** *"Our verifier imports nothing from Google. Zero network calls. And our semantic fence catches attacks in Spanish that vendor filters miss."*
- **Visual:** Métricas de 0 dependencias y 9/9 inyecciones capturadas.

#### Shot 5: Prueba de Infraestructura (2:40 – 3:20)
- **Escena OBS:** Consola GCP.
- **Voz:** *"Cloud Run, Cloud Scheduler, Cloud KMS with two asymmetric keys, and Firestore. All live, all verifiable."*
- **Acción:** Pasear tranquilamente por las 4 pestañas de Google Cloud.
- **Acción:** `[Fade a Intro / Outro]`

#### Shot 6: Cierre de Marca (3:20 – 3:40)
- **Escena OBS:** Intro / Outro.
- **Voz:** *"Cleveria, by Softronica — built for the All Things Agentic Hackathon. Because compliance facts are never paraphrased."*
- **Acción:** Detener Grabación.

---

## 3. PLAN B (CONTINGENCIAS TÉCNICAS)
- **Si el dashboard Rich falla (glitches ANSI):** Retroceder al `demo_rich.py` puro.
- **Si el Diagrama HTML no se captura bien:** Usar el render de `ARCHITECTURE.png` y narrar sobre la imagen estática.
- **Si la voz en vivo se enreda:** Grabar la captura visual primero (Video Mudo) y superponer el audio leyendo el guion en un editor de video después (Post-Dubbing).

---

## 4. POST-GRABACIÓN Y ENVÍO (DOMINGO / LUNES)
1. **Subtítulos (OBLIGATORIO):** 
   - Ejecutar: `python3 -m whisper video_final.mp4 --model large-v3 --language en --output_format srt`.
   - Revisar tiempos y corregir términos (ej: KMS, IAM, Firestore).
2. **Subida a Plataforma:** YouTube o Vimeo (Visibilidad Pública). Título recomendado: *Cleveria — Governing Enterprise Agent Fleets*.
3. **Ensamblaje Devpost:** Pegar el contenido íntegro de `DEVPOST_SUBMISSION.md` antes del Lunes a las 16:00 COT.
