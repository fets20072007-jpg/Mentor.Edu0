from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    LearningHistory,
    StudentAnswer,
    User,
    Question,
    Chapter,
    Book
)

from app.security.auth import get_current_user

from app.schema.learning_history import (
    LearningHistoryResponse
)

from app.services.education.learning_history_service import (
    create_history
)

router = APIRouter(
    prefix="/learning-history",
    tags=["Learning History"]
)


@router.post("/generate")
def generate_history(

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    respostas = (

        db.query(StudentAnswer)

        .filter(
            StudentAnswer.user_id == current_user.id
        )

        .all()

    )

    materias = defaultdict(list)

    for resposta in respostas:

        question = (
            db.query(Question)
            .filter(Question.id == resposta.question_id)
            .first()
        )

        if not question:
            continue

        chapter = (
            db.query(Chapter)
            .filter(Chapter.id == question.chapter_id)
            .first()
        )

        if not chapter:
            continue

        book = (
            db.query(Book)
            .filter(Book.id == chapter.book_id)
            .first()
        )

        if not book:
            continue

        materias[book.disciplina].append(resposta)

    historicos = []

    for materia, lista in materias.items():

        total = len(lista)

        acertos = sum(
            1
            for r in lista
            if r.correta
        )

        percentual = int(
            acertos * 100 / total
        )

        tempos = [

            r.tempo_resposta

            for r in lista

            if r.tempo_resposta is not None

        ]

        if tempos:

            tempo = int(sum(tempos) / len(tempos))

        else:

            tempo = 0

        historicos.append(

            create_history(

                db,

                current_user,

                materia,

                percentual,

                tempo

            )

        )

    return historicos


@router.get(
    "/me",
    response_model=list[LearningHistoryResponse]
)
def history(

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return (

        db.query(LearningHistory)

        .filter(
            LearningHistory.user_id == current_user.id
        )

        .all()

    )