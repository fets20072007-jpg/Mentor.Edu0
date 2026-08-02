from pydantic import BaseModel
from typing import List


class SmartRecommendation(BaseModel):

    materia: str

    motivo: str

    livro: str

    capitulo: str

    paginas: str

    video: str

    exercicios: int

    exemplo_pratico: str