from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database.dependencies import (
    get_db
)

from app.database.models import (
    User
)

from app.core.permissions import (
    require_teacher,
    require_student
)

from app.schema.assessment_access import (
    AssessmentAccessUpdate,
    AssessmentAccessResponse,
    AssessmentAvailabilityResponse,
    AssessmentSubmissionItem,
    AssessmentAnswerKeyItem
)

from app.services.academic.assessment_access_service import (
    update_assessment_access,
    get_student_availability,
    get_student_submission,
    get_student_answer_key
)


router = APIRouter(
    prefix="/assessments",
    tags=["Assessment Access"]
)


# =========================================================
# PROFESSOR
# CONFIGURAR PRAZO E LIBERACOES
# =========================================================

@router.patch(
    "/{assessment_id}/access",
    response_model=AssessmentAccessResponse
)
def configure_assessment_access(

    assessment_id: int,

    data: AssessmentAccessUpdate,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(
        get_db
    )

):

    return update_assessment_access(

        db=db,

        assessment_id=assessment_id,

        teacher_user_id=current_user.id,

        data=data
    )


# =========================================================
# ALUNO
# DISPONIBILIDADE
# =========================================================

@router.get(
    "/{assessment_id}/availability/me",
    response_model=AssessmentAvailabilityResponse
)
def assessment_availability(

    assessment_id: int,

    current_user: User = Depends(
        require_student
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_student_availability(

        db=db,

        assessment_id=assessment_id,

        student_id=current_user.id
    )


# =========================================================
# ALUNO
# PROVA RESPONDIDA
# =========================================================

@router.get(
    "/{assessment_id}/submission/me",
    response_model=list[
        AssessmentSubmissionItem
    ]
)
def assessment_submission(

    assessment_id: int,

    current_user: User = Depends(
        require_student
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_student_submission(

        db=db,

        assessment_id=assessment_id,

        student_id=current_user.id
    )


# =========================================================
# ALUNO
# GABARITO
# =========================================================

@router.get(
    "/{assessment_id}/answer-key/me",
    response_model=list[
        AssessmentAnswerKeyItem
    ]
)
def assessment_answer_key(

    assessment_id: int,

    current_user: User = Depends(
        require_student
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_student_answer_key(

        db=db,

        assessment_id=assessment_id,

        student_id=current_user.id
    )