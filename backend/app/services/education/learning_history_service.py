from app.database.models import LearningHistory


def create_history(

    db,

    user,

    materia,

    percentual,

    tempo

):

    if percentual >= 90:

        obs = (
            "Excelente evolução! Continue nesse ritmo."
        )

    elif percentual >= 75:

        obs = (
            "Bom desempenho."
        )

    elif percentual >= 60:

        obs = (
            "Desempenho regular. Faça uma revisão."
        )

    elif percentual >= 40:

        obs = (
            "Priorize esta disciplina."
        )

    else:

        obs = (
            "Necessita reforço urgente."
        )

    history = LearningHistory(

        materia=materia,

        percentual=percentual,

        tempo_medio=tempo,

        observacao=obs,

        user_id=user.id

    )

    db.add(history)

    db.commit()

    db.refresh(history)

    return history