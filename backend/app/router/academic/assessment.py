from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import User

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

