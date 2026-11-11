from pydantic import BaseModel
from typing import Optional

class StudyPlanCreate(BaseModel):
    titulo: str
    meta: str
    horas_dia: int
    materias: str
    dificuldade: str
    material_url: Optional[str] = None
    arquivo: Optional[str] = None

class StudyPlanUpdate(BaseModel):
    titulo: str | None = None
    meta: str | None = None
    horas_dia: int | None = None
    materias: str | None = None
    dificuldade: str | None = None
    material_url: str | None = None
    arquivo: str | None = None

class StudyPlanResponse(BaseModel):
    id: int
    titulo: str
    meta: str
    horas_dia: int
    materias: str
    dificuldade: str
    material_url: Optional[str] = None
    arquivo: Optional[str] = None
    user_id: int
    class Config:
        from_attributes = True
