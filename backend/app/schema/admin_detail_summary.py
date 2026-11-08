from pydantic import BaseModel


class AdminTeacherSummaryResponse(BaseModel):
    user_id: int
    total_avaliacoes: int
    total_turmas: int
    total_alunos_avaliados: int


class AdminClassroomSummaryResponse(BaseModel):
    classroom_id: int
    total_avaliacoes: int
    total_professores: int
    total_alunos_avaliados: int
    percentual_medio: float
    status: str

class AdminStudentSummaryResponse(BaseModel):
    user_id: int
    total_avaliacoes: int
    total_disciplinas: int

    media_geral: float
    percentual_medio: float

    status: str