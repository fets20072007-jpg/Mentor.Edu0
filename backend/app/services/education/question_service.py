from sqlalchemy.orm import Session

from app.database.models import Question


def create_question(

    db: Session,

    chapter_id: int,

    data

):

    question = Question(

        enunciado=data.enunciado,

        alternativa_a=data.alternativa_a,
        alternativa_b=data.alternativa_b,
        alternativa_c=data.alternativa_c,
        alternativa_d=data.alternativa_d,

        resposta_correta=data.resposta_correta,

        explicacao=data.explicacao,

        dificuldade=data.dificuldade,

        chapter_id=chapter_id

    )

    db.add(question)

    db.commit()

    db.refresh(question)

    return question