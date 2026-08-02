from pydantic import BaseModel


class LearningHistoryResponse(BaseModel):

    id: int

    materia: str

    percentual: int

    tempo_medio: int

    observacao: str

    user_id: int

    class Config:

        from_attributes = True