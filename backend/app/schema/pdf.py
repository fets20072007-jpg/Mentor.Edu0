from pydantic import BaseModel
from typing import Optional


class PDFCreate(BaseModel):

    titulo: str

    descricao: Optional[str] = None

    arquivo: str

    paginas: Optional[int] = None


class PDFResponse(BaseModel):

    id: int

    titulo: str

    descricao: Optional[str]

    arquivo: str

    paginas: Optional[int]

    chapter_id: int

    class Config:

        from_attributes = True