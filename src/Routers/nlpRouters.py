from fastapi import APIRouter
from sentence_transformers import CrossEncoder
from pydantic import BaseModel


nlpROuter = APIRouter()


class SentenceRequest(BaseModel):
    sentence: str


@nlpROuter.post('/Semantic_similarity')
async def model(request: SentenceRequest):
    model_name = "cross-encoder/stsb-roberta-base"
    model1 = CrossEncoder(model_name)
    
    # Si solo tienes una frase, la comparas con una frase predeterminada o con otra frase enviada
    other_sentence = "This is a reference sentence"  # Puedes cambiar esta frase por una dinámica
    predict = str(model1.predict((request.sentence, other_sentence)))
    
    return {"prediction": predict}
