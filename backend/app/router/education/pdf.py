from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    PDFMaterial,
    Chapter,
    User
)

from app.schema.pdf import (
    PDFCreate,
    PDFResponse
)

from app.services.education.pdf_service import (
    create_pdf
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_teacher,
    require_library_reader
)


router = APIRouter(
    prefix="/library",
    tags=["Library PDFs"]
)


# =========================================================
# PROFESSOR
# CADASTRAR PDF PEDAGÓGICO
# =========================================================

@router.post(
    "/chapters/{chapter_id}/pdfs",
    response_model=PDFResponse
)
def register_pdf(
    chapter_id: int,
    pdf: PDFCreate,

    current_user: User = Depends(
        require_teacher
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

    return create_pdf(
        db,
        chapter_id,
        pdf
    )


# =========================================================
# LISTAR PDFs DO CAPÍTULO
# USUÁRIOS AUTENTICADOS
# =========================================================

@router.get(
    "/chapters/{chapter_id}/pdfs",
    response_model=list[PDFResponse]
)
def list_pdfs(
    chapter_id: int,

   current_user: User = Depends(
    require_library_reader
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

    return (
        db.query(PDFMaterial)
        .filter(
            PDFMaterial.chapter_id == chapter_id
        )
        .all()
    )


# =========================================================
# CONSULTAR PDF
# USUÁRIOS AUTENTICADOS
# =========================================================

@router.get(
    "/pdfs/{pdf_id}",
    response_model=PDFResponse
)
def get_pdf(
    pdf_id: int,

    current_user: User = Depends(
    require_library_reader
),

    db: Session = Depends(get_db)
):

    pdf = (
        db.query(PDFMaterial)
        .filter(
            PDFMaterial.id == pdf_id
        )
        .first()
    )

    if not pdf:
        raise HTTPException(
            status_code=404,
            detail="PDF não encontrado."
        )

    return pdf