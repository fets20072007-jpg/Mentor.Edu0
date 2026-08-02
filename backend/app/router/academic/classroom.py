from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schema.classroom import (
    ClassroomCreate,
    ClassroomResponse
)

from app.services.academic.classroom_service import (
    create_classroom,
    get_classrooms
)

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"]
)


@router.post(
    "",
    response_model=ClassroomResponse
)
def register_classroom(

    classroom: ClassroomCreate,

    db: Session = Depends(get_db)

):

    return create_classroom(
        db,
        classroom
    )


@router.get(
    "",
    response_model=list[ClassroomResponse]
)
def list_classrooms(

    db: Session = Depends(get_db)

):

    return get_classrooms(db)