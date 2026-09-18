from pydantic import BaseModel


class AssessmentStudentResultResponse(BaseModel):
    user_id: int
    nome: str

    percentual: float
    nota_final: float

    questoes_respondidas: int
    questoes_corrigidas: int
    questoes_pendentes: int