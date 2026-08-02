from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import Chapter

from app.schema.chapters import (
    ChapterCreate,
    ChapterResponse
)

from app.services.education.chapter_service import (
    create_chapter
)

router = APIRouter(

    prefix="/library",

    tags=["Library Chapters"]

)


@router.post(

    "/books/{book_id}/chapters",

    response_model=ChapterResponse

)

def register_chapter(

    book_id: int,

    chapter: ChapterCreate,

    db: Session = Depends(get_db)

):

    return create_chapter(

        db,

        book_id,

        chapter

    )


@router.get(

    "/books/{book_id}/chapters",

    response_model=list[ChapterResponse]

)

def list_book_chapters(

    book_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(Chapter)

        .filter(

            Chapter.book_id == book_id

        )

        .order_by(

            Chapter.numero

        )

        .all()

    )


@router.get(

    "/chapters/{chapter_id}",

    response_model=ChapterResponse

)

def get_chapter(

    chapter_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(Chapter)

        .filter(

            Chapter.id == chapter_id

        )

        .first()

    )