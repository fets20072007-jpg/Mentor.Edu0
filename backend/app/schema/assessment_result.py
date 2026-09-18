from pydantic import BaseModel


class AssessmentResultResponse(BaseModel):
    assessment_id: int
    user_id: int

    total_questoes: int
    questoes_respondidas: int
    questoes_corrigidas: int
    questoes_pendentes: int

    pontos_obtidos: float
    pontos_possiveis: float

    percentual: float
    nota_final: float