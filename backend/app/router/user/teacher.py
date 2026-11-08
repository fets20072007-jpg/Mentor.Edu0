from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    Teacher,
    User
)

from app.schema.teacher import (
    TeacherResponse,
    TeacherClassroomResponse
)

from app.services.user.teacher_service import (
    get_teachers,
    get_teacher_classrooms
)

from app.core.permissions import (
    require_teacher,
    require_admin,
    require_admin_or_support
)


router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)


# =========================================================
# ADMINISTRAÇÃO / SUPORTE
# LISTAR PROFESSORES
# =========================================================

@router.get(
    "",
    response_model=list[TeacherResponse]
)
def list_teachers(

    current_user: User = Depends(
        require_admin_or_support
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_teachers(
        db
    )


# =========================================================
# PROFESSOR
# MINHAS TURMAS DE ATUAÇÃO
# =========================================================

@router.get(
    "/me/classrooms",
    response_model=list[
        TeacherClassroomResponse
    ]
)
def my_classrooms(

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(
        get_db
    )

):

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id
            == current_user.id
        )
        .first()
    )

    if teacher is None:
        return []

    return get_teacher_classrooms(
        db,
        teacher.id
    )


# =========================================================
# ADMINISTRAÇÃO
# TURMAS EM QUE UM PROFESSOR ATUA
#
# Esta é uma consulta pedagógica.
# Suporte não acessa.
# =========================================================

@router.get(
    "/{teacher_id}/classrooms",
    response_model=list[
        TeacherClassroomResponse
    ]
)
def teacher_classrooms_admin(

    teacher_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_teacher_classrooms(
        db,
        teacher_id
    )