import os
import dotenv
import random
import re
from task.celery_app import celery
from loguru import logger
from celery import chord
from datasets import load_from_disk
from src.repository.lessonRepository import delete_lessons_data
from src. repository.lessonRepository import insert_questions, insert_lesson
from src.models.gpt2Model import Gpt2Model
from src.models.raceModel import RaceModel
from src.models.squadModel import SquadModel
from src.models.distractorModel import DistractorModel
from src.schemas.nplSchemas import LessonData, Question, RedisSave


dotenv.load_dotenv(dotenv_path="../.env.dev")
data_path = os.getenv("DATASPLIT_PATH")

def getDatasetTextRetry() -> str:


    """
        Metodo para generar un numero dentro del rango del dataset y obtener un texto de muestra.
        en caso de reintentar la generacion de una leccion.

        Retorna
        -------

        String: Texto de muestra.
    
    """

    dataset = load_from_disk(data_path)
    
    
    local_random = random.Random()
    local_random.seed(os.urandom(16)) 
    
    random_ids = local_random.sample(range(1, 120703), 10)
    samples = [dataset[id] for id in random_ids]
    selected_text = local_random.choice(samples)
    
    return selected_text

def getDatasetText() -> list:

    """
        Metodo para generar un 6 numeros dentro del rango del dataset y obtener los textos de muestra.
        en caso de reintentar la generacion de una leccion.

        Retorna
        -------

        Lista de textos de muestra.
    
    """

    dataset = load_from_disk(data_path)
    
    randomId = random.sample(range(1,120703),6)

    sample_text = list(map(lambda x: dataset[x],randomId))

    return sample_text


def split_qa(text: str) -> tuple[str, str]:

    """
        Metodo para separar la pregunta de la respuesta generadas por los modelos race y squad

        Retorna
        -------

        pregunta y respuesta en tupla.
    """

   
    separators = ['? ', ' . ']
    
    for sep in separators:
        last_index = text.rfind(sep)
        if last_index != -1:
           
            question = text[:last_index].strip()
            answer = text[last_index+len(sep):].strip()
            
           
            if question.endswith('?'):
                question = question[:-1].strip()
                
            return question, answer
    
    # Si no se encuentra ningún separador
    return text.strip(), ''


@celery.task(bind=True, max_retries=6)
def generate_lesson(self, dict_text) -> LessonData:

    """
        Metodo para generar las lecciones y verificar que sean adecuadas
        Una leccion es adecuada cuando se genera al menos un distractor diferente a la respuesta y,
        que el texto generado sea de minimo 100 caracteres.

        Retorna
        -------
        Objeto LessonData con la informacion de la leccion
    """


    gpt2 = Gpt2Model()
    raceQA = RaceModel()
    squadQA = SquadModel()
    distractor = DistractorModel()

    logger.warning("Generando lección.")

    try:
        sample_text = dict_text["text"]
        final_text = gpt2.generateText(sample_text)

        if len(final_text) < 150:
            logger.warning("Texto generado tiene menos de 150 caracteres. Reintentando...")
            raise ValueError("Texto generado demasiado corto")

 
        # Generar QA para Race
        qa_race = raceQA.generateQA(final_text)
        question_race, answer_race = split_qa(qa_race)

        
        
        # Validar Race
        if not question_race.strip() or not answer_race.strip():
            logger.warning("QA Race vacío. Reintentando...")
            raise ValueError("Race QA vacío")
        
        distractor_race = distractor.generate_distractors(question_race, final_text, answer_race)
        if distractor_race.lower() == answer_race.lower():
            logger.warning("Distractor Race igual a respuesta. Reintentando...")
            raise ValueError("Distractor Race inválido")
 

        # Generar QA para Squad
        qa_squad = squadQA.generateQA(final_text)
        question_squad, answer_squad = split_qa(qa_squad)
         
        # Validar Squad
        if not question_squad.strip() or not answer_squad.strip():
            logger.warning("QA Squad vacío. Reintentando...")
            raise ValueError("Squad QA vacío")
        

        distractor_squad = distractor.generate_distractors(question_squad, final_text, answer_squad)
        if distractor_squad.lower() == answer_squad.lower():
            logger.warning("Distractor Squad igual a respuesta. Reintentando...")
            raise ValueError("Distractor Squad inválido")
        


        # Crear lección si pasa todas las validaciones
        lessons_generated = LessonData(
            title=dict_text["title"],
            text=final_text,
            Questions=[
                Question(question=question_race, answer=answer_race, distractor=distractor_race),
                Question(question=question_squad, answer=answer_squad, distractor=distractor_squad)
            ]
        )
        
        logger.success("Lección generada con éxito")
        return lessons_generated.model_dump()

    except Exception as e:
        logger.warning(f"Error generando lección: {str(e)}")
        new_dict_text = getDatasetTextRetry()
        logger.info(f"Reintentando con nuevo dict_text: {new_dict_text}")
        self.retry(args=[new_dict_text], countdown=2, exc=e)


@celery.task(bind=True)     
def save_on_dbs(self, lessons):


    """
        Metodo para cuardar todas las lecciones y preguntas generadas en redis y postgres (neon)
        
        Retorna
        ------
        None (Solo guarda en cada base de datos.)

    """

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

    
            lesson_id = insert_lesson(lesson)

            insert_questions(lesson.Questions, lesson_id)

            
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

    """
        Metodo inicial de la generacion de lecciones.

        Retorna
        ------
        None. (pues son los metodos dentro del proceso que las cean.)

    """
   

    sample_text = getDatasetText()


    jobs = [generate_lesson.s(dict_text) for dict_text in sample_text]


    chord(jobs)(save_on_dbs.s())
