from pydantic import BaseModel
from typing import Optional


# =========================================================
# CADASTRO DE USUÃRIO
# =========================================================

class UserCreate(BaseModel):

    nome: str
    email: str
    senha: str
    tipo: str

    # -----------------------------------------------------
    # CAMPOS GERAIS
    # -----------------------------------------------------

    bio: Optional[str] = None
    escola: Optional[str] = None
    contato1: Optional[str] = None
    contato2: Optional[str] = None
    serie: Optional[str] = None
    idade: Optional[int] = None

    objetivo: Optional[str] = None
    materias_favoritas: Optional[str] = None
    dificuldades: Optional[str] = None
    horas_estudo: Optional[int] = None

    # -----------------------------------------------------
    # ALUNO
    # -----------------------------------------------------

    classroom_id: Optional[int] = None

    # -----------------------------------------------------
    # PROFESSOR
    #
    # SÃ³ serÃ£o utilizados quando tipo == "Professor".
    # -----------------------------------------------------

    cpf: Optional[str] = None
    matricula: Optional[str] = None
    telefone: Optional[str] = None
    especialidade: Optional[str] = None
    carga_horaria: int = 40


# =========================================================
# ATUALIZAÃ‡ÃƒO DO PRÃ“PRIO PERFIL
# =========================================================

class UserUpdate(BaseModel):

    nome: Optional[str] = None
    email: Optional[str] = None

    bio: Optional[str] = None
    escola: Optional[str] = None
    contato1: Optional[str] = None
    contato2: Optional[str] = None
    serie: Optional[str] = None
    idade: Optional[int] = None

    objetivo: Optional[str] = None
    materias_favoritas: Optional[str] = None
    dificuldades: Optional[str] = None
    horas_estudo: Optional[int] = None


# =========================================================
# RESPOSTA
# =========================================================

class UserResponse(BaseModel):

    id: int
    nome: str
    email: str
    tipo: str

    bio: Optional[str]
    escola: Optional[str]
    serie: Optional[str]
    idade: Optional[int]

    objetivo: Optional[str]
    materias_favoritas: Optional[str]
    dificuldades: Optional[str]
    horas_estudo: Optional[int]

    classroom_id: Optional[int] = None

    class Config:
        from_attributes = True
