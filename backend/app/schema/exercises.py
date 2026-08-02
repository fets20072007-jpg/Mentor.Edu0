from pydantic import BaseModel
from typing import Optional


class ExerciseCreate(BaseModel):

    pergunta: str

    alternativa_a: str

    alternativa_b: str

    alternativa_c: str

    alternativa_d: str

    resposta_correta: str

    explicacao: Optional[str] = None

    dificuldade: str = "Média"


class ExerciseResponse(BaseModel):

    id: int

    pergunta: str

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