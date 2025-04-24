from sentence_transformers import CrossEncoder
import os
import dotenv
from loguru import logger



class StsbModel():

    _instance = None

    def __new__(cls):
        
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loadModel()

        return cls._instance
    
    def _loadModel(self):

        dotenv.load_dotenv(".env")

        stsb_path = os.getenv("STSB_MODEL_PATH")

        self.generator = CrossEncoder(model_name=stsb_path)

    def generatePredict(self, sentence1: str, sentence2: str):

        response = str(self.generator.predict(sentence1, sentence2))
        logger.success("predict generated")

        return response 

