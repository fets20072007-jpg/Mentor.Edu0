from sqlalchemy.orm import Session

from app.database.models import Subject

from app.schema.subject import SubjectCreate


def create_subject(
    db: Session,
    subject: SubjectCreate
):

    nova = Subject(

        nome=subject.nome,

        carga_horaria=subject.carga_horaria,

        descricao=subject.descricao,

        teacher_id=subject.teacher_id,

        classroom_id=subject.classroom_id

    )

    db.add(nova)

    db.commit()

    db.refresh(nova)

    return nova


def get_subjects(db: Session):

    return db.query(Subject).all()