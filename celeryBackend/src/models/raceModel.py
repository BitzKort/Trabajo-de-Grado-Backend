from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from loguru import logger
import dotenv
import os
import torch

class RaceModel:

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

        self.generator = pipeline("text2text-generation", model= self.model, tokenizer= self.tokenizer, device=0 if torch.cuda.is_available() else -1)

    def genarteQA(self, text: str):

        response = self.generator(text,max_length=100, truncation=True)[0]['generated_text']
        logger.success("race Q generated")

        return response
        