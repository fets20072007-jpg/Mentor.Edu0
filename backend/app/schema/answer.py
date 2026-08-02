from pydantic import BaseModel
from typing import Optional


class StudentAnswerCreate(BaseModel):

    resposta: str

    tempo_resposta: Optional[int] = None


class StudentAnswerResponse(BaseModel):

    id: int

    resposta: str

    correta: bool

    tempo_resposta: Optional[int]

    question_id: int

    user_id: int

    class Config:

        from_attributes = True