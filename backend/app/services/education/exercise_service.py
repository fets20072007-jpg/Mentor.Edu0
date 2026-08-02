from sqlalchemy.orm import Session

from app.database.models import Exercise


def create_exercise(
    db: Session,
    chapter_id: int,
    data
):

    novo = Exercise(

        pergunta=data.pergunta,

        alternativa_a=data.alternativa_a,

        alternativa_b=data.alternativa_b,

        alternativa_c=data.alternativa_c,

        alternativa_d=data.alternativa_d,

        resposta_correta=data.resposta_correta,

        explicacao=data.explicacao,

        dificuldade=data.dificuldade,

        chapter_id=chapter_id

    )

    db.add(novo)

    db.commit()

    db.refresh(novo)

    return novo