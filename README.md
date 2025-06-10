# Prototipo Web - Rama `celery`

Esta es la rama dedicada a la integración y ejecución de las tareas asíncronas mediante **Celery**.

## Requisitos previos

Antes de comenzar, asegúrate de tener instalados y configurados:

- **Python 3.13**
- **pip**
- Redis para ser broker y backend.
- Un entorno virtual de Python (recomendado).

## Instalación del proyecto

1. Clona la rama `celery` de tu repositorio:

   ```bash
   git checkout celery


2. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate    # Windows
   ```

3. Instala las dependencias del proyecto:

   ```bash
   pip install -r celery_requirements.txt
   ```

## Configuración inicial de modelos de PLN y dataset

Dentro de la carpeta `celeryBackend` se incluye un script fundamental:

1. **Descarga de modelos y dataset**

   Ve a la carpeta `celeryBackend` y ejecuta:

   ```bash
   python initSystem.py
   ```

   Este script se encarga de:

   * Descargar los modelos de PLN utilizados.
   * Obtener el dataset.
   * Realizar el preprocesamiento necesario.

## Ejecución de Celery

Tras completar los pasos anteriores, debes lanzar dos procesos de Celery:

1. **Worker**

   Abre una consola y ejecuta:

   ```bash
   celery -A task.celery_app worker --loglevel=info --concurrency=2 --pool=prefork
   ```

2. **Beat (Scheduler)**

   En otra consola, ejecuta:

   ```bash
   celery -A task.celery_app beat --loglevel=info
   ```

### Nota para usuarios de Windows

El pool `prefork` no es estable en Windows y puede generar errores. Tienes dos opciones:

* Ejecutar el worker en modo solo:

  ```bash
  celery -A task.celery_app worker --loglevel=info --concurrency=2 --pool=solo
  ```

* Dockerizar los procesos:

  1. Construye la imagen Docker:

     ```bash
     docker build -f celery.Dockerfile -t celery-app .
     ```
  2. Lanza los contenedores para **worker** y **beat**:

     ```bash
     docker run -d --name celery-worker celery-app celery -A task.celery_app worker --loglevel=info --concurrency=2 --prefetch-multiplier=1 --pool=prefork
     docker run -d --name celery-beat celery-app celery -A task.celery_app beat --loglevel=info
     ```

---

Con esto, tendrás tu entorno de Celery listo para generar las lecciones.

---

**English:**

# Web Prototype - `celery` Branch

This branch handles integration and execution of asynchronous tasks using **Celery**.

## Prerequisites

Before starting, ensure you have installed and configured:

- **Python 3.13**
- **pip**
- Redis (as broker and backend)
- Python virtual environment (recommended)

## Project Installation

1. Clone the `celery` branch:

   ```bash
   git checkout celery


2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate    # Windows
   ```

3. Install the project dependencies:

   ```bash
   pip install -r celery_requirements.txt
   ```

## Initial Setup
The  `celeryBackend` folder contains the following script:

   Go to the  `celeryBackend` folder and run:

   ```bash
   python initSystem.py
   ```

   This script handles:

   * Downloading the NLP models.
   * Download the dataset
   * Perfoming necessary preprocessing.

## How to run

1. **Worker**

  launch two celery processes (one terminal each):
   ```bash
   celery -A task.celery_app worker --loglevel=info --concurrency=2 --pool=prefork
   ```

2. **Beat (Scheduler)**

   ```bash
   celery -A task.celery_app beat --loglevel=info
   ```

### For windows users

The `prefork` pool isn´t stable on Windows and may cause errors. You hace two options:

* Run celery in solo mode:

  ```bash
  celery -A task.celery_app worker --loglevel=info --concurrency=2 --pool=solo
  ```

* Dockerize the processes:

  1. Build a Docker image:

     ```bash
     docker build -f celery.Dockerfile -t celery-app .
     ```
  2. Launch containers for worker and beat:

     ```bash
     docker run -d --name celery-worker celery-app celery -A task.celery_app worker --loglevel=info --concurrency=2 --prefetch-multiplier=1 --pool=prefork
     docker run -d --name celery-beat celery-app celery -A task.celery_app beat --loglevel=info
     ```

---

Enjoy.



