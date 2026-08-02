from pydantic import BaseModel


class ClassroomCreate(BaseModel):

    nome: str

    serie: str

    turno: str

    sala: str

    ano: int

    capacidade: int = 40

    teacher_id: int | None = None


class ClassroomResponse(BaseModel):

    id: int

    nome: str

    serie: str

    turno: str

    sala: str

    ano: int

    capacidade: int

    ativa: bool

    teacher_id: int | None

    class Config:
        from_attributes = True