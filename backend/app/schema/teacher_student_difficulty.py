from pydantic import BaseModel


class TeacherStudentDifficultyResponse(BaseModel):
    student_id: int
    nome: str

    avaliacoes_realizadas: int

    media: float
    percentual_medio: float

    status: str