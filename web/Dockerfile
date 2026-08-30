# El servicio que recibe el formulario de cleveria.co. Nada más: la página es estática y la
# sirve Firebase Hosting; aquí solo entra un POST cada vez que alguien escribe.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app_web.py .
ENV PORT=8080 PYTHONUNBUFFERED=1
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 60 app_web:app
