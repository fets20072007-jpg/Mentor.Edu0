from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import Book
from app.schema.book import BookCreate, BookResponse

router = APIRouter(
    prefix="/library",
    tags=["Digital Library"]
)


@router.get("/")
def library_home():
    return {
        "module": "Biblioteca Digital",
        "version": "1.0",
        "resources": [
            "Livros",
            "Capítulos",
            "PDFs",
            "Questões",
            "Vídeos",
            "Resumos",
            "Exemplos Práticos"
        ]
    }


@router.post(
    "/books",
    response_model=BookResponse
)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db)
):
    novo = Book(
        titulo=book.titulo,
        disciplina=book.disciplina,
        autor=book.autor,
        editora=book.editora,
        ano=book.ano,
        quantidade_capitulos=book.quantidade_capitulos,
        pdf_url=book.pdf_url,
        descricao=book.descricao
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo


@router.get(
    "/books",
    response_model=list[BookResponse]
)
def list_books(
    db: Session = Depends(get_db)
):
    return db.query(Book).all()


@router.get(
    "/books/disciplina/{disciplina}",
    response_model=list[BookResponse]
)
def books_by_subject(
    disciplina: str,
    db: Session = Depends(get_db)
):
    return (
        db.query(Book)
        .filter(Book.disciplina == disciplina)
        .all()
    )


@router.get(
    "/books/{book_id}",
    response_model=BookResponse
)
def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )