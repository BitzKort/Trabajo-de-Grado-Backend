from fastapi import APIRouter
from pydantic import BaseModel
import os
from sentence_transformers import CrossEncoder
from transformers import pipeline, set_seed, AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM


modules_path = './nplModules'
gpt_path = os.path.join(modules_path, 'gpt2')
stb_path = os.path.join(modules_path, 'stb')
question_path = os.path.join(modules_path,'QAGen')
print(stb_path)
os.makedirs(modules_path, exist_ok=True)
os.makedirs(gpt_path, exist_ok=True)
os.makedirs(stb_path, exist_ok=True)
os.makedirs(question_path, exist_ok=True)


nlpRouter = APIRouter()


class SentenceRequest(BaseModel):
    sentence1: str
    sentence2: str


@nlpRouter.get('/questionCard')

async def question():

    #save the models
    generator = pipeline('text-generation', model='gpt2-medium')

    generator.model.save_pretrained(gpt_path)
    generator.tokenizer.save_pretrained(gpt_path)


    qAGenerator = pipeline("text2text-generation", model="potsawee/t5-large-generation-race-Distractor")

    qAGenerator.model.save_pretrained(question_path)
    qAGenerator.tokenizer.save_pretrained(question_path)

    

    #load the models

    model = AutoModelForCausalLM.from_pretrained(gpt_path)
    tokenizer = AutoTokenizer.from_pretrained(gpt_path)
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer)



    questionTokenizer = AutoTokenizer.from_pretrained(question_path)
    questionModel = AutoModelForSeq2SeqLM.from_pretrained(question_path)
    qAGenerator = pipeline("text2text-generation", model=questionModel, tokenizer=questionTokenizer)


    
    #models creations

    set_seed(42)
    results = generator("Hi, I'm a teacher of math", max_length=60, num_return_sequences=1)

    print(results)

    output = qAGenerator(results[0]['generated_text'], max_length=100, clean_up_tokenization_spaces=True)
    question_answer = output[0]["generated_text"]

    # Procesar para obtener pregunta y respuesta
    question_answer = question_answer.replace(questionTokenizer.pad_token, "").replace(questionTokenizer.eos_token, "")
    question, answer = question_answer.split(questionTokenizer.sep_token)

    print(question)
    print(answer)








    

@nlpRouter.post('/Semantic_similarity')
async def model(request: SentenceRequest):
    model_path = "cross-encoder/stsb-roberta-base"
    model1 = CrossEncoder(model_path, cache_dir = './nplModules/similarity')
    predict = str(model1.predict((request.sentence1, request.sentence2)))
    
    return {"prediction": predict}
