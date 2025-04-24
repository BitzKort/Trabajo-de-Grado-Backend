import os
from schemas.nplSchemas import QuestionCardResponse, SentenceCompareResponse
from sentence_transformers import CrossEncoder
from transformers import pipeline, set_seed, AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModel
from loguru import logger
import re
import dotenv

pln_models = {}



dotenv.load_dotenv(dotenv_path=".env")

stsb_path = os.getenv("STSB_PATH")

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
    
    logger.success("squad-genetarion model ok")


    #init the stsb model

    logger.success("stsb model ok")



async def getText():

    generator = pln_models["gptGenerator"]

    set_seed(42)
    textGenerated = generator("A woman is slicing tomato.", max_length=100, truncation = True, num_return_sequences=1)[0]['generated_text']

    return textGenerated
    


async def getQuestionRACE(text) -> QuestionCardResponse:

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


async def compareAnswer(SentenceNlp) -> SentenceCompareResponse:

    stsb_model = CrossEncoder(model_name="nplModules\Stsb\models--cross-encoder--stsb-roberta-base\snapshots\d576534b67143e2c70ee9966d7fdbf5835728d13")

    predict = str(stsb_model.predict((SentenceNlp, "hi, how are you")))
    
    return SentenceCompareResponse(sentenceNlp=SentenceNlp, sentenceUser= "hi, how are you", score=predict)

