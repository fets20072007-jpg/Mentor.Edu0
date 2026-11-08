from pydantic import BaseModel
from typing import Optional


# =========================================================
# CADASTRO DE USUÁRIO
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
    # Só serão utilizados quando tipo == "Professor".
    # -----------------------------------------------------

    cpf: Optional[str] = None
    matricula: Optional[str] = None
    telefone: Optional[str] = None
    especialidade: Optional[str] = None
    carga_horaria: int = 40


# =========================================================
# ATUALIZAÇÃO DO PRÓPRIO PERFIL
# =========================================================

class UserUpdate(BaseModel):

    nome: Optional[str] = None
    email: Optional[str] = None

    bio: Optional[str] = None
    escola: Optional[str] = None
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