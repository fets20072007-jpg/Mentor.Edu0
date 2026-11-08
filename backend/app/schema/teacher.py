from pydantic import BaseModel
from typing import Optional, List


# =========================================================
# PROFESSOR
# =========================================================

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


# =========================================================
# ALUNO SIMPLES
# =========================================================

class StudentSimple(BaseModel):

    id: int
    nome: str

    class Config:
        from_attributes = True


# =========================================================
# TURMA EM QUE O PROFESSOR ATUA
# =========================================================

class TeacherClassroomResponse(BaseModel):

    classroom_id: int

    turma: str
    serie: str
    turno: str
    ano: int

    is_dt: bool

    disciplinas: List[str]

    alunos: List[StudentSimple]


# =========================================================
# PROFESSOR PRESENTE EM UMA TURMA
# =========================================================

class ClassroomTeacherResponse(BaseModel):

    teacher_id: int

    nome: str
    especialidade: str

    is_dt: bool

    disciplinas: List[str]