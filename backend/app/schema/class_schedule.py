from datetime import time
from typing import Optional

from pydantic import BaseModel


class ClassScheduleCreate(BaseModel):

    subject_id: int

    dia_semana: str

    hora_inicio: time

    hora_fim: time


class ClassScheduleUpdate(BaseModel):

    subject_id: Optional[int] = None

    dia_semana: Optional[str] = None

    hora_inicio: Optional[time] = None

    hora_fim: Optional[time] = None


class ClassScheduleResponse(BaseModel):

    id: int

    subject_id: int

    disciplina: str

    classroom_id: int

    turma: str

    teacher_id: int

    professor: str

    dia_semana: str

    hora_inicio: time

    hora_fim: time

    ativo: bool