from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AssessmentCreate(BaseModel):
    titulo: str

    descricao: Optional[str] = None

    tipo: str

    data: Optional[datetime] = None

    valor: float = 10

    ativa: bool = True

    semestre: Optional[int] = None

    ano_letivo: Optional[int] = None

    classroom_id: int

    subject_id: int


class AssessmentResponse(BaseModel):
    id: int

    titulo: str
    descricao: Optional[str]

    tipo: str

    data: Optional[datetime]

    valor: float

    ativa: bool

    semestre: Optional[int]

    ano_letivo: Optional[int]

    teacher_id: int
    classroom_id: int
    subject_id: int

    class Config:
        from_attributes = True

class AssessmentUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    data: Optional[datetime] = None
    valor: Optional[float] = None
    ativa: Optional[bool] = None
    semestre: Optional[int] = None
    ano_letivo: Optional[int] = None
    classroom_id: Optional[int] = None
    subject_id: Optional[int] = None