from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import User

from app.schema.attendance import (
    AttendanceCreate,
    AttendanceResponse
)

from app.security.auth import get_current_user

from app.services.academic.attendance_service import (
    register_attendance,
    get_all_attendance,
    get_attendance_by_id
)

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


@router.post(
    "/",
    response_model=AttendanceResponse
)
def create_attendance(
    attendance: AttendanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return register_attendance(
        db,
        current_user.id,
        attendance
    )
    
@router.get("/", response_model=list[AttendanceResponse])
def list_attendance(
    db: Session = Depends(get_db)
):
    return get_all_attendance(db)


@router.get("/{attendance_id}", response_model=AttendanceResponse)
def attendance_by_id(
    attendance_id: int,
    db: Session = Depends(get_db)
):
    return get_attendance_by_id(db, attendance_id)