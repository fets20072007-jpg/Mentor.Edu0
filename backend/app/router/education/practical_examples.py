from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import PracticalExample

from app.schema.practical_example import (
    PracticalExampleCreate,
    PracticalExampleResponse
)

from app.services.education.practical_example_service import (
    create_example
)

router = APIRouter(

    prefix="/library",

    tags=["Library Practical Examples"]

)


@router.post(

    "/chapters/{chapter_id}/examples",

    response_model=PracticalExampleResponse

)

def register_example(

    chapter_id: int,

    example: PracticalExampleCreate,

    db: Session = Depends(get_db)

):

    return create_example(

        db,

        chapter_id,

        example

    )


@router.get(

    "/chapters/{chapter_id}/examples",

    response_model=list[PracticalExampleResponse]

)

def list_examples(

    chapter_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(

            PracticalExample

        )

        .filter(

            PracticalExample.chapter_id == chapter_id

        )

        .all()

    )


@router.get(

    "/examples/{example_id}",

    response_model=PracticalExampleResponse

)

def get_example(

    example_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(

            PracticalExample

        )

        .filter(

            PracticalExample.id == example_id

        )

        .first()

    )