from pydantic import BaseModel
from typing import Optional


class AdminTeacherResponse(BaseModel):
    user_id: int
    nome: str
    email: str
    especialidade: Optional[str] = None
    ativo: bool


class AdminStudentResponse(BaseModel):
    user_id: int
    nome: str
    email: str
    escola: Optional[str] = None
    serie: Optional[str] = None