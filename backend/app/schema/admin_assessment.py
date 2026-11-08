from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdminAssessmentResponse(BaseModel):
    assessment_id: int
    titulo: str
    descricao: Optional[str] = None
    tipo: str

    data: Optional[datetime] = None
    valor: float
    ativa: bool

    semestre: Optional[int] = None
    ano_letivo: Optional[int] = None

    teacher_id: int
    classroom_id: int
    subject_id: int