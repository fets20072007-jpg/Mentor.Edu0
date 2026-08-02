from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.analytics.grade_analytics_service import (
    calculate_student_average
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/average")
def student_average(
    student_id: int,
    subject_id: int,
    db: Session = Depends(get_db)
):
    media = calculate_student_average(
        db,
        student_id,
        subject_id
    )

    return {
        "student_id": student_id,
        "subject_id": subject_id,
        "average": media
    }