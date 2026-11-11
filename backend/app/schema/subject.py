from pydantic import BaseModel
from typing import Optional

class SubjectCreate(BaseModel):
    nome: str
    carga_horaria: int = 80
    descricao: Optional[str] = None
    categoria: str = "Outras"
    teacher_id: int
    classroom_id: int

class SubjectResponse(BaseModel):
    id: int
    nome: str
    carga_horaria: int
    descricao: Optional[str]
    categoria: str = "Outras"
    ativa: bool
    teacher_id: int
    classroom_id: int
    class Config:
        from_attributes = True

class SubjectTeacherUpdate(BaseModel):
    teacher_id: int
