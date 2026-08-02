from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AssessmentCreate(BaseModel):

    titulo: str

    descricao: Optional[str] = None

    tipo: str

    data: datetime

    valor: int

    classroom_id: int

    subject_id: int


class AssessmentResponse(BaseModel):

    id: int

    titulo: str

    descricao: Optional[str]

    tipo: str

    data: datetime

    valor: int

    ativa: bool

    teacher_id: int

    classroom_id: int

    subject_id: int

    class Config:
        from_attributes = True