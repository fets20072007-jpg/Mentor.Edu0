from pydantic import BaseModel
from typing import Optional

class SubjectCreate(BaseModel):
    nome: str
    carga_horaria: int = 80
    descricao: Optional[str] = None
    categoria: str = "Outras"
    teacher_id: int
    classroom_id: int

class SubjectUpdate(BaseModel):
    nome: Optional[str] = None
    carga_horaria: Optional[int] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    teacher_id: Optional[int] = None
    classroom_id: Optional[int] = None
    ativa: Optional[bool] = None

class SubjectResponse(BaseModel):
    id: int
    nome: str
    carga_horaria: int
    descricao: Optional[str]
    categoria: str = "Outras"
    ativa: bool
    teacher_id: int
    classroom_id: int
    classroom_nome: Optional[str] = None
    class Config:
        from_attributes = True

class SubjectTeacherUpdate(BaseModel):
    teacher_id: int
