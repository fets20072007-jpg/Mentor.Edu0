from sqlalchemy.orm import Session

from app.database.models import Assessment


def create_assessment(

    db: Session,

    teacher_id: int,

    assessment

):

    nova = Assessment(

        titulo=assessment.titulo,

        descricao=assessment.descricao,

        tipo=assessment.tipo,

        data=assessment.data,

        valor=assessment.valor,

        teacher_id=teacher_id,

        classroom_id=assessment.classroom_id,

        subject_id=assessment.subject_id

    )

    db.add(nova)

    db.commit()

    db.refresh(nova)

    return nova

def get_all_assessments(db: Session):
    return db.query(Assessment).all()


def get_assessment_by_id(
    db: Session,
    assessment_id: int
):
    return (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )