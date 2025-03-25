import os
from schemas.nplSchemas import QuestionCardResponse
from sentence_transformers import CrossEncoder
from transformers import pipeline, set_seed, AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM
from loguru import logger


pln_models = {}


async def init_models(gpt_path, race_path, squad_path, stsb_path ):


    global pln_models

    logger.warning("init models")

    
    #init the gpt2 model
    gptModel = AutoModelForCausalLM.from_pretrained(gpt_path)
    GptTokenizer = AutoTokenizer.from_pretrained(gpt_path)
    gptGenerator = pipeline('text-generation', model=gptModel, tokenizer=GptTokenizer, device=0)

    pln_models["gptGenerator"] = gptGenerator

    logger.success("gpt model ok")

    #init the race model
    raceModel = AutoModelForSeq2SeqLM.from_pretrained(race_path)
    raceTokenizer = AutoTokenizer.from_pretrained(race_path)
    raceGenerator = pipeline("text2text-generation", model=raceModel, tokenizer=raceTokenizer, device=0)

    pln_models["raceGenerator"] = raceGenerator

    logger.success("race-genetarion model ok")

        #init the race model
    squadModel = AutoModelForSeq2SeqLM.from_pretrained(squad_path)
    squadTokenizer = AutoTokenizer.from_pretrained(squad_path)
    squadGenerator = pipeline("text2text-generation", model=squadModel, tokenizer=squadTokenizer, device=0)

    pln_models["squadGenerator"] = squadGenerator




async def getText():

    generator = pln_models["gptGenerator"]

    set_seed(42)
    textGenerated = generator("A woman is slicing tomato.", max_length=100, truncation = True, num_return_sequences=1)[0]['generated_text']

    return textGenerated
    

import re
async def getQuestion(text) -> QuestionCardResponse:

    raceGenerator = pln_models["raceGenerator"]

    response = raceGenerator(text,max_length=100, truncation=True)[0]['generated_text']


    print(response)

    response = re.split(r"(?<=[?_])", response)

    return QuestionCardResponse(text=text, question=response[0], answer= response[1])


async def getQuestionSQUAD(text) ->QuestionCardResponse:

    squadGenerator = pln_models["squadGenerator"]

    response = squadGenerator(text, max_length=100, truncation=True)[0]['generated_text']

    response = re.split(r"(?<=[?_])", response)

    return QuestionCardResponse(text=text, question=response[0], answer= response[1])


    

