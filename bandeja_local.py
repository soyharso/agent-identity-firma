#!/usr/bin/env python3
"""La bandeja humana, servida DESDE LA MÁQUINA DE LA PERSONA.

POR QUÉ EXISTE ESTE ARCHIVO, que es lo único que hay que entender aquí.

La misma pantalla —`assets/slides/ui_bandeja_humana.html`, byte por byte la misma— se sirve
desde dos sitios, y no se comporta igual:

  · servida por Cloud Run, corre con la identidad del agente (`sa-agente-curador`). Esa
    identidad NO tiene permiso sobre la clave de la persona en Cloud KMS: pedirla devuelve
    403 PERMISSION_DENIED. Así que allí la bandeja es de solo lectura y lo dice en pantalla.
  · servida por este programa, corre en el portátil de quien decide, con SU credencial. Aquí
    la clave sí responde, y por eso aquí —y solo aquí— aparecen el selector y el botón.

Esa diferencia no debilita el argumento del proyecto: es el argumento. La distancia entre
leer el caso y poder firmarlo es una frontera de permisos real, y este programa la hace
visible sin contarla: se ve porque una pantalla tiene botón y la otra no.

CÓMO SE MANTIENE HONESTO. Este servidor no firma. Ni siquiera sabe firmar: para cada
decisión ejecuta `src/decidir_como_persona.py`, que es el flujo que ya existía y el mismo
comando que la bandeja de solo lectura enseña en cada fila. Si mañana alguien moviera este
proceso a un servidor, el subproceso pediría igual la clave humana a Cloud KMS y recibiría el
mismo 403 — no hay ningún camino en este archivo por el que la firma pueda nacer en otro
sitio que no sea la máquina donde corre.

Uso:
    python3 bandeja_local.py            # http://localhost:8800/
"""
import ast
import json
import pathlib
import re
import subprocess
import sys

import requests
from flask import Flask, Response, jsonify, request, send_file

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

PAGINA = RAIZ / "assets" / "slides" / "ui_bandeja_humana.html"
DIRECTORIO = RAIZ / "claves" / "directorio.json"
DECIDIR = RAIZ / "src" / "decidir_como_persona.py"
# Dos archivos que esta bandeja LEE pero no reimplementa. Ver `aceptadas_por_el_servicio` y
# `marcas_de_juicio`: la lista se saca del código que manda, nunca se vuelve a teclear aquí.
PUERTA_SERVICIO = RAIZ / "servicio" / "main.py"
GRAFO = RAIZ / "agente" / "grafo.py"

# El registro durable vive en la nube y lo publica el servicio de la demostración. Esta
# bandeja NO tiene datos propios ni los inventa: lee de ahí y hace de intermediaria para que
# el navegador no choque contra CORS. Si esa lectura falla, se dice; no se rellena.
BACKEND = "https://demo.cleveria.co/api/auditoria_datos"

PUERTO = 8800

app = Flask(__name__)


# ── QUIÉN ES LA PERSONA Y QUÉ PUEDE AUTORIZAR ────────────────────────────────────────────
# El catálogo de decisiones no se teclea aquí: se lee del directorio de claves, que es la
# única compuerta de política del verificador. Escribir la lista a mano en dos sitios es
# tener dos formas de equivocarse, y la que se vería en cámara sería la falsa.
def decisiones_de_la_persona() -> list:
    d = json.loads(DIRECTORIO.read_text())
    return list(d["claves"]["persona-operador"]["alcance_permitido"])


def aceptadas_por_el_servicio() -> list:
    """Qué decisiones acepta de verdad la puerta `/decidir` del servicio desplegado.

    NO es lo mismo que el alcance de la clave. El directorio le permite a la persona cinco
    estados; la puerta desplegada solo admite tres —`cerrada`, `descartada` y `no`— y a los
    demás les contesta HTTP 400 sin llegar a mirar la firma. Ofrecer en el selector un estado
    que el servicio va a rechazar es preparar un error delante de la cámara.

    La lista se saca del ÁRBOL SINTÁCTICO de `servicio/main.py`, que es el archivo que se
    despliega, en vez de volver a teclearla aquí: dos copias de una lista son dos formas de
    equivocarse, y la que se vería en pantalla sería la falsa. Si el archivo cambia de forma y
    no se reconoce, se devuelve `None` y la pantalla lo dice — no se adivina.
    """
    try:
        arbol = ast.parse(PUERTA_SERVICIO.read_text())
    except Exception:                                             # noqa: BLE001
        return None
    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Compare) or not nodo.ops:
            continue
        if not isinstance(nodo.ops[0], ast.NotIn):
            continue
        derecha = nodo.comparators[0]
        if not isinstance(derecha, (ast.Tuple, ast.List, ast.Set)):
            continue
        valores = [e.value for e in derecha.elts
                   if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        # La firma de la puerta humana: contiene los dos estados y la negativa.
        if {"cerrada", "descartada", "no"} <= set(valores):
            # `no` no es una decisión que se firme: es la negativa, y no tiene sitio en un
            # selector cuyo botón firma. Se deja fuera aquí y no en la pantalla.
            return [v for v in valores if v != "no"]
    return None


def marcas_de_juicio() -> list:
    """Las marcas de texto con las que el TECHO DE AUTORIDAD decide que hace falta una persona.

    Es lo único de «por qué se detuvo este caso» que se puede saber con certeza, porque el
    techo es determinista: no lo decide un modelo, lo decide `techo_de_autoridad` mirando si el
    texto contiene alguna de estas raíces. El registro durable NO guarda esa razón —el sobre
    firmado solo lleva el estado— así que la pantalla la recalcula con ESTA MISMA lista y lo
    dice en pantalla: calculado aquí, no leído del registro.

    Se lee por árbol sintáctico, sin importar `agente.grafo`, que arrastra el agente entero.
    """
    try:
        arbol = ast.parse(GRAFO.read_text())
    except Exception:                                             # noqa: BLE001
        return None
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "MARCAS_DE_JUICIO" for t in nodo.targets):
            if isinstance(nodo.value, (ast.Tuple, ast.List)):
                return [e.value for e in nodo.value.elts
                        if isinstance(e, ast.Constant) and isinstance(e.value, str)]
    return None


def sesion_activa() -> dict:
    """QUIÉN sostiene esta pantalla. No se autentica a nadie: se LEE una sesión que ya existe.

    Aquí no hay ni habrá un inicio de sesión propio —ni formulario, ni OAuth, ni usuarios—, y no
    por pereza: toda la tesis del proyecto es que la autoridad la da la infraestructura y no el
    software. Un login escrito por nosotros sería exactamente el control blando que esto rechaza,
    y encima sería el que un jurado sabe saltarse. La sesión de Google YA es el login: es la que
    Cloud KMS acepta o rechaza tres funciones más abajo, y es la única que decide si esta máquina
    puede firmar. Lo que se añade es enseñarla.

    Y se enseña A MEDIAS, a propósito. El vídeo es público y en él no entra un correo personal.
    La regla ya está sellada en `servicio/main.py` —el servicio devuelve el dominio de quien
    llamó y no su correo, «dice lo mismo sin poner un correo personal en cámara»— y aquí se
    repite: `dominio` es lo que la pantalla pinta, `cuenta` viaja en el JSON local para depurar
    y no se pinta nunca. La identidad completa sigue dentro del sobre firmado, que es donde
    tiene que estar para poder auditar.
    """
    try:
        p = subprocess.run(["gcloud", "auth", "list", "--filter=status:ACTIVE",
                            "--format=value(account)"],
                           capture_output=True, text=True, timeout=30)
        cuenta = (p.stdout or "").strip().splitlines()
        cuenta = cuenta[0].strip() if cuenta else ""
    except Exception as e:                                        # noqa: BLE001
        return {"cuenta": None, "dominio": None,
                "motivo": f"could not read the active session: {type(e).__name__}: {e}"}
    if not cuenta:
        # Sin sesión activa no se inventa una. Que la pantalla lo diga es mejor que un nombre
        # de relleno, que en cámara es indistinguible de uno real.
        return {"cuenta": None, "dominio": None,
                "motivo": "gcloud reports no active account on this machine"}
    return {"cuenta": cuenta,
            "dominio": cuenta.split("@")[-1] if "@" in cuenta else cuenta,
            "motivo": "read from the active gcloud session on this machine"}


# Se lee UNA vez al arrancar, por lo mismo que la sonda de KMS: es la misma sesión durante toda
# la grabación, y llamar a `gcloud` en cada latido del reloj de la pantalla sería pagar un
# proceso por segundo para que conteste siempre lo mismo.
_SESION = None


def sesion():
    global _SESION
    if _SESION is None:
        _SESION = sesion_activa()
    return _SESION


def sondear_clave_humana() -> dict:
    """¿Puede ESTA máquina firmar como la persona? Se le pregunta a la nube, no a un archivo.

    La sonda es una firma de verdad sobre un sobre de usar y tirar, con la misma función que
    usa el flujo real. No se presenta a nadie ni se registra en ningún sitio: solo sirve para
    que la nube conteste 200 o 403. Preguntarlo de otra manera —por el nombre del host, por
    una variable de entorno— sería adivinar; esto es la respuesta de quien manda.
    """
    try:
        from src.firma_kms import CLAVE_HUMANO, firmar
        r = firmar(CLAVE_HUMANO, {"peticion_id": "SONDA-ARRANQUE",
                                  "estado_destino": "descartada",
                                  "tipo_firmante": "HUMANO",
                                  "hash_contenido": "sha256:sonda",
                                  "marca_temporal": 0,
                                  "algoritmo": "EC_SIGN_P256_SHA256"})
        if r.get("http") == 200:
            return {"puede": True, "http": 200,
                    "motivo": "Cloud KMS accepted a signature with the human key from this "
                              "machine's credential."}
        return {"puede": False, "http": r.get("http"),
                "motivo": f"Cloud KMS refused the human key: {r.get('error')} "
                          f"{r.get('mensaje', '')}".strip()}
    except Exception as e:                                        # noqa: BLE001
        return {"puede": False, "http": None,
                "motivo": f"no credential available on this machine: {type(e).__name__}: {e}"}


# La sonda se hace UNA vez, al arrancar, y no en cada carga de la página: la respuesta no
# cambia mientras el proceso vive, y preguntarlo cada tres segundos sería gastar una llamada
# a la nube por cada latido del reloj de la pantalla.
_SONDA = None


def sonda():
    global _SONDA
    if _SONDA is None:
        _SONDA = sondear_clave_humana()
    return _SONDA


# ── LAS ENTRADAS ─────────────────────────────────────────────────────────────────────────
@app.get("/")
def pagina():
    """La MISMA pantalla que sirve Cloud Run. No hay una copia local con botones añadidos:
    hay un archivo, y es el que ambos lados sirven. Si hubiera dos, la comparación que este
    proyecto pone en cámara dejaría de probar nada."""
    return send_file(PAGINA)


@app.get("/ui/<path:nombre>")
def marca(nombre):
    """La página pide su logotipo por la misma ruta en los dos sitios. Aquí se sirve del
    repositorio, para que la pantalla local no dependa de la red para verse entera."""
    rutas = {"qnowa-logo.svg": ("assets/qnowa/qnowa-logo.svg", "image/svg+xml"),
             "qnowa-mark.svg": ("assets/qnowa/qnowa-mark.svg", "image/svg+xml")}
    if nombre not in rutas:
        return "UI no encontrada", 404
    ruta, mime = rutas[nombre]
    return send_file(RAIZ / ruta, mimetype=mime)


@app.get("/api/puede_firmar")
def api_puede_firmar():
    """Lo que distingue un sitio del otro, y lo declara el SERVIDOR, no el navegador.

    Mirar el nombre del host desde la página sería una conjetura disfrazada: `localhost`
    puede ser cualquier cosa, y un túnel la volvería mentira. Quien sabe si hay credencial
    humana es quien la tiene delante. En Cloud Run esta entrada no existe —el servicio de la
    demostración no la define— y la página recibe un 404, que es exactamente la respuesta
    correcta: allí no se puede firmar.
    """
    s = sonda()
    ses = sesion()
    return jsonify({"puede_firmar": s["puede"],
                    "motivo": s["motivo"],
                    "kms_http": s["http"],
                    "servido_desde": "esta máquina · credencial de la persona",
                    # `dominio` es lo ÚNICO que la pantalla pinta. `cuenta` va aquí para poder
                    # depurar desde la consola local; si algún día alguien la pinta, estará
                    # rompiendo la misma regla que `servicio/main.py` ya sella.
                    "dominio": ses["dominio"],
                    "cuenta": ses["cuenta"],
                    "sesion_motivo": ses["motivo"],
                    "decisiones": decisiones_de_la_persona(),
                    # Lo que la CLAVE permite y lo que la PUERTA acepta son dos cosas, y la
                    # diferencia se ve en el selector: los estados que el servicio rechaza
                    # salen deshabilitados y con el motivo, en vez de fallar en cámara.
                    "aceptadas_por_el_servicio": aceptadas_por_el_servicio(),
                    "marcas_de_juicio": marcas_de_juicio(),
                    "comando": "python3 src/decidir_como_persona.py"})


@app.get("/api/auditoria_datos")
def api_datos():
    """Intermediaria del registro durable. Devuelve lo que el backend conteste, tal cual.

    Existe solo por CORS: el navegador no deja que una página servida en localhost lea
    directamente demo.cleveria.co. No se filtra, no se ordena, no se completa nada — la
    pantalla tiene que pintar los mismos datos aquí que allí, o la comparación no vale.
    """
    try:
        r = requests.get(BACKEND, timeout=25)
        return Response(r.content, status=r.status_code,
                        mimetype=r.headers.get("Content-Type", "application/json"))
    except Exception as e:                                        # noqa: BLE001
        # No hay datos de repuesto. Una bandeja que enseña casos viejos cuando el registro no
        # contesta es indistinguible en cámara de una que mide, y este producto existe para
        # hacer visible esa diferencia.
        return jsonify({"error": f"the backend did not answer: {type(e).__name__}: {e}",
                        "backend": BACKEND}), 502


@app.post("/firmar")
def api_firmar():
    """El botón. Ejecuta el flujo humano que ya existe, sin reimplementar ni un paso.

    Se invoca `src/decidir_como_persona.py` como subproceso, y no se importan sus funciones,
    por dos razones que apuntan al mismo sitio: es literalmente el comando que la bandeja de
    solo lectura muestra en cada fila —lo que se ve en pantalla es lo que se ejecuta—, y deja
    la firma en un proceso cuyo único origen de credencial es esta máquina. Aquí no hay una
    segunda ruta de firma que pudiera algún día correr en otro sitio: hay una, y es la de
    siempre.

    Se devuelve la salida COMPLETA del subproceso, incluido el fallo. Si el servicio contesta
    un error, ese error es el resultado y se enseña.
    """
    cuerpo = request.get_json(silent=True) or {}
    pid = str(cuerpo.get("peticion_id", "")).strip()
    estado = str(cuerpo.get("estado", "")).strip().lower()

    if not pid:
        return jsonify({"ok": False, "salida": "peticion_id is required"}), 400
    # El alcance se comprueba contra el directorio, no contra una lista de esta función. Es un
    # filtro de cortesía, no la garantía: la garantía la da el verificador del servicio, que
    # rechaza el sobre aunque este programa se equivoque.
    permitidas = decisiones_de_la_persona()
    if estado not in permitidas:
        return jsonify({"ok": False,
                        "salida": f"'{estado}' is outside the person's scope {permitidas}"}), 400

    p = subprocess.run([sys.executable, str(DECIDIR), pid, estado],
                       cwd=str(RAIZ), capture_output=True, text=True, timeout=180)
    salida = (p.stdout + p.stderr).strip()

    # Se rescata del texto lo que contestó el servicio, para que la pantalla pueda saber si la
    # decisión quedó ANOTADA y no solo si el comando terminó bien. Son cosas distintas: un
    # sobre rechazado por el verificador también «termina», y con código de salida 1.
    http = None
    registrado = False
    m = re.search(r"the service replied HTTP (\d+): (.*)", salida, re.S)
    if m:
        http = int(m.group(1))
        try:
            registrado = bool(json.loads(m.group(2)).get("recorded"))
        except Exception:                                        # noqa: BLE001
            registrado = False

    return jsonify({"ok": p.returncode == 0,
                    "codigo_salida": p.returncode,
                    "servicio_http": http,
                    "registrado": registrado,
                    "peticion_id": pid,
                    "estado": estado,
                    "comando": f"python3 src/decidir_como_persona.py {pid} {estado}",
                    "salida": salida}), 200


def anunciar():
    """Lo primero que se lee en la consola es si esta máquina puede firmar o no. Arrancar sin
    saberlo llevaría a descubrirlo delante de la cámara, con un caso real de por medio."""
    s = sonda()
    ses = sesion()
    print()
    print("  Bandeja humana — servida desde ESTA máquina")
    print(f"  sesión activa: {ses['cuenta'] or '(ninguna) — ' + ses['motivo']}")
    print(f"  en pantalla se verá solo el dominio: {ses['dominio'] or '—'}")
    print(f"  http://localhost:{PUERTO}/")
    print(f"  datos: {BACKEND}")
    print()
    if s["puede"]:
        print("  ✓ HAY CREDENCIAL HUMANA. Cloud KMS firmó con la clave de la persona (HTTP 200).")
        print(f"    Alcance de la clave (directorio): {', '.join(decisiones_de_la_persona())}")
        acep = aceptadas_por_el_servicio()
        print(f"    Acepta la puerta desplegada:      {', '.join(acep) if acep else 'no se pudo leer de servicio/main.py'}")
        print("    La pantalla mostrará selector y botón de firma.")
    else:
        print(f"  ✗ SIN CREDENCIAL HUMANA (KMS HTTP {s['http']}).")
        print(f"    {s['motivo']}")
        print("    La pantalla será de SOLO LECTURA, igual que la servida por Cloud Run.")
        print("    Si esto no es lo que esperabas: gcloud auth application-default login")
    print()


if __name__ == "__main__":
    anunciar()
    # `debug=False` a propósito: el recargador levanta dos procesos y sondaría KMS dos veces,
    # y en una grabación un servidor que se reinicia solo es un riesgo sin ninguna ventaja.
    app.run(host="127.0.0.1", port=PUERTO, debug=False)
