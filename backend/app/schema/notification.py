from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):

    id: int

    titulo: str

    mensagem: str

    tipo: str

    link: Optional[str] = None

    lida: bool

    criado_em: datetime

    lida_em: Optional[datetime] = None

    user_id: int

    class Config:
        from_attributes = True


class NotificationCountResponse(BaseModel):

    nao_lidas: int