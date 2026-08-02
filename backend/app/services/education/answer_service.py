from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import (
    Question,
    StudentAnswer,
    User
)


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

    correta = (
        data.resposta.upper().strip()
        ==
        question.resposta_correta.upper().strip()
    )

    answer = StudentAnswer(

        resposta=data.resposta,

        correta=correta,

        tempo_resposta=data.tempo_resposta,

        question_id=question.id,

        user_id=user.id

    )

    db.add(answer)

    db.commit()

    db.refresh(answer)

    return answer