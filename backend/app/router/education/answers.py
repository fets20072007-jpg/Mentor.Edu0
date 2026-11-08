from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    User,
    StudentAnswer,
    Question
)

from app.schema.answer import (
    StudentAnswerCreate,
    StudentAnswerUpdate,
    StudentAnswerSafeResponse,
    StudentAnswerResponse
)

from app.services.education.answer_service import (
    register_answer,
    get_pending_answers,
    review_answer
)

from app.services.academic.assessment_access_service import (
    ensure_student_can_answer
)

from app.core.permissions import (
    require_student,
    require_teacher
)


router = APIRouter(
    prefix="/answers",
    tags=["Answers"]
)


# =========================================================
# ALUNO
# RESPONDER QUESTAO
# =========================================================

@router.post(
    "/questions/{question_id}",
    response_model=StudentAnswerSafeResponse
)
def answer_question(

    question_id: int,

    answer: StudentAnswerCreate,

    current_user: User = Depends(
        require_student
    ),

    db: Session = Depends(
        get_db
    )

):

    question = (
        db.query(Question)
        .filter(
            Question.id
            == question_id
        )
        .first()
    )


    if question is not None:

        if question.assessment_id is not None:

            ensure_student_can_answer(

                db=db,

                assessment_id=(
                    question.assessment_id
                ),

                student_id=(
                    current_user.id
                )
            )


    return register_answer(
        db,
        question_id,
        current_user,
        answer
    )


# =========================================================
# ALUNO
# MINHAS RESPOSTAS
# =========================================================

@router.get(
    "/me",
    response_model=list[
        StudentAnswerSafeResponse
    ]
)
def my_answers(

    current_user: User = Depends(
        require_student
    ),

    db: Session = Depends(
        get_db
    )

):

    return (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.user_id
            == current_user.id
        )
        .order_by(
            StudentAnswer.id.desc()
        )
        .all()
    )


# =========================================================
# PROFESSOR
# CORRECOES PENDENTES
# =========================================================

@router.get(
    "/teacher/pending",
    response_model=list[
        StudentAnswerResponse
    ]
)
def pending_answers(

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_pending_answers(

        db=db,

        teacher_user_id=current_user.id
    )


# =========================================================
# PROFESSOR
# CORRIGIR RESPOSTA
# =========================================================

@router.patch(
    "/{answer_id}/review",
    response_model=StudentAnswerResponse
)
def review_student_answer(

    answer_id: int,

    data: StudentAnswerUpdate,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(
        get_db
    )

):

    return review_answer(

        db=db,

        answer_id=answer_id,

        teacher_user_id=current_user.id,

        percentual_professor=(
            data.percentual_professor
        )
    )