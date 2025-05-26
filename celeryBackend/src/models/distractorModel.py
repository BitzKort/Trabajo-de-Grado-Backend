import dotenv
import os
from loguru import logger
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class DistractorModel:

    """
        Clase para manejar las instancias creadas del modelo t5-large-generation-race-Distractor.
        Utiliza el patrón singleton para el manejo de la memoria.

        Retorna
        -------
        Una instancia del modelo t5-large-generation-race-Distractor.

    """

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

    def generate_distractors(self, question: str, context: str, answer: str):
        input_text = " ".join([question, self.tokenizer.sep_token, answer, self.tokenizer.sep_token, context])
        inputs = self.tokenizer(input_text, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=128,
            num_beams=5,  
            no_repeat_ngram_size=2,  
            do_sample=True,  
            temperature=0.9,  
            top_k=50
        )
        
        distractors = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
        distractors = distractors.replace(self.tokenizer.pad_token, "").replace(self.tokenizer.eos_token, "")
        distractors = [y.strip() for y in distractors.split(self.tokenizer.sep_token) if y.strip()]
        
       
        valid_distractors = []
        seen = set()
        for distractor in distractors:
            
            lower_dist = distractor.lower()
            lower_ans = answer.lower()
            if (lower_dist not in seen and 
                lower_dist != lower_ans and 
                not any(word in lower_ans for word in lower_dist.split()) and
                len(distractor) > 2):
                
                valid_distractors.append(distractor)
                seen.add(lower_dist)
        
        logger.info(f"Distractores generados: {valid_distractors}")

        return valid_distractors[0]
    