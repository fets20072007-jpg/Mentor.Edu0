from pydantic import BaseModel


class StudentContentDifficultyResponse(BaseModel):
    subject_id: int
    categoria: str

    questoes_respondidas: int

    percentual_medio: float
    status: str