from pydantic import BaseModel
from typing import Optional
from typing import List

class TeacherCreate(BaseModel):

    nome: str

    email: str

    cpf: str

    matricula: str

    telefone: Optional[str] = None

    especialidade: str

    carga_horaria: int = 40


class TeacherResponse(BaseModel):

    id: int

    nome: str

    email: str

    cpf: str

    matricula: str

    telefone: Optional[str]

    especialidade: str

    carga_horaria: int

    ativo: bool

    class Config:
        from_attributes = True



class StudentSimple(BaseModel):

    id: int

    nome: str

    class Config:
        from_attributes = True


class TeacherClassroomResponse(BaseModel):

    turma: str

    disciplina: str

    serie: str

    turno: str

    ano: int

    alunos: List[StudentSimple]