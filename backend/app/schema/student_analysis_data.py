from pydantic import BaseModel
from typing import Optional


class AnalysisContentDifficulty(BaseModel):
    subject_id: int
    categoria: str
    percentual_medio: float
    status: str


class AnalysisCriticalQuestion(BaseModel):
    question_id: int
    categoria: Optional[str] = None
    percentual_erro: float


class StudentAnalysisDataResponse(BaseModel):
    student_id: int
    nome: str

    media_geral: float
    percentual_medio: float
    status: str

    conteudos_com_dificuldade: list[
        AnalysisContentDifficulty
    ]

    questoes_criticas: list[
        AnalysisCriticalQuestion
    ]