from pydantic import BaseModel
from typing import Optional


class StudentSummaryResponse(BaseModel):
    avaliacoes_realizadas: int

    media_geral: float
    percentual_medio: float

    melhor_nota: Optional[float] = None
    pior_nota: Optional[float] = None

    melhor_percentual: Optional[float] = None
    pior_percentual: Optional[float] = None

    status_geral: str