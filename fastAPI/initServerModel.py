import dotenv
import os
from loguru import logger
from sentence_transformers import CrossEncoder
from pathlib import Path


def checkout():

    """
        Método general para la descarga de los modelos de pln.
    
        Retorna
        -------
        boolean: True si ya paso mas de un dia, False si no.

        Excepciones
        -------
        - Excepciones dentro de los metodos del repositorio.
    """

    dotenv.load_dotenv(dotenv_path="../.env.dev")
    
    global stsb_path

    modules_path = os.getenv("MODULES_PATH")
    stsb_path = os.getenv("STSB_PATH")
     

    if not (Path(stsb_path).is_dir()):
         
        logger.warning("Algunas carpetas no fueron encontradas")
        init_Folders()
    
    else:
         logger.success("Listo para iniciar el servidor.")


def init_Folders():

    """
        Método para crear las carpetas de los modelos
    
        Retorna
        -------
        None
    """

    logger.warning("Creando carpetas para el modelo")

    dotenv.load_dotenv(dotenv_path=".env")

    modules_path = './nplModules'
    os.makedirs(modules_path, exist_ok=True)
    os.makedirs(stsb_path, exist_ok=True)

    logger.success("Carpetas creadas")

    init_models()


def init_models():

    """
        Método para descargar y guarder el modelo de comparación de frases.
    
        Retorna
        -------
        None
    """

    logger.warning("Descargando los modelos")

    crossEncoderName = "cross-encoder/stsb-roberta-base"
    model1 = CrossEncoder(crossEncoderName, cache_dir = './nplModules/Stsb')

    logger.warning("modelo stsb guardado con éxito.")

checkout()