from sqlalchemy.orm import Session

from app.database.models import (
    LibraryQuestion
)


def create_library_question(
    db: Session,
    teacher_id: int,
    data
):

    question = LibraryQuestion(
        teacher_id=teacher_id,
        subject_id=data.subject_id,

        tipo=data.tipo,
        enunciado=data.enunciado,

        alternativa_a=data.alternativa_a,
        alternativa_b=data.alternativa_b,
        alternativa_c=data.alternativa_c,
        alternativa_d=data.alternativa_d,

        resposta_correta=data.resposta_correta,

        explicacao=data.explicacao,

        dificuldade=data.dificuldade,

        categoria=data.categoria,

        criterio_0=data.criterio_0,
        criterio_25=data.criterio_25,
        criterio_50=data.criterio_50,
        criterio_75=data.criterio_75,
        criterio_100=data.criterio_100,

        compartilhada=data.compartilhada,

        ativa=True
    )

    db.add(question)

    db.commit()

    db.refresh(question)

    return question