from celery_app import celery


@celery.task

def generate_lessons():

    for _ in range(10):

        #pasos para tener el generador:
            #1. metodo en servicios para brindar un texto de ejemplo random del dataset
            # 2. pasar el texto a gpt2
            # 3. pasar el texto generado a los modelos de preguntas
            # 4. Enviar a redis como k/v y a postgres como el esquema de tabla que tiene
            # 5. hacer pruebas de cada 10 min y verificar que se generen todas las 10 lecciones en ese plazo 
            # 6. no se que mas si alguien ve esto se gana el baloto. 
        get_text_set = "aqui va el texto de ejemplo del dataset"
        generated_text = "hi"
        race_response ="hi"
        squad_response ="Hi"

        #logica para guardar las lecciones