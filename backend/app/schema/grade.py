from pydantic import BaseModel
from typing import Optional

class GradeCreate(BaseModel):

    assessment_id: int

    student_id: int

    nota: float

    observacao: Optional[str] = None


class GradeResponse(BaseModel):

    id: int

    assessment_id: int

    student_id: int

    nota: float

    observacao: Optional[str]

    class Config:
        from_attributes = True