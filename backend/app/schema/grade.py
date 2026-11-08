from pydantic import BaseModel, Field
from typing import Optional


class GradeCreate(BaseModel):

    assessment_id: int
    student_id: int

    nota: float = Field(
        ge=0
    )

    observacao: Optional[str] = None


class GradeUpdate(BaseModel):

    nota: Optional[float] = Field(
        default=None,
        ge=0
    )

    observacao: Optional[str] = None


class GradeResponse(BaseModel):

    id: int

    assessment_id: int
    student_id: int

    nota: float

    observacao: Optional[str] = None

    class Config:
        from_attributes = True