from pydantic import BaseModel


class TeacherClassroomSummaryResponse(BaseModel):
    classroom_id: int

    avaliacoes_criadas: int
    alunos_avaliados: int

    media_turma: float
    percentual_medio: float

    status: str