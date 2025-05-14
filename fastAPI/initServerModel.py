
from loguru import logger
import os
from sentence_transformers import CrossEncoder
import dotenv
from pathlib import Path



#Run this script only before create the docker images

def checkout():

    dotenv.load_dotenv(dotenv_path="../.env.dev")
    
    global stsb_path

    modules_path = os.getenv("MODULES_PATH")
    stsb_path = os.getenv("STSB_PATH")
     

    logger.warning("scanning necessary files")

    if not (Path(stsb_path).is_dir()):
         
        logger.warning("some folders were not found")
        init_Folders()
    
    else:
         logger.success("ready to start the server")


def init_Folders():

    logger.warning("creating the folder for the stsb model")

    dotenv.load_dotenv(dotenv_path=".env")

    modules_path = './nplModules'
    os.makedirs(modules_path, exist_ok=True)
    os.makedirs(stsb_path, exist_ok=True)

    logger.success("folders created")

    init_models()


def init_models():

    logger.warning("Download the models")

    #Special saving for stsb model
    crossEncoderName = "cross-encoder/stsb-roberta-base"
    model1 = CrossEncoder(crossEncoderName, cache_dir = './nplModules/Stsb')

    logger.warning("model stsb was saved succesfully")

checkout()