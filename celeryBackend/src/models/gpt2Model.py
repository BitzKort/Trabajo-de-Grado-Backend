
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

        dotenv.load_dotenv(dotenv_path="../.env.dev")
        self.gpt_path = os.getenv("GPT2_PATH")

         # Verifica si la ruta existe
        if not os.path.exists(self.gpt_path):
            raise FileNotFoundError(f"Ruta del modelo gpt2 no encontrada: {self.gpt_path}")

        self.model  = AutoModelForCausalLM.from_pretrained(self.gpt_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.gpt_path)

        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.config.pad_token_id = self.tokenizer.eos_token_id

        self.generator = pipeline( 'text-generation', model = self.model, tokenizer= self.tokenizer, device= 0 if torch.cuda.is_available() else -1, pad_token_id=self.tokenizer.eos_token_id)

    def genetateText(self, base_text: str, max_length: int = 150) ->str:

        if len(base_text) > 70:
            base_text = base_text[:70]
            logger.warning("Texto base truncado a 70 caracteres")

        set_seed(40)
        generated_text = self.generator(base_text, max_length =max_length, 
                                        truncation = True, 
                                        num_return_sequences=1
                                        )[0]["generated_text"]
        
        
        logger.success("gpt2 text generated")


        #post procesamiento para evitar malos cierres en el texto
        last_valid_end = max(
            generated_text.rfind("."),
            generated_text.rfind("!"),
            generated_text.rfind("?")
        )
        
        if last_valid_end != -1:
            return generated_text[:last_valid_end+1]
        
        # Si no encuentra, devolver hasta el último espacio en blanco
        last_space = generated_text.rfind(" ", 0, len(generated_text)-1)

        return generated_text[:last_space+1] if last_space != -1 else generated_text