from pydantic import BaseModel


class QuestionDifficultyResponse(BaseModel):
    question_id: int
    categoria: str | None = None

    total_respostas: int
    respostas_com_erro: int

    percentual_erro: float
    dificuldade: str