from pydantic import BaseModel

from typing import List


class DayRecommendation(BaseModel):

    dia: str

    horas: int

    materias: List[str]