from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import User, Assessment, Question
from app.security.auth import get_current_user

from app.schema.assessment import (
    AssessmentCreate,
    AssessmentResponse
)

from app.services.academic.assessment_service import (
    create_assessment,
    get_all_assessments,
    get_assessment_by_id
)

from fastapi import HTTPException

from app.schema.question import (
    QuestionCreate,
    QuestionResponse
)

router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"]
)


@router.post(
    "",
    response_model=AssessmentResponse
)
def register_assessment(

    assessment: AssessmentCreate,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    return create_assessment(
        db,
        current_user.id,
        assessment
    )
@router.get("/", response_model=list[AssessmentResponse])
def list_assessments(
    db: Session = Depends(get_db)
):
    return get_all_assessments(db)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def assessment_by_id(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    return get_assessment_by_id(db, assessment_id)

@router.post(
    "/{assessment_id}/questions",
    response_model=QuestionResponse
)
def create_assessment_question(
    assessment_id: int,
    question: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )

    new_question = Question(
        tipo=question.tipo,
        enunciado=question.enunciado,

        alternativa_a=question.alternativa_a,
        alternativa_b=question.alternativa_b,
        alternativa_c=question.alternativa_c,
        alternativa_d=question.alternativa_d,

        resposta_correta=question.resposta_correta,
        explicacao=question.explicacao,

        dificuldade=question.dificuldade,
        peso=question.peso,
        categoria=question.categoria,

        criterio_0=question.criterio_0,
        criterio_25=question.criterio_25,
        criterio_50=question.criterio_50,
        criterio_75=question.criterio_75,
        criterio_100=question.criterio_100,

        chapter_id=question.chapter_id,
        assessment_id=assessment.id
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


@router.get(
    "/{assessment_id}/questions",
    response_model=list[QuestionResponse]
)
def list_assessment_questions(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )

    return (
        db.query(Question)
        .filter(
            Question.assessment_id == assessment_id
        )
        .all()
    )