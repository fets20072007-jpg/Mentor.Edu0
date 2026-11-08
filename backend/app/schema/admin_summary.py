from pydantic import BaseModel


class AdminSummaryResponse(BaseModel):
    total_alunos: int
    total_professores: int
    total_turmas: int
    total_avaliacoes: int
    avaliacoes_ativas: int