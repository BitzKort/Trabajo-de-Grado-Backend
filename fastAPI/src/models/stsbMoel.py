import os
from sentence_transformers import CrossEncoder
from loguru import logger



class StsbModel():

    
    """
        Clase para manejar las instancias creadas del modelo cross-encoder/stsb-roberta-base.
        Utiliza el patrón singleton para el manejo de la memoria.

        Retorna
        -------
        Una instancia del modelo cross-encoder/stsb-roberta-base.

    """

    _instance = None

    def __new__(cls):
        
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.warning("Se crea una nueva instancia de StsbModel")
            
            try:
                cls._instance._loadModel()

            except Exception as e:
                logger.error(f"Error al cargar el modelo stsb {str(e)}")
                raise

        return cls._instance
    
    def _loadModel(self):

        stsb_path = os.getenv("STSB_MODEL_PATH")

        self.generator = CrossEncoder(model_name=stsb_path)

    def generatePredict(self, sentence1: str, sentence2: str):

        prediction = str(self.generator.predict(sentence1, sentence2))

        return prediction 

