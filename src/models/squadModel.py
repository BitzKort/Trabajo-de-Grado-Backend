from transformers import pipeline, AutoModelForSeq2SeqLM ,AutoTokenizer
from loguru import logger
import os
import dotenv


class SquadModel():

    _instance = None

    def __new__(cls):
        
        if cls._instance is None:

            cls._instance = super().__new__(cls)
            cls._instance._loadModel()
        
        return cls._instance
    
    def _loadModel(self):

        dotenv.load_dotenv(".env")

        self.squad_path = os.getenv("SQUAD_PATH")

        self.model = AutoModelForSeq2SeqLM(self.squad_path)
        self.tokenizer = AutoTokenizer(self.squad_path)

        self.generator = pipeline("text2text-generation", self.model, self.tokenizer)
    
    def genrateQA(self, text: str):

        response = self.generator(text, max_length=100, truncation = True)[0]['generated_text']
        logger.success("squad QA generated")

        return response


