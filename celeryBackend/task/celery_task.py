import os
import dotenv
import random
import json
from task.celery_app import celery
from src.models.gpt2Model import Gpt2Model
from src.models.raceModel import RaceModel
from src.models.squadModel import SquadModel
from src.schemas.nplSchemas import QuestionCardResponse, Question
from typing import List
from loguru import logger
from celery import group, chord
from datasets import load_from_disk


dotenv.load_dotenv(dotenv_path="../.env")


data_path = os.getenv("DATASPLIT_PATH")


#1. server rest -> front react
#1.1. neondb
#2. redis lecciones
#3. celery

#Este metodo genera un dict con id, url, titulo y texto
def getDatasetText(dataset) -> list:
    
    randomId = random.sample(range(1,205328),5)

    sample_text = list(map(lambda x: dataset[x],randomId))

    return sample_text

@celery.task
def generate_lesson(dict_text) -> str:

    gpt2 = Gpt2Model()
    raceQA = RaceModel()
    scuadQA = SquadModel()


    sample_text = dict_text["text"]

    logger.warning("a lesson is generating")

    final_text = gpt2.genetateText(sample_text)

    qa_race = raceQA.genarteQA(final_text)

    qa_squad = scuadQA.genrateQA(final_text)

    response = (QuestionCardResponse(title=dict_text["title"], text=final_text, Questions=[Question(question= qa_race), Question(question= qa_squad)]))

    logger.success("leccion generada")

    return response.model_dump_json()

@celery.task(bind=True)     
def save_on_dbs(self, results):

    redis = self.backend.client

    data_json = json.dumps(results, ensure_ascii=False)

    key = f"lessons:default"

    redis.set(key, data_json)

    return {"stored_key": key, "count": len(results)}
    

@celery.task
def generate_lessons():

    dataset = load_from_disk(data_path)
   

    sample_text = getDatasetText(dataset)


    jobs = [generate_lesson.s(dict_text) for dict_text in sample_text]


    chord(jobs)(save_on_dbs.s())
