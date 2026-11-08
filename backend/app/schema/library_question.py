from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LibraryQuestionCreate(BaseModel):

    subject_id: int

    tipo: str = "Objetiva"

    enunciado: str

    alternativa_a: Optional[str] = None
    alternativa_b: Optional[str] = None
    alternativa_c: Optional[str] = None
    alternativa_d: Optional[str] = None

    resposta_correta: Optional[str] = None
    explicacao: Optional[str] = None

    dificuldade: str = "Médio"

    categoria: Optional[str] = None

    criterio_0: Optional[str] = None
    criterio_25: Optional[str] = None
    criterio_50: Optional[str] = None
    criterio_75: Optional[str] = None
    criterio_100: Optional[str] = None

    compartilhada: bool = False


class LibraryQuestionUpdate(BaseModel):

    tipo: Optional[str] = None

    enunciado: Optional[str] = None

    alternativa_a: Optional[str] = None
    alternativa_b: Optional[str] = None
    alternativa_c: Optional[str] = None
    alternativa_d: Optional[str] = None

    resposta_correta: Optional[str] = None
    explicacao: Optional[str] = None

    dificuldade: Optional[str] = None
    categoria: Optional[str] = None

    criterio_0: Optional[str] = None
    criterio_25: Optional[str] = None
    criterio_50: Optional[str] = None
    criterio_75: Optional[str] = None
    criterio_100: Optional[str] = None

    compartilhada: Optional[bool] = None


class LibraryQuestionResponse(BaseModel):

    id: int

    teacher_id: int
    subject_id: int

    tipo: str

    enunciado: str

    alternativa_a: Optional[str]
    alternativa_b: Optional[str]
    alternativa_c: Optional[str]
    alternativa_d: Optional[str]

    resposta_correta: Optional[str]
    explicacao: Optional[str]

    dificuldade: str
    categoria: Optional[str]

    criterio_0: Optional[str]
    criterio_25: Optional[str]
    criterio_50: Optional[str]
    criterio_75: Optional[str]
    criterio_100: Optional[str]

    compartilhada: bool
    ativa: bool

    criado_em: datetime

    class Config:
        from_attributes = True