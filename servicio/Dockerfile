FROM python:3.12-slim
WORKDIR /app
COPY servicio/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY agente/ ./agente/
COPY libro/peticiones.json ./libro/peticiones.json
# El directorio de claves PÚBLICAS: es lo que el verificador usa para saber qué clave firmó y
# qué estados puede autorizar. Sin él, /decidir revienta con 500 al comprobar la firma humana.
# Faltaba porque este Dockerfile no se usaba: se desplegaba con `--source .`, que toma el
# Dockerfile de la raíz. Aquí no hay ninguna clave privada — esas viven en Cloud KMS y el
# servicio no las alcanza, que es el producto entero.
COPY claves/ ./claves/
COPY servicio/main.py ./main.py
COPY servicio/identidad.py ./identidad.py
COPY servicio/mediador.py ./mediador.py
ENV PORT=8080 PYTHONUNBUFFERED=1 APP_MODULO=main
# UNA imagen, DOS servicios. `main` es el agente; `mediador` es el único que puede escribir el
# registro. Lo que los separa no es el código: es la identidad con la que Cloud Run los corre y
# el permiso que esa identidad tiene sobre Firestore.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 300 ${APP_MODULO}:app
