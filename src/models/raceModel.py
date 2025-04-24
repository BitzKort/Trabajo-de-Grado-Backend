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
            cls._instance._load_model()

        return cls._instance
    
    def _load_model(self):

        dotenv.load_dotenv(".env")

        self.race_path = os.getenv("RACE_PATH")

        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.race_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.race_path)

        self.generator = pipeline("text2text-generation", self.model, self.tokenizer, device= 0 if torch.cuda.is_available() else -1)

    def genarteQA(self, text: str):

        response = self.generator(text,max_length=100, truncation=True)[0]['generated_text']
        logger.success("race Q generated")

        return response
        