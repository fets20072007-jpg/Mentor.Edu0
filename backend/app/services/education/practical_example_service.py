from sqlalchemy.orm import Session

from app.database.models import PracticalExample


def create_example(

    db: Session,

    chapter_id: int,

    data

):

    example = PracticalExample(

        titulo=data.titulo,

        contexto=data.contexto,

        explicacao=data.explicacao,

        curso_relacionado=data.curso_relacionado,

        chapter_id=chapter_id

    )

    db.add(example)

    db.commit()

    db.refresh(example)

    return example