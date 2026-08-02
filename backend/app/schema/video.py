from pydantic import BaseModel
from typing import Optional


class VideoCreate(BaseModel):

    titulo: str

    descricao: Optional[str] = None

    url: str

    duracao: Optional[str] = None

    plataforma: str = "YouTube"


class VideoResponse(BaseModel):

    id: int

    titulo: str

    descricao: Optional[str]

    url: str

    duracao: Optional[str]

    plataforma: str

    chapter_id: int

    class Config:

        from_attributes = True