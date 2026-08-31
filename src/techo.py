r"""El techo de autoridad: cuánto puede la máquina sobre un texto, decidido sin modelo.

POR QUÉ VIVE AQUÍ Y NO EN `agente/grafo.py`, que es donde nació. La puerta de entrada del
portal (`/api/inbound`) tiene que aplicar EL MISMO techo que el agente, y `grafo.py` no se
puede importar desde el servicio web: arrastra el motor de agentes de Google entero. La salida
fácil era copiar la lista de marcas en el servicio. Copiarla es lo peor que se podía hacer:
serían dos techos que empiezan iguales y divergen al primer cambio, y el producto entero
sostiene que la garantía no depende de dónde se ejecute. Así que se mueve, y quien la quiera
la importa. `agente/grafo.py` la reexporta, de modo que los kill-tests que hacen
`from grafo import techo_de_autoridad` siguen valiendo.

Búsqueda previa (C1): `grep -rn 'MARCAS_DE_JUICIO\|techo_de_autoridad' --include='*.py'` solo
devolvía `agente/grafo.py` (definición) y los kill-tests `killtest_inyeccion.py` y
`killtest_voz.py`, que la importan de ahí. `src/cerco_semantico.py` es OTRA cosa —el techo
semántico por embeddings, la segunda capa— y no contiene esta lista.
"""

# Marcas de que hay un juicio de por medio. La lista es tonta a propósito: no razona, así que
# no hay nada que engañar. Un texto envenenado no puede convencerla de nada.
MARCAS_DE_JUICIO = (
    # español
    "descart", "absol", "absuelv", "absuelt", "exculp", "exime", "exim",
    "perdon", "culpa", "sanci", "multa", "reclam", "queja", "cliente",
    "denuncia", "despido", "indemniz", "no amerita", "no vale la pena",
    "caso límite", "caso limite", "ya no importa", "no parece importante",
    # inglés: las reglas del concurso exigen que la aplicación soporte inglés, y sin estas
    # marcas «Dismissing the customer complaint» o «the fine is waived» pasaban LIMPIAS.
    # Medido antes de añadirlas: dos de tres casos de juicio en inglés se colaban.
    "dismiss", "absolv", "exonerat", "waive", "forgiv", "pardon", "blame",
    "fault", "penalt", "fine", "complaint", "claim", "customer", "client",
    "dispute", "grievance", "layoff", "termination", "compensat",
    "not worth", "no longer matters", "doesn't matter", "does not matter",
    "edge case", "minor issue", "no action needed",
)
# `absuelv` está aquí porque el kill-test lo cazó: «absuelve» NO contiene «absol». Una lista de
# raíces se rompe por una conjugación, y por eso el kill-test corre en cada cambio. Lo que la
# lista da es superficie de ataque más pequeña, no una garantía: la garantía está más abajo.


def techo_de_autoridad(texto: str) -> str:
    """Cuánta autoridad puede tener la máquina sobre ESTE texto, decidido sin modelo.

    Es el arreglo del agujero que la fase cero encontró en la promesa central: si el techo lo
    fijara el modelo, un texto envenenado podría subirlo. Aquí lo fija una función, y el modelo
    solo puede REBAJARLO.
    """
    t = (texto or "").lower()
    return "exige_humano" if any(m in t for m in MARCAS_DE_JUICIO) else "cerrada"
