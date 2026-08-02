from pydantic import BaseModel


class StudyPlanCreate(BaseModel):
    titulo: str
    meta: str
    horas_dia: int
    materias: str
    dificuldade: str


class StudyPlanUpdate(BaseModel):
    titulo: str | None = None
    meta: str | None = None
    horas_dia: int | None = None
    materias: str | None = None
    dificuldade: str | None = None


class StudyPlanResponse(BaseModel):
    id: int
    titulo: str
    meta: str
    horas_dia: int
    materias: str
    dificuldade: str
    user_id: int

    class Config:
        from_attributes = True