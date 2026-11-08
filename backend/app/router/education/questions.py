from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import Question

from app.schema.question import (
    QuestionCreate,
    QuestionResponse
)

from app.services.education.question_service import (
    create_question
)
from app.database.models import User
from app.core.permissions import require_teacher

router = APIRouter(

    prefix="/library",

    tags=["Library Questions"]

)


@router.post(

    "/chapters/{chapter_id}/questions",

    response_model=QuestionResponse

)

def register_question(
    chapter_id: int,
    question: QuestionCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):

    return create_question(

        db,
        chapter_id,
        question
    )

@router.get(

    "/chapters/{chapter_id}/questions",

    response_model=list[QuestionResponse]

)

def list_questions(
    chapter_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):

    return (

        db.query(Question)

        .filter(

            Question.chapter_id == chapter_id

        )

        .all()

    )


@router.get(

    "/questions/{question_id}",

    response_model=QuestionResponse

)

def get_question(
    question_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)

):

    return (

        db.query(Question)

        .filter(

            Question.id == question_id

        )

        .first()
    )

