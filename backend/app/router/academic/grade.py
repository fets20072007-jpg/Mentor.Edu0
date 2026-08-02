from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schema.grade import GradeCreate, GradeResponse

from app.services.academic.grade_service import (
    create_grade,
    get_all_grades,
    get_grade_by_id
)

router = APIRouter(
    prefix="/grades",
    tags=["Grades"]
)

@router.post(
    "",
    response_model=GradeResponse
)

def register_grade(

    grade: GradeCreate,

    db: Session = Depends(get_db)

):

    return create_grade(
        db,
        grade
    )

@router.get("/", response_model=list[GradeResponse])
def list_grades(
    db: Session = Depends(get_db)
):
    return get_all_grades(db)


@router.get("/{grade_id}", response_model=GradeResponse)
def grade_by_id(
    grade_id: int,
    db: Session = Depends(get_db)
):
    return get_grade_by_id(db, grade_id)