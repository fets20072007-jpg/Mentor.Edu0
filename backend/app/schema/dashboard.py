from pydantic import BaseModel


class StudentDashboard(BaseModel):

    nome: str

    horas_estudo: int

    questoes_respondidas: int

    acertos: int

    erros: int

    tempo_medio: int

    livros_recomendados: int

    ultima_recomendacao: str