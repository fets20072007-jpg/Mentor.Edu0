from sqlalchemy.orm import Session

from app.database.models import Grade

from app.schema.grade import (
    GradeCreate,
    GradeUpdate
)


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


def get_all_grades(
    db: Session
):

    return (
        db.query(Grade)
        .order_by(
            Grade.id.desc()
        )
        .all()
    )


def get_grade_by_id(
    db: Session,
    grade_id: int
):

    return (
        db.query(Grade)
        .filter(
            Grade.id == grade_id
        )
        .first()
    )


def get_student_grades(
    db: Session,
    student_id: int
):

    return (
        db.query(Grade)
        .filter(
            Grade.student_id == student_id
        )
        .order_by(
            Grade.id.desc()
        )
        .all()
    )


def get_assessment_grades(
    db: Session,
    assessment_id: int
):

    return (
        db.query(Grade)
        .filter(
            Grade.assessment_id == assessment_id
        )
        .order_by(
            Grade.id.desc()
        )
        .all()
    )


def update_grade(
    db: Session,
    grade: Grade,
    grade_update: GradeUpdate
):

    update_data = (
        grade_update.model_dump(
            exclude_unset=True
        )
    )

    for field, value in update_data.items():

        setattr(
            grade,
            field,
            value
        )

    db.commit()
    db.refresh(grade)

    return grade