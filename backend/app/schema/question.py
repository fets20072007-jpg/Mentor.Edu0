from pydantic import BaseModel
from typing import Optional


class QuestionCreate(BaseModel):

    enunciado: str

    alternativa_a: str
    alternativa_b: str
    alternativa_c: str
    alternativa_d: str

    resposta_correta: str

    explicacao: Optional[str] = None

    dificuldade: Optional[str] = "Médio"


class QuestionResponse(BaseModel):

    id: int

    enunciado: str

    alternativa_a: str
    alternativa_b: str
    alternativa_c: str
    alternativa_d: str

    resposta_correta: str

    explicacao: Optional[str]

    dificuldade: str

    chapter_id: int

    class Config:

        from_attributes = True