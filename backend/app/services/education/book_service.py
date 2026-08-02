from sqlalchemy.orm import Session

from app.database.models import Book
from app.schema.book import BookCreate


def create_book(
    db: Session,
    book_data: BookCreate,
):
    new_book = Book(
        **book_data.model_dump()
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


def list_books(
    db: Session,
):
    return db.query(Book).all()


def search_books_by_subject(
    db: Session,
    disciplina: str,
):
    return (
        db.query(Book)
        .filter(Book.disciplina == disciplina)
        .all()
    )