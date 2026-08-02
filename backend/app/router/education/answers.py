from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.security.auth import get_current_user

from app.database.models import (
    User,
    StudentAnswer
)

from app.schema.answer import (
    StudentAnswerCreate,
    StudentAnswerResponse
)

from app.services.education.answer_service import (
    register_answer
)

router = APIRouter(

    prefix="/answers",

    tags=["Answers"]

)


@router.post(

    "/questions/{question_id}",

    response_model=StudentAnswerResponse

)

def answer_question(

    question_id: int,

    answer: StudentAnswerCreate,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return register_answer(

        db,

        question_id,

        current_user,

        answer

    )


@router.get(

    "/me",

    response_model=list[StudentAnswerResponse]

)

def my_answers(

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return (

        db.query(StudentAnswer)

        .filter(

            StudentAnswer.user_id == current_user.id

        )

        .all()

    )