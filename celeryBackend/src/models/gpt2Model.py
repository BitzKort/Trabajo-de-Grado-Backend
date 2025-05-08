
from transformers import pipeline, set_seed, AutoModelForCausalLM, AutoTokenizer
from loguru import logger
import dotenv
import os
import torch
class Gpt2Model:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.warning("Se crea una nueva instancia de gpt2")
            cls._instance = super().__new__(cls)

            try:
                cls._instance._loadModel()

            except Exception as e:
                logger.error(f"Error en gpt2 {str(e)}")
                raise
        return cls._instance

    def _loadModel(self):

        dotenv.load_dotenv(dotenv_path="../.env.prod")
        self.gpt_path = os.getenv("GPT2_PATH")

         # Verifica si la ruta existe
        if not os.path.exists(self.gpt_path):
            raise FileNotFoundError(f"Ruta del modelo gpt2 no encontrada: {self.gpt_path}")

        self.model  = AutoModelForCausalLM.from_pretrained(self.gpt_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.gpt_path)

        self.generator = pipeline( 'text-generation', model = self.model, tokenizer= self.tokenizer, device= 0 if torch.cuda.is_available() else -1 )

    def genetateText(self, base_text: str, max_length: int = 200) ->str:

        set_seed(40)
        response = self.generator(base_text, max_length =max_length, truncation = True, num_return_sequences=1)[0]["generated_text"]
        logger.success("gpt2 text generated")

        return response