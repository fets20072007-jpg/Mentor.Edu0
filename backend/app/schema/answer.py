from pydantic import BaseModel
from typing import Optional


class StudentAnswerCreate(BaseModel):
    resposta: str
    tempo_resposta: Optional[int] = None


class StudentAnswerUpdate(BaseModel):
    percentual_professor: Optional[float] = None


class StudentAnswerResponse(BaseModel):
    id: int

    resposta: str
    tempo_resposta: Optional[int] = None

    percentual_ia: Optional[float] = None
    justificativa_ia: Optional[str] = None

    percentual_professor: Optional[float] = None
    percentual_final: Optional[float] = None

    pontuacao_obtida: Optional[float] = None

    corrigida_ia: bool
    revisada_professor: bool

    question_id: int
    user_id: int

    class Config:
        from_attributes = True