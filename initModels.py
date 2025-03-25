
from loguru import logger
import os
from transformers import pipeline
import dotenv

def init_Folders():

    dotenv.load_dotenv(dotenv_path=".env")


    modules_path = os.getenv("MODULES_PATH")
    gpt_path = os.getenv("GPT2_PATH")
    race_path = os.getenv("RACE_PATH")
    squad_path = os.getenv("SQUAD_PATH")
    stsb_path = os.getenv("STSB_PATH")

    logger.warning("creating the folder for the models")

    modules_path = './nplModules'
    os.makedirs(modules_path, exist_ok=True)
    os.makedirs(gpt_path, exist_ok=True)
    os.makedirs(race_path, exist_ok=True)
    os.makedirs(squad_path, exist_ok=True)
    os.makedirs(stsb_path, exist_ok=True)

    logger.success("folders created")

    logger.warning("Download the models")


    #Model for text generation (experimental)
    textGenerator = pipeline('text-generation', model='gpt2-medium')
    
    #Model for question and answers in an abstractive form (potsawee/t5-large-generation-race-QuestionAnswer)

    raceQAGenerator = pipeline("text2text-generation", model="potsawee/t5-large-generation-race-QuestionAnswer")

    #Model for question and answers in an extractive form (potsawee/t5-large-generation-squad-QuestionAnswer)

    squadQAGenerator = pipeline("text2text-generation", model = "potsawee/t5-large-generation-squad-QuestionAnswer")

    #Model for semantic similarity "compare the user/model answers with an attention model" (cross-encoder/stsb-roberta-base)

    logger.success("All models downloaded")

    logger.warning("Saving models")
    
    
    #For gpt model
    textGenerator.model.save_pretrained(gpt_path)
    textGenerator.tokenizer.save_pretrained(gpt_path)

    #For race-t5 model (Abstractive)
    raceQAGenerator.model.save_pretrained(race_path)
    raceQAGenerator.tokenizer.save_pretrained(race_path)

    #For squad-t5 model (extractive)
    squadQAGenerator.model.save_pretrained(squad_path)
    squadQAGenerator.tokenizer.save_pretrained(squad_path)

    logger.success("All models saved in the server")


init_Folders()