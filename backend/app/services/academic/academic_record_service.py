from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import (
    User,
    Enrollment,
    Classroom,
    Subject,
    Grade,
    Attendance
)

from app.schema.academic_record import (
    AcademicRecordResponse,
    SubjectPerformance
)


def generate_academic_record(
    db: Session,
    student_id: int
):

    aluno = (
        db.query(User)
        .filter(User.id == student_id)
        .first()
    )

    if not aluno:
        return None

    matricula = (
        db.query(Enrollment)
        .filter(Enrollment.student_id == student_id)
        .first()
    )

    turma = (
        db.query(Classroom)
        .filter(Classroom.id == matricula.classroom_id)
        .first()
    )

    disciplinas = db.query(Subject).all()

    resultado = []

    for disciplina in disciplinas:

        notas = (
            db.query(Grade)
            .join(Grade.assessment)
            .filter(
                Grade.student_id == student_id,
                Grade.assessment.has(
                    subject_id=disciplina.id
                )
            )
            .all()
        )

        if len(notas) == 0:
            continue

        media = sum(n.nota for n in notas) / len(notas)

        total_presencas = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student_id,
                Attendance.subject_id == disciplina.id,
                Attendance.status == "Presente"
            )
            .count()
        )

        total_aulas = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student_id,
                Attendance.subject_id == disciplina.id
            )
            .count()
        )

        frequencia = 0

        if total_aulas > 0:
            frequencia = round(
                (total_presencas / total_aulas) * 100,
                2
            )

        if media >= 7:
            situacao = "Aprovado"

        elif media >= 5:
            situacao = "Recuperação"

        else:
            situacao = "Reprovado"

        resultado.append(

            SubjectPerformance(

                disciplina=disciplina.nome,

                media=round(media, 2),

                frequencia=frequencia,

                situacao=situacao

            )

        )

    return AcademicRecordResponse(

        aluno=aluno.nome,

        turma=turma.nome,

        disciplinas=resultado

    )