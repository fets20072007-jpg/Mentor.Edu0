from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.models import (
    Teacher,
    Classroom,
    Subject,
    Enrollment,
    User
)


# =========================================================
# LISTAR PROFESSORES
# =========================================================

def get_teachers(
    db: Session
):

    return (
        db.query(Teacher)
        .order_by(
            Teacher.nome.asc()
        )
        .all()
    )


# =========================================================
# PROFESSOR POR ID
# =========================================================

def get_teacher_by_id(
    db: Session,
    teacher_id: int
):

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.id == teacher_id
        )
        .first()
    )

    if not teacher:

        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado."
        )

    return teacher


# =========================================================
# TURMAS EM QUE O PROFESSOR LECIONA
#
# Subject.teacher_id:
# define atuação pedagógica.
#
# Classroom.teacher_id:
# define somente a função DT.
# =========================================================

def get_teacher_classrooms(
    db: Session,
    teacher_id: int
):

    teacher = get_teacher_by_id(
        db,
        teacher_id
    )

    subjects = (
        db.query(Subject)
        .filter(
            Subject.teacher_id == teacher.id,
            Subject.ativa == True
        )
        .all()
    )

    classroom_ids = {
        subject.classroom_id
        for subject in subjects
    }

    results = []

    for classroom_id in classroom_ids:

        classroom = (
            db.query(Classroom)
            .filter(
                Classroom.id == classroom_id
            )
            .first()
        )

        if not classroom:
            continue

        teacher_subjects = [
            subject.nome
            for subject in subjects
            if (
                subject.classroom_id
                == classroom.id
            )
        ]

        enrollments = (
            db.query(Enrollment)
            .filter(
                Enrollment.classroom_id
                == classroom.id,

                Enrollment.ativo
                == True
            )
            .all()
        )

        alunos = []

        for enrollment in enrollments:

            student = (
                db.query(User)
                .filter(
                    User.id
                    == enrollment.user_id
                )
                .first()
            )

            if not student:
                continue

            tipo = (
                student.tipo
                or ""
            ).strip().lower()

            if tipo != "aluno":
                continue

            alunos.append({
                "id": student.id,
                "nome": student.nome
            })

        results.append({

            "classroom_id":
                classroom.id,

            "turma":
                classroom.nome,

            "serie":
                classroom.serie,

            "turno":
                classroom.turno,

            "ano":
                classroom.ano,

            "is_dt":
                classroom.teacher_id
                == teacher.id,

            "disciplinas":
                teacher_subjects,

            "alunos":
                alunos
        })

    results.sort(
        key=lambda item: (
            item["ano"],
            item["turma"]
        )
    )

    return results


# =========================================================
# PROFESSORES QUE ATUAM EM UMA TURMA
# =========================================================

def get_classroom_teachers(
    db: Session,
    classroom_id: int
):

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id == classroom_id
        )
        .first()
    )

    if not classroom:

        raise HTTPException(
            status_code=404,
            detail="Turma não encontrada."
        )

    subjects = (
        db.query(Subject)
        .filter(
            Subject.classroom_id
            == classroom.id,

            Subject.ativa
            == True
        )
        .all()
    )

    teacher_ids = {
        subject.teacher_id
        for subject in subjects
    }

    results = []

    for teacher_id in teacher_ids:

        teacher = (
            db.query(Teacher)
            .filter(
                Teacher.id == teacher_id
            )
            .first()
        )

        if not teacher:
            continue

        teacher_subjects = [
            subject.nome
            for subject in subjects
            if (
                subject.teacher_id
                == teacher.id
            )
        ]

        results.append({

            "teacher_id":
                teacher.id,

            "nome":
                teacher.nome,

            "especialidade":
                teacher.especialidade,

            "is_dt":
                classroom.teacher_id
                == teacher.id,

            "disciplinas":
                teacher_subjects
        })

    results.sort(
        key=lambda item:
            item["nome"].lower()
    )

    return results