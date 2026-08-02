from pydantic import BaseModel
from typing import Optional


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

    student_id: int

    classroom_id: int

    subject_id: int

    status: str

    justificada: bool

    motivo: Optional[str]

    arquivo: Optional[str]

    observacao: Optional[str]

    class Config:
        from_attributes = True