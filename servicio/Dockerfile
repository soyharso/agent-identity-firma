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
ENV PORT=8080 PYTHONUNBUFFERED=1
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 300 main:app
