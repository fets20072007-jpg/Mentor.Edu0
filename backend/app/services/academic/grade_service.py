from sqlalchemy.orm import Session

from app.database.models import Grade

from app.schema.grade import GradeCreate


def create_grade(
    db: Session,
    grade: GradeCreate
):

    nova = Grade(

        assessment_id=grade.assessment_id,

        student_id=grade.student_id,

        nota=grade.nota,

        observacao=grade.observacao

    )

    db.add(nova)

    db.commit()

    db.refresh(nova)

    return nova

def get_all_grades(db: Session):
    return db.query(Grade).all()


def get_grade_by_id(
    db: Session,
    grade_id: int
):
    return (
        db.query(Grade)
        .filter(Grade.id == grade_id)
        .first()
    )