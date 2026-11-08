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

from app.schema.attendance import (
    AttendanceResponse
)

from app.schema.attendance_edit import (
    AttendanceEdit
)

from app.core.permissions import (
    require_teacher
)

from app.services.academic.attendance_edit_service import (
    edit_attendance
)


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


# =========================================================
# PROFESSOR
# EDITAR REGISTRO EM ATE 24 HORAS
# =========================================================

@router.patch(
    "/{attendance_id}",
    response_model=AttendanceResponse
)
def update_attendance(

    attendance_id: int,

    data: AttendanceEdit,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(
        get_db
    )

):

    return edit_attendance(

        db=db,

        attendance_id=attendance_id,

        teacher_user_id=current_user.id,

        data=data
    )