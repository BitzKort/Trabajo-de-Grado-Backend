import os
from schemas.nplSchemas import Something
from sentence_transformers import CrossEncoder
from transformers import pipeline, set_seed, AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM
from loguru import logger


pln_models = {}

async def init_Folders():

    logger.warning("creating the folder for the models")

    modules_path = './nplModules'
    gpt_path = os.path.join(modules_path, 'gpt2')
    race_path = os.path.join(modules_path, 'Q&A-RACE')
    squad_path = os.path.join(modules_path,'Q&A-SQUAD')
    stsb_path = os.path.join(modules_path="Stsb")
    os.makedirs(modules_path, exist_ok=True)
    os.makedirs(gpt_path, exist_ok=True)
    os.makedirs(race, exist_ok=True)
    os.makedirs(squad, exist_ok=True)
    os.makedirs(stsb, exist_ok=True)

    logger.success("folders created")

    await init_models(gpt_path, race_path, squad_path, stsb_path)

async def init_models(gpt_path, race_path, squad_path, stsb_path ):


    global pln_models

    logger.warning("Download the models")


    #Model for text generation (experimental)
    textGenerator = pipeline('text-generation', model='gpt2-medium')

    #Model for question and answers in an abstractive form (potsawee/t5-large-generation-race-QuestionAnswer)

    raceQAGenerator = pipeline("text2text-generation", model="potsawee/t5-large-generation-race-Distractor")

    #Model for question and answers in an extractive form (potsawee/t5-large-generation-squad-QuestionAnswer)

    squadQAGenerator = pipeline("text2text-generation", model = "potsawee/t5-large-generation-squad-QuestionAnswer")

    #Model for semantic similarity "compare the user/model answers with an attention model" (cross-encoder/stsb-roberta-base)

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




    logger.warning("init models")

    model = AutoModelForCausalLM.from_pretrained(gpt_path)
    tokenizer = AutoTokenizer.from_pretrained(gpt_path)
    gptGenerator = pipeline('text-generation', model=model, tokenizer=tokenizer, device=1)

    pln_models["gptGenerator"] = gptGenerator

    logger.success("all models ok")



async def getText():

    generator = pln_models["gptGenerator"]

    set_seed(42)
    results = generator("The tennis shoes have a range of prices.", max_length=60, num_return_sequences=2)

    return Something(text= results[0]['generated_text'])

async def getQuestion(text):

    pass

