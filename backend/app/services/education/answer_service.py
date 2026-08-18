from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import (
    Question,
    StudentAnswer,
    User
)


def calcular_pontuacao(
    peso: float,
    percentual: float
):
    return peso * (percentual / 100)


def register_answer(
    db: Session,
    question_id: int,
    user: User,
    data
):

    question = (
        db.query(Question)
        .filter(Question.id == question_id)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Questão não encontrada."
        )

    percentual_ia = None
    justificativa_ia = None
    percentual_final = None
    pontuacao_obtida = None
    corrigida_ia = False

    # Correção automática para questões objetivas
    if (
        question.tipo
        and question.tipo.lower() == "objetiva"
        and question.resposta_correta
    ):

        resposta_aluno = data.resposta.upper().strip()

        resposta_correta = (
            question.resposta_correta
            .upper()
            .strip()
        )

        if resposta_aluno == resposta_correta:

            percentual_final = 100.0

        else:

            percentual_final = 0.0

        pontuacao_obtida = calcular_pontuacao(
            question.peso or 1,
            percentual_final
        )

    answer = StudentAnswer(

        resposta=data.resposta,

        tempo_resposta=data.tempo_resposta,

        percentual_ia=percentual_ia,

        justificativa_ia=justificativa_ia,

        percentual_professor=None,

        percentual_final=percentual_final,

        pontuacao_obtida=pontuacao_obtida,

        corrigida_ia=corrigida_ia,

        revisada_professor=False,

        question_id=question.id,

        user_id=user.id

    )

    db.add(answer)

    db.commit()

    db.refresh(answer)

    return answer

def review_answer(
    db: Session,
    answer_id: int,
    percentual_professor: float
):

    if percentual_professor not in [0, 25, 50, 75, 100]:
        raise HTTPException(
            status_code=400,
            detail="Percentual deve ser 0, 25, 50, 75 ou 100."
        )

    answer = (
        db.query(StudentAnswer)
        .filter(StudentAnswer.id == answer_id)
        .first()
    )

    if not answer:
        raise HTTPException(
            status_code=404,
            detail="Resposta não encontrada."
        )

    question = answer.question

    answer.percentual_professor = percentual_professor

    answer.percentual_final = percentual_professor

    answer.pontuacao_obtida = calcular_pontuacao(
        question.peso or 1,
        percentual_professor
    )

    answer.revisada_professor = True

    db.commit()

    db.refresh(answer)

    return answer

def review_answer(
    db: Session,
    answer_id: int,
    percentual_professor: float
):
    if percentual_professor not in [0, 25, 50, 75, 100]:
        raise HTTPException(
            status_code=400,
            detail="Percentual deve ser 0, 25, 50, 75 ou 100."
        )

    answer = (
        db.query(StudentAnswer)
        .filter(StudentAnswer.id == answer_id)
        .first()
    )

    if not answer:
        raise HTTPException(
            status_code=404,
            detail="Resposta não encontrada."
        )

    question = answer.question

    answer.percentual_professor = percentual_professor
    answer.percentual_final = percentual_professor

    answer.pontuacao_obtida = calcular_pontuacao(
        question.peso or 1,
        percentual_professor
    )

    answer.revisada_professor = True

    db.commit()
    db.refresh(answer)

    return answer