from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TicketCreate(BaseModel):
    titulo: str
    descricao: str
    categoria: str = "Sistema"
    prioridade: str = "Media"
    destinatario_perfil: str = "Suporte"
    destinatario_user_id: Optional[int] = None


class ForgotPasswordRequest(BaseModel):
    email: str


class TicketStatusUpdate(BaseModel):
    status: str
    solucao: Optional[str] = None


class TicketRecipientResponse(BaseModel):
    perfil: str
    user_id: Optional[int] = None
    nome: str
    detalhe: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    categoria: str
    prioridade: str
    destinatario_perfil: str = "Suporte"
    destinatario_user_id: Optional[int] = None
    destinatario_nome: Optional[str] = None
    status: str
    solucao: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
    requester_id: int
    assigned_support_id: Optional[int] = None

    class Config:
        from_attributes = True
