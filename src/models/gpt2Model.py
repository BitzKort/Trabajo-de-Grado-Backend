
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
            cls._instance._loadModel()
        
        return cls._instance

    def _loadModel(self):

        dotenv.load_dotenv(dotenv_path=".env")
        gpt_path = os.getenv("GPT2_PATH")

        print(gpt_path)

        self.model  = AutoModelForCausalLM.from_pretrained(gpt_path)
        self.tokenizer = AutoTokenizer.from_pretrained(gpt_path)

        self.generator = pipeline( 'text-generation', model = self.model, tokenizer= self.tokenizer, device_map="auto")

    def genetateText(self, base_text: str, max_length: int = 200) ->str:

        set_seed(40)
        response = self.generator(base_text, max_length =max_length, truncation = True, num_return_sequences=1)[0]["generated_text"]
        logger.success("gpt2 text generated")

        return response