from pydantic import BaseModel
from typing import Optional


class BookCreate(BaseModel):

    titulo: str

    disciplina: str

    autor: str

    editora: Optional[str] = None

    ano: Optional[int] = None

    quantidade_capitulos: int = 0

    pdf_url: Optional[str] = None

    descricao: Optional[str] = None


class BookResponse(BaseModel):

    id: int

    titulo: str

    disciplina: str

    autor: str

    editora: Optional[str]

    ano: Optional[int]

    quantidade_capitulos: int

    pdf_url: Optional[str]

    descricao: Optional[str]

    class Config:

        from_attributes = True