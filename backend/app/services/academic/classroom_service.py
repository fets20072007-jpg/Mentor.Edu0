from sqlalchemy.orm import Session

from app.database.models import Classroom

from app.schema.classroom import (
    ClassroomCreate
)


def create_classroom(
    db: Session,
    classroom: ClassroomCreate
):

    nova = Classroom(

        nome=classroom.nome.strip(),

        serie=classroom.serie.strip(),

        turno=classroom.turno.strip(),

        sala=classroom.sala.strip(),

        ano=classroom.ano,

        capacidade=classroom.capacidade,

        # DT só é escolhido posteriormente.
        teacher_id=None
    )

    db.add(nova)

    db.commit()

    db.refresh(nova)

    return nova


def get_classrooms(
    db: Session
):

    return (
        db.query(Classroom)
        .order_by(
            Classroom.ano.desc(),
            Classroom.nome.asc()
        )
        .all()
    )