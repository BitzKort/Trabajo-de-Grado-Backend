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
from src.repository.dbConection import get_postgres_conn, release_postgres_conn
from src. repository.lessonRepository import insert_lesson
from tsidpy import TSID



dotenv.load_dotenv(dotenv_path="../.env.prod")
data_path = os.getenv("DATASPLIT_PATH")

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

    #iteramos con el fin de guardar una por una en postgres y redis
    for result in results:

        conexion = get_postgres_conn()
        id = str(TSID.create())

        #para postgress
        lesson = QuestionCardResponse(**result)

        try:
            insert_lesson(id, lesson, conexion)
        finally:
            release_postgres_conn(conexion)
        
        #para redis
        key = f"lessons:{id}"

        redis.set(key, result)

@celery.task
def generate_lessons():

    dataset = load_from_disk(data_path)
   

    sample_text = getDatasetText(dataset)


    jobs = [generate_lesson.s(dict_text) for dict_text in sample_text]


    chord(jobs)(save_on_dbs.s())
