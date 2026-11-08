from pydantic import BaseModel
from typing import Optional


class AdminClassroomResponse(BaseModel):
    classroom_id: int
    nome: str
    ano_letivo: Optional[int] = None