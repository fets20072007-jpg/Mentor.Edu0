from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):

    nome: str
    email: str
    senha: str

    tipo: str

    bio: Optional[str] = None
    escola: Optional[str] = None
    serie: Optional[str] = None
    idade: Optional[int] = None

    objetivo: Optional[str] = None
    materias_favoritas: Optional[str] = None
    dificuldades: Optional[str] = None
    horas_estudo: Optional[int] = None


class UserUpdate(BaseModel):

    nome: Optional[str] = None

    bio: Optional[str] = None
    escola: Optional[str] = None
    serie: Optional[str] = None
    idade: Optional[int] = None

    objetivo: Optional[str] = None
    materias_favoritas: Optional[str] = None
    dificuldades: Optional[str] = None
    horas_estudo: Optional[int] = None


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

    class Config:
        from_attributes = True