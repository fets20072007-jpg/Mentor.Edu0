from pydantic import BaseModel
from typing import Optional


class StudentEvolutionResponse(BaseModel):
    ano_letivo: int
    semestre: Optional[int] = None

    avaliacoes_realizadas: int
    media: float
    percentual_medio: float
    status: str