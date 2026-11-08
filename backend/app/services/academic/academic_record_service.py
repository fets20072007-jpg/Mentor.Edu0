from sqlalchemy.orm import Session

from app.database.models import (
    User,
    Enrollment,
    Classroom,
    Subject,
    Grade,
    Attendance,
    Assessment
)

from app.schema.academic_record import (
    AcademicRecordResponse,
    SubjectPerformance
)


def generate_academic_record(
    db: Session,
    student_id: int,
    allowed_subject_ids: list[int] | None = None
):

    # =====================================================
    # ALUNO
    # =====================================================

    aluno = (
        db.query(User)
        .filter(
            User.id == student_id
        )
        .first()
    )

    if not aluno:
        return None

    tipo = (
        aluno.tipo
        or ""
    ).strip().lower()

    if tipo != "aluno":
        return None


    # =====================================================
    # MATRÍCULA
    # =====================================================

    matricula = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == student_id
        )
        .order_by(
            Enrollment.ativo.desc(),
            Enrollment.data_matricula.desc()
        )
        .first()
    )

    if not matricula:

        return AcademicRecordResponse(
            aluno=aluno.nome,
            turma="Sem turma vinculada",
            disciplinas=[]
        )


    # =====================================================
    # TURMA
    # =====================================================

    turma = (
        db.query(Classroom)
        .filter(
            Classroom.id == matricula.classroom_id
        )
        .first()
    )

    if not turma:

        return AcademicRecordResponse(
            aluno=aluno.nome,
            turma="Turma não encontrada",
            disciplinas=[]
        )


    # =====================================================
    # DISCIPLINAS DA TURMA
    # =====================================================

    disciplinas_query = (
        db.query(Subject)
        .filter(
            Subject.classroom_id == turma.id
        )
    )

    if allowed_subject_ids is not None:

        disciplinas_query = (
            disciplinas_query
            .filter(
                Subject.id.in_(
                    allowed_subject_ids
                )
            )
        )

    disciplinas = disciplinas_query.all()

    resultado = []


    # =====================================================
    # DESEMPENHO POR DISCIPLINA
    # =====================================================

    for disciplina in disciplinas:

        # -------------------------------------------------
        # NOTAS
        # -------------------------------------------------

        notas = (
            db.query(Grade)
            .join(
                Assessment,
                Grade.assessment_id == Assessment.id
            )
            .filter(
                Grade.student_id == student_id,
                Assessment.subject_id == disciplina.id
            )
            .all()
        )

        if notas:

            media = (
                sum(
                    nota.nota
                    for nota in notas
                )
                / len(notas)
            )

            media = round(
                media,
                2
            )

        else:

            media = 0.0


        # -------------------------------------------------
        # FREQUÊNCIA
        # -------------------------------------------------

        total_presencas = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student_id,
                Attendance.subject_id == disciplina.id,
                Attendance.status == "presente"
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

        if total_aulas > 0:

            frequencia = round(
                (
                    total_presencas
                    / total_aulas
                )
                * 100,
                2
            )

        else:

            frequencia = 0.0


        # -------------------------------------------------
        # SITUAÇÃO
        # -------------------------------------------------

        if not notas:

            situacao = "Sem notas"

        elif media >= 7:

            situacao = "Aprovado"

        elif media >= 5:

            situacao = "Recuperação"

        else:

            situacao = "Reprovado"


        resultado.append(

            SubjectPerformance(
                disciplina=disciplina.nome,
                media=media,
                frequencia=frequencia,
                situacao=situacao
            )
        )


    # =====================================================
    # BOLETIM
    # =====================================================

    return AcademicRecordResponse(
        aluno=aluno.nome,
        turma=turma.nome,
        disciplinas=resultado
    )