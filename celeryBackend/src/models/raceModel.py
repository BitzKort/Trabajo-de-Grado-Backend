import dotenv
import os
import torch
import re
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from loguru import logger


class RaceModel:

    """
        Clase para manejar las instancias creadas del modelo t5-large-generation-race-QuestionAnswer.
        Utiliza el patrón singleton para el manejo de la memoria.

        Retorna
        -------
        Una instancia del modelo t5-large-generation-race-QuestionAnswer.

    """

    _instance = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)
            
            try:
                cls._instance._loadModel()

            except Exception as e:
                logger.error(f"Error en RACE {str(e)}")
                raise

        return cls._instance
    
    def _loadModel(self):

        dotenv.load_dotenv(dotenv_path="../.env.dev")

        self.race_path = os.getenv("RACE_PATH")

         # Verifica si la ruta existe
        if not os.path.exists(self.race_path):
            raise FileNotFoundError(f"Ruta del modelo RACE no encontrada: {self.race_path}")

        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.race_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.race_path)

        self.generator = pipeline(
                    "text2text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if torch.cuda.is_available() else -1,
                    max_length=80,
                    num_beams=5,
                    no_repeat_ngram_size=2,
                    do_sample=True,
                    temperature=0.7,
                    top_k=50
                )
    def generateQA(self, text: str):

        response = self.generator(text,max_length=80, truncation=True)[0]['generated_text']

        clean_response = re.sub(
            r'[^a-zA-Z0-9áéíóúüñÁÉÍÓÚÜÑ¿¡\s\.,;:!?()\-—"\'-]', 
            '', response).strip()

        logger.success("race Q&A generado y sanitizado")

        return clean_response
        