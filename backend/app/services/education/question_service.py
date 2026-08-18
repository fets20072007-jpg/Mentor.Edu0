from sqlalchemy.orm import Session

from app.database.models import Question


def create_question(
    db: Session,
    chapter_id: int,
    data
):

    question = Question(

        tipo=data.tipo,

        enunciado=data.enunciado,

        alternativa_a=data.alternativa_a,
        alternativa_b=data.alternativa_b,
        alternativa_c=data.alternativa_c,
        alternativa_d=data.alternativa_d,

        resposta_correta=data.resposta_correta,

        explicacao=data.explicacao,

        dificuldade=data.dificuldade,

        peso=data.peso,

        categoria=data.categoria,

        criterio_0=data.criterio_0,
        criterio_25=data.criterio_25,
        criterio_50=data.criterio_50,
        criterio_75=data.criterio_75,
        criterio_100=data.criterio_100,

        chapter_id=chapter_id,

        assessment_id=data.assessment_id

    )

    db.add(question)

    db.commit()

    db.refresh(question)

    return question