from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schema.subject import (
    SubjectCreate,
    SubjectResponse
)

from app.services.academic.subject_service import (
    create_subject,
    get_subjects
)

router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)


@router.post(
    "",
    response_model=SubjectResponse
)
def register_subject(

    subject: SubjectCreate,

    db: Session = Depends(get_db)

):

    return create_subject(
        db,
        subject
    )


@router.get(
    "",
    response_model=list[SubjectResponse]
)
def list_subjects(

    db: Session = Depends(get_db)

):

    return get_subjects(db)