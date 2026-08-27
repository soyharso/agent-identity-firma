FROM python:3.12-slim
WORKDIR /app
COPY servicio/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY agente/ ./agente/
COPY claves/ ./claves/
COPY libro/peticiones.json ./libro/peticiones.json
COPY servicio/main.py ./main.py
ENV PORT=8080 PYTHONUNBUFFERED=1
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 300 main:app
