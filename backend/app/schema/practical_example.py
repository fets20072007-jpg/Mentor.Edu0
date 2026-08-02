from pydantic import BaseModel
from typing import Optional


class PracticalExampleCreate(BaseModel):

    titulo: str

    contexto: str

    explicacao: str

    curso_relacionado: Optional[str] = None


class PracticalExampleResponse(BaseModel):

    id: int

    titulo: str

    contexto: str

    explicacao: str

    curso_relacionado: Optional[str]

    chapter_id: int

    class Config:

        from_attributes = True