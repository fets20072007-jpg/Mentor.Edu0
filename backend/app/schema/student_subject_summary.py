from pydantic import BaseModel


class StudentSubjectSummaryResponse(BaseModel):
    subject_id: int
    avaliacoes_realizadas: int
    media: float
    percentual_medio: float
    status: str