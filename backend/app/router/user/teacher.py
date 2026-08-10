from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import Teacher, User
from app.schema.teacher import (
    TeacherCreate,
    TeacherResponse,
    TeacherClassroomResponse
)
from app.services.user.teacher_service import (
    create_teacher,
    get_teachers,
    get_teacher_classrooms
)
from app.security.auth import get_current_user


router = APIRouter(
    prefix="/teachers",
    tags=["Teachers"]
)


@router.post(
    "",
    response_model=TeacherResponse
)
def register_teacher(
    teacher: TeacherCreate,
    db: Session = Depends(get_db)
):
    return create_teacher(db, teacher)


@router.get(
    "",
    response_model=list[TeacherResponse]
)
def list_teachers(
    db: Session = Depends(get_db)
):
    return get_teachers(db)


@router.get(
    "/me/classrooms",
    response_model=list[TeacherClassroomResponse]
)
def my_classrooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    teacher = (
        db.query(Teacher)
        .filter(Teacher.user_id == current_user.id)
        .first()
    )

    if teacher is None:
        return []

    return get_teacher_classrooms(
        db,
        teacher.id
    )

@router.post(
    "",
    response_model=TeacherResponse
)
def register_teacher(
    teacher: TeacherCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_teacher(
        db,
        teacher,
        current_user.id
    )