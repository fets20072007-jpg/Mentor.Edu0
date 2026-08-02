from pydantic import BaseModel


class PerformanceResponse(BaseModel):

    total_questoes: int

    acertos: int

    erros: int

    percentual: float

    tempo_medio: float

    nivel: str