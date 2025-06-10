import re
import os
import dotenv
from loguru import logger
from transformers import pipeline
from datasets import load_dataset, Dataset
from datasets import load_dataset

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
     

    global modules_path 
    global gpt_path 
    global race_path 
    global squad_path
    global distractor_path
    global datasetFolder
    global datasetFilterFolder



    modules_path = os.getenv("MODULES_PATH")
    datasetFolder = os.getenv("DATA_PATH")
    datasetFilterFolder = os.getenv("DATASPLIT_PATH")
    gpt_path = os.getenv("GPT2_PATH")
    race_path = os.getenv("RACE_PATH")
    squad_path = os.getenv("SQUAD_PATH")
    distractor_path = os.getenv("DISTRACTOR_PATH")

    init_Folders()
     

def init_Folders():

    """
        Método para crear las carpetas de los modelos
    
        Retorna
        -------
        None
    """

    logger.warning("Creando las carpetas para los modelos.")

    dotenv.load_dotenv(dotenv_path=".env.dev")


    

    modules_path = './nplModules'
    os.makedirs(modules_path, exist_ok=True)
    os.makedirs(gpt_path, exist_ok=True)
    os.makedirs(race_path, exist_ok=True)
    os.makedirs(squad_path, exist_ok=True)
    os.makedirs(distractor_path, exist_ok=True)
    os.makedirs(datasetFolder, exist_ok=True)
    os.makedirs(datasetFilterFolder, exist_ok=True)

    logger.success("Carpetas creadas.")

    init_models()


def init_models():

    """
        Método para descargar y guarder los modelos
    
        Retorna
        -------
        None
    """

    logger.warning("Descargando los modelos.")


    
    textGenerator = pipeline('text-generation', model='gpt2')
   

    raceQAGenerator = pipeline("text2text-generation", model="potsawee/t5-large-generation-race-QuestionAnswer")

   

    squadQAGenerator = pipeline("text2text-generation", model = "potsawee/t5-large-generation-squad-QuestionAnswer")

   
    DGenerator = pipeline("text2text-generation", model="potsawee/t5-large-generation-race-Distractor")

    

    logger.warning("Guardando los modelos.")
    
    
    #gpt
    textGenerator.model.save_pretrained(gpt_path)
    textGenerator.tokenizer.save_pretrained(gpt_path)

    #race-t5 model (Abstractive)
    raceQAGenerator.model.save_pretrained(race_path)
    raceQAGenerator.tokenizer.save_pretrained(race_path)

    #squad-t5 model (extractive)
    squadQAGenerator.model.save_pretrained(squad_path)
    squadQAGenerator.tokenizer.save_pretrained(squad_path)

    DGenerator.model.save_pretrained(distractor_path)
    DGenerator.tokenizer.save_pretrained(distractor_path)


    logger.success("Todos los modelos han sido guardados.")



    init_dataset()


def init_dataset():


    """
        Método para descargar el dataset utilizado.

        Restricciones
        ----------
        - Se eliminan id's conflictivos segun pruebas durante el desarrollo
        - Se eliminan textos que contengan caracteres diferentes a los existentes en el idioma ingles y español.
        - Se crea un nuevo dataset
        - Se guarda en local
    
        Retorna
        -------
        None
    """

   
    exclude_ids = {"302157", "367755", "28112", "604881", "789869"}


    def is_valid_text(text: str) -> bool:
        pattern = re.compile(
            r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ'
            r'\s.,;:!?¿¡()\-]*$'
        )
        return bool(pattern.fullmatch(text))


    logger.warning("Descargando el dataset para su uso...")
    dataset = load_dataset("wikipedia", "20220301.simple")["train"]

   
    logger.warning("procesando el dataset...")
    filtered_data = []
    for example in dataset:
        # Saltar IDs excluidos
        if example["id"] in exclude_ids:
            continue
        
        # Procesar texto
        clean_text = example["text"].split("\n")[0].strip()
        
        if clean_text and is_valid_text(clean_text):
            filtered_data.append({
                "id": example["id"],
                "title": example["title"],
                "text": clean_text
            })

    logger.warning("Creando el dataset final...")

    clean_dataset = Dataset.from_dict({
        "id": [x["id"] for x in filtered_data],
        "title": [x["title"] for x in filtered_data],
        "text": [x["text"] for x in filtered_data]
    })

    logger.warning(f"Dataset final guardado en {datasetFilterFolder}")

    logger.success("dataset final guardado exitosamente en local")
    logger.info(clean_dataset)

    clean_dataset.save_to_disk(datasetFilterFolder)

checkout()