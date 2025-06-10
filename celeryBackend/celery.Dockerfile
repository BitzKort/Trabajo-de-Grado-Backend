FROM python:3.13-slim

# Establece el directorio de trabajo
WORKDIR /celery_app

ENV PYTHONPATH=/celery_app
# Copia los archivos de requisitos e instala las dependencias


RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./celery_requirements.txt .
RUN pip install --no-cache-dir -r celery_requirements.txt

# Copia el resto del código de la aplicación
COPY . .
