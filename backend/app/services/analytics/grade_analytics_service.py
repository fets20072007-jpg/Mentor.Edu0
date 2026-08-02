from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import Grade, Assessment


def calculate_student_average(
    db: Session,
    student_id: int,
    subject_id: int
):
    """
    Calcula a média do aluno em uma disciplina.
    """

    media = (
        db.query(func.avg(Grade.nota))
        .join(Assessment)
        .filter(
            Grade.student_id == student_id,
            Assessment.subject_id == subject_id
        )
        .scalar()
    )

    if media is None:
        return 0.0

    return round(float(media), 2)