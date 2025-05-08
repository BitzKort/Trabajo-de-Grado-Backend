FROM python:3.13-slim

WORKDIR /fastapi

ENV PYTHONPATH=/fastapi
# Copiar requirements primero para cachear dependencias
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

EXPOSE 8000