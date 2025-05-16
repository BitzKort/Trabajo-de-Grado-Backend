
from loguru import logger
import os
from transformers import pipeline
import dotenv
from datasets import load_dataset
from pathlib import Path
from pprint import pprint



#Run this script only before create the docker images

def checkout():

    dotenv.load_dotenv(dotenv_path="../.env.dev")
     

    global modules_path 
    global gpt_path 
    global race_path 
    global squad_path
    global distractor_path
    global datasetFolder
    global datasetFilterFolder



    modules_path = os.getenv("MODULES_PATH")
    datasetFolder = os.getenv("DATA_PATH")
    datasetFilterFolder = os.getenv("DATASPLIT_PATH")
    gpt_path = os.getenv("GPT2_PATH")
    race_path = os.getenv("RACE_PATH")
    squad_path = os.getenv("SQUAD_PATH")
    distractor_path = os.getenv("DISTRACTOR_PATH")

    init_Folders()
     

def init_Folders():

    logger.warning("creating the folder for the models")

    dotenv.load_dotenv(dotenv_path=".env.dev")


    

    modules_path = './nplModules'
    os.makedirs(modules_path, exist_ok=True)
    os.makedirs(gpt_path, exist_ok=True)
    os.makedirs(race_path, exist_ok=True)
    os.makedirs(squad_path, exist_ok=True)
    os.makedirs(distractor_path, exist_ok=True)
    os.makedirs(datasetFolder, exist_ok=True)
    os.makedirs(datasetFilterFolder, exist_ok=True)

    logger.success("folders created")

    init_models()


def init_models():

    logger.warning("Download the models")


    #Model for text generation (experimental)
    textGenerator = pipeline('text-generation', model='gpt2')
    
    #Model for question and answers in an abstractive form (potsawee/t5-large-generation-race-QuestionAnswer)

    raceQAGenerator = pipeline("text2text-generation", model="potsawee/t5-large-generation-race-QuestionAnswer")

    #Model for question and answers in an extractive form (potsawee/t5-large-generation-squad-QuestionAnswer)

    squadQAGenerator = pipeline("text2text-generation", model = "potsawee/t5-large-generation-squad-QuestionAnswer")

    #Model for distractor answers t5-large-generation-race-Distractor

    DGenerator = pipeline("text2text-generation", model="potsawee/t5-large-generation-race-Distractor")

    

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

    DGenerator.model.save_pretrained(distractor_path)
    DGenerator.tokenizer.save_pretrained(distractor_path)


    logger.success("All models saved in the server")



    init_dataset()


def init_dataset():

    logger.warning("Downloading the dataset wikipedia.simple")

    dataset = load_dataset("wikipedia", "20220301.simple", cache_dir=datasetFolder, trust_remote_code=True)

    allTexts = dataset["train"]["text"]

    allSplitedText = list(map(lambda x: x.split("\n")[0], allTexts)) 

    newDataset = dataset["train"].remove_columns(["text"])
    newDataset = newDataset.add_column("text", allSplitedText)

    newDataset.save_to_disk(datasetFilterFolder)

    

checkout()