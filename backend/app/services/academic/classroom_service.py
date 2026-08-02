from sqlalchemy.orm import Session

from app.database.models import Classroom

from app.schema.classroom import ClassroomCreate


def create_classroom(
    db: Session,
    classroom: ClassroomCreate
):

    nova = Classroom(

        nome=classroom.nome,

        serie=classroom.serie,

        turno=classroom.turno,

        sala=classroom.sala,

        ano=classroom.ano,

        capacidade=classroom.capacidade,

        teacher_id=classroom.teacher_id

    )

    db.add(nova)

    db.commit()

    db.refresh(nova)

    return nova


def get_classrooms(db: Session):

    return db.query(Classroom).all()