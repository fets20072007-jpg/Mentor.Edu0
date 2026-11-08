from pydantic import BaseModel
from typing import Optional


class QuestionStudentResponse(BaseModel):
    id: int

    tipo: str
    enunciado: str

    alternativa_a: Optional[str] = None
    alternativa_b: Optional[str] = None
    alternativa_c: Optional[str] = None
    alternativa_d: Optional[str] = None

    dificuldade: str
    peso: float

    categoria: Optional[str] = None

    chapter_id: Optional[int] = None
    assessment_id: Optional[int] = None

    class Config:
        from_attributes = True