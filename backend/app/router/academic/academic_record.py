from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schema.academic_record import AcademicRecordResponse

from app.services.academic.academic_record_service import generate_academic_record


router = APIRouter(
    prefix="/academic-record",
    tags=["Academic Record"]
)


@router.get(
    "/{student_id}",
    response_model=AcademicRecordResponse
)
def get_academic_record(
    student_id: int,
    db: Session = Depends(get_db)
):

    boletim = generate_academic_record(
        db,
        student_id
    )

    if boletim is None:

        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado."
        )

    return boletim