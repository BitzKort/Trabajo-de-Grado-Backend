import os
import dotenv
import random
import json
from task.celery_app import celery
from src.models.gpt2Model import Gpt2Model
from src.models.raceModel import RaceModel
from src.models.squadModel import SquadModel
from src.models.distractorModel import DistractorModel
from src.schemas.nplSchemas import QuestionCardResponse, Question
from typing import List
from loguru import logger
from celery import group, chord
from datasets import load_from_disk
from src. repository.lessonRepository import insert_lesson
from tsidpy import TSID



dotenv.load_dotenv(dotenv_path="../.env.dev")
data_path = os.getenv("DATASPLIT_PATH")

#Este metodo genera un dict con id, url, titulo y texto
def getDatasetText(dataset) -> list:
    
    randomId = random.sample(range(1,205328),10)

    sample_text = list(map(lambda x: dataset[x],randomId))

    return sample_text


def split_qa(text: str) -> tuple[str, str]:
    # Definir posibles separadores en orden de prioridad
    separators = ['? ', ' . ']
    
    for sep in separators:
        last_index = text.rfind(sep)
        if last_index != -1:
            # Encontramos el separador
            question = text[:last_index].strip()
            answer = text[last_index+len(sep):].strip()
            
            # Eliminar posibles signos de interrogación finales en la pregunta
            if question.endswith('?'):
                question = question[:-1].strip()
                
            return question, answer
    
    # Si no se encuentra ningún separador
    return text.strip(), ''


@celery.task
def generate_lesson(dict_text) -> str:

    gpt2 = Gpt2Model()
    raceQA = RaceModel()
    scuadQA = SquadModel()
    distractor = DistractorModel()


    sample_text = dict_text["text"]

    logger.warning("a lesson is generating")

    final_text = gpt2.genetateText(sample_text)

    qa_race = raceQA.genarteQA(final_text)

    question_race, answer_race = split_qa(qa_race)

    distractor_race_list = distractor.generate_distractors(question_race, final_text, answer_race)


    logger.warning(f"distractor race: {distractor_race_list}")


    qa_squad = scuadQA.genrateQA(final_text)

    question_squad, answer_squad = split_qa(qa_squad)

    distractor_squad_list = distractor.generate_distractors(question_squad, final_text, answer_squad)

    logger.warning(f"distractor squad: {distractor_squad_list}")

    response = (QuestionCardResponse(title=dict_text["title"], text=final_text, Questions=[Question(question= qa_race, answer=answer_race, Distractors=distractor_race_list), Question(question= qa_squad, answer=answer_squad,Distractors=distractor_squad_list)]))

    logger.success("leccion generada")

    return response.model_dump_json()

@celery.task(bind=True)     
def save_on_dbs(self, results):

    logger.warning("Lecciones en proceso de guardado")
    redis = self.backend.client

    #iteramos con el fin de guardar una por una en postgres y redis
    for result in results:

        id = str(TSID.create())

        #para postgress
        lesson = QuestionCardResponse.model_validate_json(result)

        try:
            insert_lesson(id, lesson)

        except Exception as e:
            raise
        
        #para redis
        key = f"lessons:{id}"

        redis.set(key, result)
    
    logger.success("Todas las lecciones han sido guardadas")

@celery.task
def generate_lessons():

    dataset = load_from_disk(data_path)
   

    sample_text = getDatasetText(dataset)


    jobs = [generate_lesson.s(dict_text) for dict_text in sample_text]


    chord(jobs)(save_on_dbs.s())
