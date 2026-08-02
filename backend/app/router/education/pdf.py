from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import PDFMaterial

from app.schema.pdf import (
    PDFCreate,
    PDFResponse
)

from app.services.education.pdf_service import create_pdf

router = APIRouter(

    prefix="/library",

    tags=["Library PDFs"]

)


@router.post(

    "/chapters/{chapter_id}/pdfs",

    response_model=PDFResponse

)

def register_pdf(

    chapter_id: int,

    pdf: PDFCreate,

    db: Session = Depends(get_db)

):

    return create_pdf(

        db,

        chapter_id,

        pdf

    )


@router.get(

    "/chapters/{chapter_id}/pdfs",

    response_model=list[PDFResponse]

)

def list_pdfs(

    chapter_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(PDFMaterial)

        .filter(

            PDFMaterial.chapter_id == chapter_id

        )

        .all()

    )


@router.get(

    "/pdfs/{pdf_id}",

    response_model=PDFResponse

)

def get_pdf(

    pdf_id: int,

    db: Session = Depends(get_db)

):

    return (

        db.query(PDFMaterial)

        .filter(

            PDFMaterial.id == pdf_id

        )

        .first()

    )