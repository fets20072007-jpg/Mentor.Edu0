from pydantic import BaseModel
from typing import Optional


class QuestionCreate(BaseModel):

    tipo: str = "Objetiva"

    enunciado: str

    alternativa_a: Optional[str] = None
    alternativa_b: Optional[str] = None
    alternativa_c: Optional[str] = None
    alternativa_d: Optional[str] = None

    resposta_correta: Optional[str] = None

    explicacao: Optional[str] = None

    dificuldade: str = "Médio"

    peso: float = 1.0

    categoria: Optional[str] = None

    criterio_0: Optional[str] = None
    criterio_25: Optional[str] = None
    criterio_50: Optional[str] = None
    criterio_75: Optional[str] = None
    criterio_100: Optional[str] = None

    chapter_id: Optional[int] = None

    assessment_id: Optional[int] = None


class QuestionResponse(BaseModel):

    id: int

    tipo: str

    enunciado: str

    alternativa_a: Optional[str]
    alternativa_b: Optional[str]
    alternativa_c: Optional[str]
    alternativa_d: Optional[str]

    resposta_correta: Optional[str]

    explicacao: Optional[str]

    dificuldade: str

    peso: float

    categoria: Optional[str]

    criterio_0: Optional[str]
    criterio_25: Optional[str]
    criterio_50: Optional[str]
    criterio_75: Optional[str]
    criterio_100: Optional[str]

    chapter_id: Optional[int]

    assessment_id: Optional[int]

    class Config:
        from_attributes = True