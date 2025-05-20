import os
import dotenv
import random
from task.celery_app import celery
from loguru import logger
from celery import group, chord
from datasets import load_from_disk
from tsidpy import TSID
from src.repository.lessonRepository import delete_lessons_data
from src. repository.lessonRepository import insert_questions, insert_lesson
from src.models.gpt2Model import Gpt2Model
from src.models.raceModel import RaceModel
from src.models.squadModel import SquadModel
from src.models.distractorModel import DistractorModel
from src.schemas.nplSchemas import LessonData, Question, RedisSave


dotenv.load_dotenv(dotenv_path="../.env.dev")
data_path = os.getenv("DATASPLIT_PATH")

#Este metodo genera un dict con id, url, titulo y texto
def getDatasetText(dataset) -> list:
    
    randomId = random.sample(range(1,205328),2)

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
def generate_lesson(dict_text) -> LessonData:

    gpt2 = Gpt2Model()
    raceQA = RaceModel()
    scuadQA = SquadModel()
    distractor = DistractorModel()


    sample_text = dict_text["text"]

    logger.warning("Generando leccion.")

    final_text = gpt2.genetateText(sample_text)

    qa_race = raceQA.genarteQA(final_text)

    question_race, answer_race = split_qa(qa_race)

    distractor_race = distractor.generate_distractors(question_race, final_text, answer_race)


    logger.warning(f"distractor race: {distractor_race}")


    qa_squad = scuadQA.genrateQA(final_text)

    question_squad, answer_squad = split_qa(qa_squad)

    distractor_squad = distractor.generate_distractors(question_squad, final_text, answer_squad)

    logger.warning(f"distractor squad: {distractor_squad}")

    lessons_generated = LessonData(title=dict_text["title"], text=final_text, Questions=[Question(question= question_race, answer=answer_race, distractor=distractor_race), Question(question= question_squad, answer=answer_squad, distractor=distractor_squad)])

    logger.success("leccion generada")

    return lessons_generated.model_dump() 


@celery.task(bind=True)     
def save_on_dbs(self, lessons):

    redis = self.backend.client

    pipeline = redis.pipeline()

    all_lesson_ids = []

    try:

        logger.warning("Iniciando borrado de lecciones antiguas")

        delete_lessons_data(self.backend.client)

    except Exception as e:

        logger.error(e)

    logger.warning("Lecciones en proceso de guardado")

    try:
        
        for lesson in lessons:

            lesson = LessonData(**lesson)

    
            
            questions_id = insert_questions(lesson.Questions)

            lesson_id = insert_lesson(lesson, questions_id)



            
            #para redis
            key = f"lesson:{lesson_id}"

            all_lesson_ids.append(key)

            redisResult = RedisSave(id=lesson_id, title=lesson.title, question_count=str(len(lesson.Questions)))

            pipeline.hset(
                name=key,
                mapping=redisResult.model_dump()
                )


        
        if all_lesson_ids:
            pipeline.sadd("all_lessons", *all_lesson_ids)

        pipeline.execute()

        logger.success("Todas las lecciones han sido guardadas")
    
    except Exception as e:

        logger.error(e)
        raise e

@celery.task
def generate_lessons():




    dataset = load_from_disk(data_path)
   

    sample_text = getDatasetText(dataset)


    jobs = [generate_lesson.s(dict_text) for dict_text in sample_text]


    chord(jobs)(save_on_dbs.s())
