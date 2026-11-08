from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AttendanceCreate(BaseModel):
    student_id: int
    classroom_id: int
    subject_id: int

    status: str

    justificada: bool = False
    motivo: Optional[str] = None
    arquivo: Optional[str] = None
    observacao: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: int
    data: datetime

    status: str
    justificada: bool

    motivo: Optional[str] = None
    arquivo: Optional[str] = None
    observacao: Optional[str] = None

    teacher_id: int
    student_id: int
    classroom_id: int
    subject_id: int

    class Config:
        from_attributes = True

class AttendanceJustification(BaseModel):
    motivo: str
    arquivo: Optional[str] = None
    observacao: Optional[str] = None