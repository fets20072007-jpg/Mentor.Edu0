from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# =========================================================
# CRIAÃ‡ÃƒO DE AVALIAÃ‡ÃƒO
# =========================================================

class AssessmentCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None

    tipo: str
    arquivo: Optional[str] = None
    arquivo_nome: Optional[str] = None
    data: Optional[datetime] = None

    valor: float = 10
    ativa: bool = True

    semestre: Optional[int] = None
    ano_letivo: Optional[int] = None

    subject_id: int


# =========================================================
# RESPOSTA DA AVALIAÃ‡ÃƒO
# =========================================================

class AssessmentResponse(BaseModel):
    id: int

    titulo: str

    descricao: Optional[str] = None

    tipo: str
    arquivo: Optional[str] = None
    arquivo_nome: Optional[str] = None

    data: Optional[datetime] = None

    valor: float

    ativa: bool

    semestre: Optional[int] = None

    ano_letivo: Optional[int] = None

    teacher_id: int

    classroom_id: int

    subject_id: int

    class Config:
        from_attributes = True


# =========================================================
# EDIÃ‡ÃƒO DE AVALIAÃ‡ÃƒO
# =========================================================

class AssessmentUpdate(BaseModel):
    titulo: Optional[str] = None

    descricao: Optional[str] = None

    tipo: Optional[str] = None

    data: Optional[datetime] = None

    valor: Optional[float] = None

    ativa: Optional[bool] = None

    semestre: Optional[int] = None

    ano_letivo: Optional[int] = None

    subject_id: Optional[int] = None
