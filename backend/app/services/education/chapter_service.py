from sqlalchemy.orm import Session

from app.database.models import Chapter


def create_chapter(

    db: Session,

    book_id: int,

    data

):

    novo = Chapter(

        titulo=data.titulo,

        numero=data.numero,

        pagina_inicio=data.pagina_inicio,

        pagina_fim=data.pagina_fim,

        descricao=data.descricao,

        book_id=book_id

    )

    db.add(novo)

    db.commit()

    db.refresh(novo)

    return novo