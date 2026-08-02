from pydantic import BaseModel


class SubjectPerformance(BaseModel):
    disciplina: str
    media: float
    frequencia: float
    situacao: str


class AcademicRecordResponse(BaseModel):
    aluno: str
    turma: str
    disciplinas: list[SubjectPerformance]