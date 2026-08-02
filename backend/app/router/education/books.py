from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schema.book import BookCreate, BookResponse
from app.services.education.book_service import (
    create_book,
    list_books,
    search_books_by_subject,
)


router = APIRouter(
    prefix="/books",
    tags=["Books"],
)


@router.post(
    "/",
    response_model=BookResponse,
)
def create_book_route(
    book: BookCreate,
    db: Session = Depends(get_db),
):
    return create_book(
        db=db,
        book_data=book,
    )


@router.get(
    "/",
    response_model=list[BookResponse],
)
def list_books_route(
    db: Session = Depends(get_db),
):
    return list_books(db=db)


@router.get(
    "/disciplina/{disciplina}",
    response_model=list[BookResponse],
)
def books_by_subject_route(
    disciplina: str,
    db: Session = Depends(get_db),
):
    return search_books_by_subject(
        db=db,
        disciplina=disciplina,
    )