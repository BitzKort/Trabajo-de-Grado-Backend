import dotenv
import os
import re
import difflib
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
        logger.info(f"answer: {answer}")
        input_text = " ".join([question, self.tokenizer.sep_token, answer, self.tokenizer.sep_token, context])
        inputs = self.tokenizer(input_text, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=20,
            num_beams=5,
            no_repeat_ngram_size=2,
            do_sample=True,
            temperature=0.9,
            top_k=50
        )
        
        distractors = self.tokenizer.decode(outputs[0], skip_special_tokens=False)
        distractors = distractors.replace(self.tokenizer.pad_token, "").replace(self.tokenizer.eos_token, "")
        
        # Limpieza con regex
        clean_pattern = r'[^a-zA-Z0-9áéíóúüñÁÉÍÓÚÜÑ¿¡\s\.,;:!?()\-—"\'–]'
        distractors = [
            re.sub(clean_pattern, '', d.strip()) 
            for d in distractors.split(self.tokenizer.sep_token) 
            if d.strip()
        ]
        
        valid_distractors = []
        seen = set()
        for distractor in distractors:
            logger.warning(distractor)
            clean_d = re.sub(clean_pattern, '', distractor).strip()
            if not clean_d:
                continue
                
            lower_dist = clean_d.lower()
            lower_ans = answer.lower()
            
            if (lower_dist not in seen and 
                            lower_dist != lower_ans and
                        len(clean_d) > 2):
                
                valid_distractors.append(clean_d)
                seen.add(lower_dist)
        
            if valid_distractors:
                most_diff = min(
                    valid_distractors,
                    key=lambda d: difflib.SequenceMatcher(None, d.lower(), answer.lower().strip()).ratio()
                )
                return most_diff
    