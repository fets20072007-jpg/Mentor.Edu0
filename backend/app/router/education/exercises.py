from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import Exercise

from app.schema.exercises import (
    ExerciseCreate,
    ExerciseResponse
)

from app.services.education.exercise_service import (
    create_exercise
)

router = APIRouter(

    prefix="/library",

    tags=["Library Exercises"]

)


@router.post(

    "/chapters/{chapter_id}/exercises",

    response_model=ExerciseResponse

)

def register_exercise(

    chapter_id: int,

    exercise: ExerciseCreate,

    db: Session = Depends(get_db)

):

    return create_exercise(

        db,

        chapter_id,

        exercise

    )


@router.get(

    "/chapters/{chapter_id}/exercises",

    response_model=list[ExerciseResponse]

)

def list_exercises(

    chapter_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(Exercise)

        .filter(

            Exercise.chapter_id == chapter_id

        )

        .all()

    )


@router.get(

    "/exercises/{exercise_id}",

    response_model=ExerciseResponse

)

def get_exercise(

    exercise_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(Exercise)

        .filter(

            Exercise.id == exercise_id

        )

        .first()

    )