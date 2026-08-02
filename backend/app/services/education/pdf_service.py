from sqlalchemy.orm import Session

from app.database.models import PDFMaterial


def create_pdf(

    db: Session,

    chapter_id: int,

    data

):

    pdf = PDFMaterial(

        titulo=data.titulo,

        descricao=data.descricao,

        arquivo=data.arquivo,

        paginas=data.paginas,

        chapter_id=chapter_id

    )

    db.add(pdf)

    db.commit()

    db.refresh(pdf)

    return pdf