import dotenv
import os
from loguru import logger
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class DistractorModel:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.warning("Se crea una nueva instancia de distractors")
            cls._instance = super().__new__(cls)
            try:
                cls._instance._loadModel()
            except Exception as e:
                logger.error(f"Error en Distractor: {str(e)}")
                raise
        return cls._instance

    def _loadModel(self):

        dotenv.load_dotenv(dotenv_path="../.env.dev")

        self.distractor_path= os.getenv("DISTRACTOR_PATH")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.distractor_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.distractor_path)

    def generate_distractors(self, question: str,context: str, answer: str):
      input_text = " ".join([question, self.tokenizer.sep_token, answer, self.tokenizer.sep_token, context])
      inputs = self.tokenizer(input_text, return_tensors="pt")
      outputs = self.model.generate(**inputs, max_new_tokens=128)
      distractors = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
      distractors = distractors.replace(self.tokenizer.pad_token, "").replace(self.tokenizer.eos_token, "")
      distractors = [str(y.strip()) for y in distractors.split(self.tokenizer.sep_token)]

      logger.info(distractors)
      logger.info(distractors[0])

      return str(distractors[0])