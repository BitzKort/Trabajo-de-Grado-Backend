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
    stb_path = os.path.join(modules_path, 'stb')
    question_path = os.path.join(modules_path,'QAGen')
    os.makedirs(modules_path, exist_ok=True)
    os.makedirs(gpt_path, exist_ok=True)
    os.makedirs(stb_path, exist_ok=True)
    os.makedirs(question_path, exist_ok=True)

    logger.success("folders created")

    await init_models(gpt_path, stb_path, question_path)

async def init_models(gpt_path, stb_path, question_path):


    global pln_models

    logger.warning("Download the models")

    generator = pipeline('text-generation', model='gpt2-medium')


    logger.warning("Saving models")
    generator.model.save_pretrained(gpt_path)
    generator.tokenizer.save_pretrained(gpt_path)

    logger.warning("init models")

    model = AutoModelForCausalLM.from_pretrained(gpt_path)
    tokenizer = AutoTokenizer.from_pretrained(gpt_path)
    gptGenerator = pipeline('text-generation', model=model, tokenizer=tokenizer)

    pln_models["gptGenerator"] = gptGenerator

    logger.success("all models ok")



async def getText():

    generator = pln_models["gptGenerator"]

    set_seed(42)
    results = generator("A woman is slicing tomato.", max_length=60, num_return_sequences=1)

    return Something(text= results[0]['generated_text'])

