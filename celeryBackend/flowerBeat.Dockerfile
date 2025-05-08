FROM python:3.13-slim

# Establece el directorio de trabajo
WORKDIR /flower_beat

# Copia los archivos de requisitos e instala las dependencias
COPY ./flowerBeat_requirements.txt .
RUN pip install --no-cache-dir -r flowerBeat_requirements.txt

# Copia el resto del código de la aplicación
COPY task/ ./task

