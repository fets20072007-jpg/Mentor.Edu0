from pydantic import BaseModel
from typing import Optional


class ChapterCreate(BaseModel):

    titulo: str

    numero: int

    pagina_inicio: int

    pagina_fim: int

    descricao: Optional[str] = None


class ChapterResponse(BaseModel):

    id: int

    titulo: str

    numero: int

    pagina_inicio: int

    pagina_fim: int

    descricao: Optional[str]

    book_id: int

    class Config:

        from_attributes = True