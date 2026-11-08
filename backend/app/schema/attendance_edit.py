from typing import Optional

from pydantic import BaseModel


class AttendanceEdit(BaseModel):

    status: str

    justificada: bool = False

    motivo: Optional[str] = None

    arquivo: Optional[str] = None

    observacao: Optional[str] = None