# Runbook de Grabación y Checklist Técnico — All Things Agentic Hackathon

**Entorno de Grabación:** Fedora Linux (Wayland / GNOME)  
**Herramientas:** OBS Studio (o Kooha como backup) + PipeWire + terminal configurada  
**Restricción Dura:** Vídeo ≤ 4:00 minutos (solo se juzgan los primeros 4 minutos)  
**Objetivo de Fecha:** Grabación Domingo 30 de Agosto (13:00 – 17:00 COT)  

---

## 1. Checklist Técnico Prevuelo (Domingo 12:30 COT)

- [ ] **Servicio Cloud Run "caliente"**:
  - Ejecutar un curl previo para evitar *cold start* en la toma:
    ```bash
    curl -s -X POST "https://candado-firma-141981963817.us-central1.run.app/despertar"
    ```
- [ ] **Terminal de Grabación**:
  - Fuente monospace limpia (JetBrains Mono / Fira Code) a tamaño **24–28 pt**.
  - Tema de alto contraste (fondo oscuro puro, texto blanco/azul/verde claro).
  - Variable `PS1` limpia (sin rutas largas que ocupen media pantalla).
- [ ] **Navegador Web (Pestañas en orden)**:
  - Zoom al **125% o 150%** para legibilidad en 1080p.
  - Barra de marcadores oculta y notificaciones del sistema desactivadas (`Do Not Disturb`).
  - Pestaña 1: Consola de Google Cloud Run (`candado-firma`, URL `.run.app` visible).
  - Pestaña 2: Consola de Cloud KMS (`keyRings/firmas` mostrando `clave-agente` vs `clave-humano`).
  - Pestaña 3: Consola de Cloud Firestore (colección de peticiones con documentos y firmas).
- [ ] **Audio & Micrófono**:
  - Micrófono configurado en PipeWire con filtro de cancelación de ruido activo.
  - Nivel de entrada calibrado a **-6 dB de pico** (sin saturar).
- [ ] **OBS Studio**:
  - Perfil de grabación: 1080p a 30 fps (formato MKV, remux automático a MP4).
  - Escenas preparadas:
    1. *Escena 1: Terminal Demo* (pantalla completa o terminal + cámara miniatura).
    2. *Escena 2: Consola GCP / Navegador* (Cloud Run + KMS + Firestore).
    3. *Escena 3: Diagrama de Arquitectura* (`ARCHITECTURE.png`).

---

## 2. Cronograma de las 5 Tomas del Vídeo (Presupuesto: 3:50 / 4:00)

| Timecode | Toma / Segmento | Qué se muestra | Frase Clave |
|---|---|---|---|
| **0:00 – 0:35** | **Shot 1: El Defecto Real** | Ledger / terminal con los 58 registros en preproducción. | *"Companies are about to run fleets of AI agents. When one acts, who authorized it? ... 58 closures signed 'human' closed by a machine."* |
| **0:35 – 1:30** | **Shot 2: Utilidad & Flota** | Cloud Scheduler + Firestore + audio waveform de WhatsApp. Tarea legítima completada. | *"A commercial agent does the work end to end... Spoken in WhatsApp. Modality changes; the key does not."* |
| **1:30 – 2:30** | **Shot 3: La que Gana (KMS 403)** | Terminal en vivo: `POST /intentar-suplantar` ➔ `HTTP 403 PERMISSION_DENIED`. | *"The cloud itself says no. Live. It's not that the agent won't; it can't."* |
| **2:30 – 3:20** | **Shot 4: Verificador & Ataque** | Verificador puro RFC 8785 offline + resultado 9/9 del cerco semántico (`gemini-embedding-001`). | *"Zero network, zero Google credentials... Anyone can re-verify every closure independently."* |
| **3:20 – 3:55** | **Shot 5: Prueba GCP & Cierre** | Consola Cloud Run con URL `.run.app` visible + Diagrama Fleet. | *"Cleveria isn't a brake — it is the license to scale... Because compliance facts are never paraphrased."* |

---

## 3. Matriz de Riesgos en Vivo y Mitigaciones ("Qué puede fallar y qué hacer")

| Riesgo / Fallo | Probabilidad | Impacto | Mitigación Inmediata |
|---|---|---|---|
| **Latencia / Cold Start en Cloud Run** | Media | Alto | Tirar 2 peticiones antes de grabar para que la instancia esté caliente. Si tarda >3s en responder, no cortar la toma en falso: regrabar ese segmento. |
| **Error de token OIDC expirado** | Baja | Medio | Generar token fresco antes de iniciar el bloque de terminal: `export TOK=$(gcloud auth print-identity-token)`. |
| **Saturación o ruido de fondo en el micro** | Media | Alto | Grabar una prueba de 10 segundos antes del ensayo y escucharla con auriculares. |
| **El 403 no se lee con claridad** | Baja | Crítico | Mantener la fuente a ≥26pt. Dejar el `HTTP 403 PERMISSION_DENIED` visible en pantalla durante al menos 4 segundos enteros. |
| **El tiempo se pasa de los 4:00 minutos** | Media | Crítico | El rubro descarta todo lo que supere el minuto 4:00. Si el ensayo da 4:05, recortar 10s de la explicación inicial de Shot 1, **nunca** de Shot 3 (el 403). |

---

## 4. Checklist Post-Grabación (Domingo Tarde)

- [ ] Generar subtítulos en inglés con `faster-whisper` local:
  ```bash
  whisper cleveria_demo.mp4 --model medium --language en --output_format srt
  ```
- [ ] Revisión humana línea a línea del archivo `.srt` (verificar términos técnicos: *Cloud KMS*, *Firestore*, *ADK*, *RFC 8785*).
- [ ] Subir vídeo a YouTube como **Público** (o *No listado* si las reglas lo permiten; se recomienda Público con `#AllThingsAgenticHackathon`).
- [ ] Verificar que la URL del vídeo reproduce en 1080p y que el audio es nítido.
- [ ] Respaldar el archivo de vídeo final (`cleveria_demo.mp4`) y subtítulos (`subtitles.srt`) en la carpeta `demo/` del repositorio.
