from pydantic import BaseModel
from typing import Optional


class AssessmentHistoryResponse(BaseModel):
    assessment_id: int
    titulo: str

    subject_id: int
    classroom_id: int
    teacher_id: int

    tipo: str

    semestre: Optional[int] = None
    ano_letivo: Optional[int] = None

    percentual: float
    nota_final: float

    status_desempenho: str