# Prototipo Web - Rama `fastapiServer`

Esta rama contiene el servidor web construido con **FastAPI**.

## Requisitos previos

- **Python 3.13**
- **pip**
- Un entorno virtual de Python (recomendado).
- Redis (la misma instancia que se utiliza con celery).

## Instalación del proyecto

1. Cambia a la rama `fastapiServer`:

   ```bash
   git checkout fastapiServer

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\\Scripts\\activate    # Windows
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Configuración inicial del modelo

Dentro de la carpeta `fastAPI` encontrarás el script **initServerModel.py**. Este script se encarga de descargar el modelo `cross-encoder/stsb-roberta-base` para la comparación de oraciones:

```bash
cd fastAPI
python initServerModel.py
```

Al ejecutarlo, se descargan y configuran:

* El modelo `cross-encoder/stsb-roberta-base`.
* Las dependencias asociadas.

## Ejecución del servidor

Con el modelo listo, inicia el servidor con Uvicorn:

```bash
python -m uvicorn main:app --reload
```

Esto arrancará FastAPI en [http://localhost:8000](http://localhost:8000) con recarga automática durante el desarrollo.

## Dockerización (opcional)

Para simplificar el despliegue, puedes crear una imagen Docker usando el `Dockerfile` por defecto en la raíz de la rama:

1. Construye la imagen:

   ```bash
      docker build -f Dockerfile -t fastapi-app .
   ```

2. Lanza el contenedor:

   ```bash
   docker run -d \
     --name fastapi-server \
     -p 8000:8000 \
     fastapi-app
   ```

Esto expondrá tu servidor FastAPI en el puerto 8000 de tu máquina.

---

**English:**

# Web Prototype - `fastapi-server` Branch

This branch contains the web server built with **FastAPI**.

## Prerequisites

- **Python 3.13**
- **pip**
- A Python virtual environment (recommended).
- Redis (the same instance used with Celery).

## Project Installation

1. Switch to the `fastapiServer` branch:

   ```bash
   git checkout fastapiServer
   
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\\Scripts\\activate    # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Initial Model Setup

Inside the `fastAPI` folder, you'll find the **initServerModel.py** script. This script downloads the `cross-encoder/stsb-roberta-base` model for sentences comparison:

```bash
cd fastAPI
python initServerModel.py
```

When executed, it downloads and sets up:

* the `cross-encoder/stsb-roberta-base` model.
* All the dependencies.

## How to run.

Start the server with:

```bash
python -m uvicorn main:app --reload
```
This will run fastAPI at [http://localhost:8000](http://localhost:8000) woth automatic reloading development.

## Dockerization (Optional)

1. Build the image:

   ```bash
      docker build -f Dockerfile -t fastapi-app .
   ```

2. Run de container:

   ```bash
   docker run -d \
     --name fastapi-server \
     -p 8000:8000 \
     fastapi-app
   ```

This will expose the server on the port 8000 of your machine.
