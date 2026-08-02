from pydantic import BaseModel


class EnrollmentCreate(BaseModel):

    user_id: int

    classroom_id: int


class EnrollmentResponse(BaseModel):

    id: int

    user_id: int

    classroom_id: int

    ativo: bool

    class Config:
        from_attributes = True