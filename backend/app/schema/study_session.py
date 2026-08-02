from pydantic import BaseModel
from typing import Optional


class StudySessionCreate(BaseModel):
    materia: str
    assunto: str
    duracao_minutos: int
    dificuldade_sentida: Optional[int] = None
    concluida: bool = False
    data_sessao: Optional[str] = None
    observacoes: Optional[str] = None


class StudySessionUpdate(BaseModel):
    materia: Optional[str] = None
    assunto: Optional[str] = None
    duracao_minutos: Optional[int] = None
    dificuldade_sentida: Optional[int] = None
    concluida: Optional[bool] = None
    data_sessao: Optional[str] = None
    observacoes: Optional[str] = None


class StudySessionResponse(BaseModel):
    id: int
    materia: str
    assunto: str
    duracao_minutos: int
    dificuldade_sentida: Optional[int] = None
    concluida: bool
    data_sessao: Optional[str] = None
    observacoes: Optional[str] = None
    user_id: int

    class Config:
        from_attributes = True