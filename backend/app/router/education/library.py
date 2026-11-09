from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.core.permissions import require_library_reader

from app.database.models import (
    Book,
    User
)

from app.schema.book import (
    BookCreate,
    BookResponse
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_support
)


router = APIRouter(
    prefix="/library",
    tags=["Digital Library"]
)


# =========================================================
# INFORMAÇÕES DA BIBLIOTECA
# TODOS OS USUÁRIOS AUTENTICADOS
# =========================================================

@router.get("/")
def library_home(
    current_user: User = Depends(require_library_reader)
):

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


# =========================================================
# SUPORTE
# CADASTRAR LIVRO INSTITUCIONAL
# =========================================================

@router.post(
    "/books",
    response_model=BookResponse
)
def create_book(
    book: BookCreate,

    current_user: User = Depends(
        require_support
    ),

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


# =========================================================
# LISTAR LIVROS
# TODOS OS USUÁRIOS AUTENTICADOS
# =========================================================

@router.get(
    "/books",
    response_model=list[BookResponse]
)
def list_books(
    current_user: User = Depends(require_library_reader),

    db: Session = Depends(get_db)
):

    return (
        db.query(Book)
        .order_by(Book.titulo)
        .all()
    )


# =========================================================
# LIVROS POR DISCIPLINA
# =========================================================

@router.get(
    "/books/disciplina/{disciplina}",
    response_model=list[BookResponse]
)
def books_by_subject(
    disciplina: str,

    current_user: User = Depends(require_library_reader),

    db: Session = Depends(get_db)
):

    return (
        db.query(Book)
        .filter(
            Book.disciplina == disciplina
        )
        .order_by(Book.titulo)
        .all()
    )


# =========================================================
# CONSULTAR LIVRO
# =========================================================

@router.get(
    "/books/{book_id}",
    response_model=BookResponse
)
def get_book(
    book_id: int,

    current_user: User = Depends(require_library_reader),

    db: Session = Depends(get_db)
):

    livro = (
        db.query(Book)
        .filter(
            Book.id == book_id
        )
        .first()
    )

    if not livro:
        raise HTTPException(
            status_code=404,
            detail="Livro não encontrado."
        )

    return livro