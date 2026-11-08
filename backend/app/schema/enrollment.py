from pydantic import BaseModel
from datetime import datetime


class EnrollmentCreate(BaseModel):

    user_id: int
    classroom_id: int


class EnrollmentTransfer(BaseModel):

    classroom_id: int


class EnrollmentResponse(BaseModel):

    id: int

    data_matricula: datetime

    ativo: bool

    user_id: int

    classroom_id: int

    class Config:
        from_attributes = True