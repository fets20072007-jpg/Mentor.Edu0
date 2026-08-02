from sqlalchemy.orm import Session

from app.database.models import Video


def create_video(

    db: Session,

    chapter_id: int,

    data

):

    video = Video(

        titulo=data.titulo,

        descricao=data.descricao,

        url=data.url,

        duracao=data.duracao,

        plataforma=data.plataforma,

        chapter_id=chapter_id

    )

    db.add(video)

    db.commit()

    db.refresh(video)

    return video