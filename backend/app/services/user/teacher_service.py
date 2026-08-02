from sqlalchemy.orm import Session

from app.database.models import Teacher

from app.schema.teacher import TeacherCreate

from app.database.models import (Subject,Enrollment)


def create_teacher(
    db: Session,
    teacher: TeacherCreate
):

    novo = Teacher(

        nome=teacher.nome,

        email=teacher.email,

        cpf=teacher.cpf,

        matricula=teacher.matricula,

        telefone=teacher.telefone,

        especialidade=teacher.especialidade,

        carga_horaria=teacher.carga_horaria

    )

    db.add(novo)

    db.commit()

    db.refresh(novo)

    return novo


def get_teachers(db: Session):

    return db.query(Teacher).all()

def get_teacher_classrooms(
    db: Session,
    teacher_id: int
):

    resultado = []

    disciplinas = (

        db.query(Subject)

        .filter(
            Subject.teacher_id == teacher_id
        )

        .all()

    )

    for disciplina in disciplinas:

        turma = disciplina.classroom

        alunos = []

        for matricula in turma.enrollments:

            alunos.append({

                "id": matricula.user.id,

                "nome": matricula.user.nome

            })

        resultado.append({

            "turma": turma.nome,

            "disciplina": disciplina.nome,

            "serie": turma.serie,

            "turno": turma.turno,

            "ano": turma.ano,

            "alunos": alunos

        })

    return resultado