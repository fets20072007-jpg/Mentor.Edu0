from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    mensagem: str = Field(
        min_length=1,
        max_length=6000,
    )


class AIQuestionRequest(BaseModel):
    disciplina: str
    assunto: str
    serie: str | None = None
    curso_tecnico: str | None = None

    quantidade: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    dificuldade: str = "Médio"

    alternativas: int = Field(
        default=5,
        ge=4,
        le=5,
    )


class AILessonPlanRequest(BaseModel):
    disciplina: str
    assunto: str
    serie: str | None = None

    duracao_minutos: int = Field(
        default=50,
        ge=20,
        le=300,
    )

    curso_tecnico: str | None = None
    recursos_disponiveis: list[str] = []
    observacoes: str | None = None
