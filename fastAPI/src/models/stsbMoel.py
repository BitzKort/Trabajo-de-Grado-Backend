import os
from sentence_transformers import CrossEncoder
from loguru import logger



class StsbModel():

    _instance = None

    def __new__(cls):
        
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            try:
                cls._instance._loadModel()

            except Exception as e:
                logger.error(f"Error al cargar el modelo stsb {str(e)}")
                raise

        return cls._instance
    
    def _loadModel(self):

        stsb_path = os.getenv("STSB_MODEL_PATH")

        self.generator = CrossEncoder(model_name_or_path=stsb_path)

    def generatePredict(self, sentence1: str, sentence2: str):

        prediction = str(self.generator.predict(sentence1, sentence2))
        logger.success("Predicción generada")

        return prediction 

