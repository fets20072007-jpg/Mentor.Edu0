from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schema.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse
)

from app.services.academic.enrollment_service import (
    create_enrollment,
    get_enrollments
)

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)


@router.post(
    "",
    response_model=EnrollmentResponse
)
def register_enrollment(

    enrollment: EnrollmentCreate,

    db: Session = Depends(get_db)

):

    return create_enrollment(
        db,
        enrollment
    )


@router.get(
    "",
    response_model=list[EnrollmentResponse]
)
def list_enrollments(

    db: Session = Depends(get_db)

):

    return get_enrollments(db)