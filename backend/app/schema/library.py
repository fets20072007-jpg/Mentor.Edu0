from pydantic import BaseModel
from typing import Optional


class LibraryBookCreate(BaseModel):

    titulo: str

    autor: str

    disciplina: str

    serie: Optional[str] = None

    descricao: Optional[str] = None

    arquivo_pdf: Optional[str] = None


class LibraryBookResponse(BaseModel):

    id: int

    titulo: str

    autor: str

    disciplina: str

    serie: Optional[str] = None

    descricao: Optional[str] = None

    arquivo_pdf: Optional[str] = None

    ativo: bool

    class Config:
        from_attributes = True