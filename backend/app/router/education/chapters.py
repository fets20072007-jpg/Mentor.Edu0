from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    Book,
    Chapter,
    User
)

from app.schema.chapters import (
    ChapterCreate,
    ChapterResponse
)

from app.services.education.chapter_service import (
    create_chapter
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_support
)


router = APIRouter(
    prefix="/library",
    tags=["Library Chapters"]
)


# =========================================================
# SUPORTE
# CADASTRAR CAPÍTULO EM LIVRO INSTITUCIONAL
# =========================================================

@router.post(
    "/books/{book_id}/chapters",
    response_model=ChapterResponse
)
def register_chapter(
    book_id: int,
    chapter: ChapterCreate,

    current_user: User = Depends(
        require_support
    ),

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

    return create_chapter(
        db,
        book_id,
        chapter
    )


# =========================================================
# LISTAR CAPÍTULOS DE UM LIVRO
# USUÁRIO AUTENTICADO
# =========================================================

@router.get(
    "/books/{book_id}/chapters",
    response_model=list[ChapterResponse]
)
def list_book_chapters(
    book_id: int,

    current_user: User = Depends(
        get_current_user
    ),

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


# =========================================================
# CONSULTAR CAPÍTULO
# USUÁRIO AUTENTICADO
# =========================================================

@router.get(
    "/chapters/{chapter_id}",
    response_model=ChapterResponse
)
def get_chapter(
    chapter_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    chapter = (
        db.query(Chapter)
        .filter(
            Chapter.id == chapter_id
        )
        .first()
    )

    if not chapter:
        raise HTTPException(
            status_code=404,
            detail="Capítulo não encontrado."
        )

    return chapter