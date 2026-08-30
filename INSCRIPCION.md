# Inscripción paso a paso

**Cierre: 31 de agosto de 2026, 17:00 hora del Pacífico = 19:00 en Colombia.**

Todo lo de aquí es acto del operador. Cada paso trae el comando o el enlace exacto, y qué
comprobar después para saber que salió bien.

> **Lo que más importa del reglamento, leído el 2026-08-30:**
> *«Judges aren't required to download or run your project. They may score entirely from your
> video, your text description, and your repo.»*
>
> Los jueces pueden puntuar **sin ejecutar nada**. El vídeo, la descripción y el repositorio son
> todo lo que hay. Lo que no se vea ahí, no existe.

---

## 0 · Antes de nada (5 min)

```bash
gcloud auth print-identity-token | head -c 20   # debe devolver algo
cd ~/Desarrollos/agent-identity-firma
./pruebas_de_ruptura.sh                          # ~2½ min, deja el resumen listo
python3 sembrar_demo.py --borrar && python3 sembrar_demo.py
```

Y **comprueba con tus ojos** que la toma 3 no enseña tu correo:

```bash
bash demo.sh 3 --sin-pausa | grep '"by"'
# debe decir "a person at softronica.com.co", NUNCA tu correo completo
```

---

## 1 · Compartir el repositorio (3 min)

El repositorio es privado, y las reglas lo admiten **con acceso concedido**.

> https://github.com/soyharso/agent-identity-firma/settings/access

**Add people** → añade los dos correos, con permiso de lectura:

- `testing@devpost.com`
- `cloudhackathons@google.com`

**Comprueba** que aparecen como invitados pendientes o colaboradores. Si `gh` te deja invitarlos
por nombre de usuario, mejor; por correo hay que hacerlo desde la web.

---

## 2 · La descripción del repositorio (1 min)

Hoy dice que esto es «sujeto de un experimento medido sobre el método», y un jurado lo lee antes
que nada.

```bash
gh repo edit soyharso/agent-identity-firma \
  --description "An agent can work, but cannot sign as a person. Cryptographic authority boundary for enterprise agent fleets on Google Cloud (KMS, Cloud Run, Firestore, ADK, Gemini)."
```

---

## 3 · Grabar (la partida grande)

El orden y las escenas están en [`RUNBOOK_GRABACION.md`](./RUNBOOK_GRABACION.md). Lo esencial:
**graba primero la toma 3**, de una sola pasada, cuando la máquina esté fresca.

---

## 4 · Subir el vídeo (30 min, y no lo dejes para el final)

Los organizadores avisan: YouTube y Vimeo tardan **«desde unos minutos hasta varias horas»** en
procesar. Súbelo con margen.

- **Público**, no «no listado»
- **4:00 o menos** — solo se evalúan los primeros cuatro minutos
- **En inglés**, o con subtítulos en inglés
- Comprueba que se ve el backend corriendo en Google Cloud

---

## 5 · Rellenar Devpost (20 min)

Todo el texto está listo en [`DEVPOST_SUBMISSION.md`](./DEVPOST_SUBMISSION.md). Copia y pega:

| Campo de Devpost | De dónde sale |
|---|---|
| Project name y tagline | primeras líneas |
| Elevator pitch | *Short Description* |
| Descripción larga | *The «Unlikely Hero»* + *What We Built* + *Fleet Capabilities Coverage* |
| Google technologies | *Google Technologies Used* |
| **Bonus contributions** | la sección **Bonus Contributions** — **no la saltes, son hasta 0,6 puntos** |
| Repositorio | `https://github.com/soyharso/agent-identity-firma` |
| Vídeo | el enlace de YouTube o Vimeo |
| Hosted app | el portal y el libro de autoridad |

**Vía de premio**: Startup Excellence, a nombre de Softrónica S.A.S. Exige declarar organización
constituida y correo corporativo. **Los tienes; hay que declararlo al inscribir.**

---

## 6 · Comprobación final antes de darle a enviar

- [ ] El vídeo dura 4:00 o menos y está **público**
- [ ] Está en inglés o lleva subtítulos en inglés
- [ ] Se ve el backend corriendo en Google Cloud
- [ ] **No aparece ningún correo, ruta personal ni nombre de cliente** en ningún fotograma
- [ ] El repositorio está compartido con los dos correos
- [ ] La descripción del repositorio es la nueva
- [ ] La sección de bonificación está rellenada en Devpost
- [ ] El diagrama de arquitectura se ve en la portada del repositorio
- [ ] Enviado **antes** de las 17:00 hora del Pacífico

---

## Opcional · Una dirección de marca para el demo

Hoy `cleveria.co` sirve una página de «Próximamente» de Squarespace, y **su correo de Google
depende de esa misma zona** — por eso no se toca la raíz ni los registros de correo.

Lo seguro es **añadir un subdominio nuevo**, que no toca nada de lo anterior y se borra en un
clic. Desde el panel de Cloudflare, o con este comando:

```bash
export CF_TOKEN="$(getsecret CloudflareDNSToken)"
curl -s -X POST \
  -H "Authorization: Bearer $CF_TOKEN" -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/zones/67af78b6.../dns_records" \
  --data '{"type":"CNAME","name":"demo",
           "content":"cleveria-demo-141981963817.us-central1.run.app",
           "proxied":true,"comment":"demo hackathon — reversible"}'
```

(el identificador de zona completo sale de
`curl -H "Authorization: Bearer $CF_TOKEN" "https://api.cloudflare.com/client/v4/zones?name=cleveria.co"`)

**Y luego compruébalo**, porque puede no bastar:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://demo.cleveria.co/ui/portal
```

Si devuelve **404**, es que Cloud Run no reconoce ese nombre de dominio: hay que mapearlo en
Cloud Run —lo que exige verificar el dominio en Search Console— o poner una regla de redirección
en Cloudflare hacia la dirección `.run.app`.

**Esto es opcional y no bloquea la entrega.** Las direcciones que ya funcionan sirven, y una
dirección alojada es opcional según las reglas. Si a estas alturas da guerra, déjalo.
