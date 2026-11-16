from collections import defaultdict
from statistics import mean

from sqlalchemy.orm import Session

from app.database.models import (
    User,
    Grade,
    Attendance,
    StudentAnswer,
    Enrollment,
)


def _average(values):
    values = [
        float(v)
        for v in values
        if v is not None
    ]
    if not values:
        return None
    return round(mean(values), 1)


def _grade_percent(grade):
    assessment = grade.assessment
    if not assessment:
        return None

    maximum = float(assessment.valor or 10)
    if maximum <= 0:
        return None

    return round(
        max(
            0.0,
            min(
                100.0,
                (float(grade.nota) / maximum) * 100,
            ),
        ),
        1,
    )


def _answer_percent(answer):
    for value in (
        answer.percentual_final,
        answer.percentual_professor,
        answer.percentual_ia,
    ):
        if value is not None:
            return round(float(value), 1)
    return None


def build_student_metrics(
    db: Session,
    student: User,
) -> dict:
    grades = (
        db.query(Grade)
        .filter(Grade.student_id == student.id)
        .all()
    )

    attendance_rows = (
        db.query(Attendance)
        .filter(Attendance.student_id == student.id)
        .all()
    )

    answers = (
        db.query(StudentAnswer)
        .filter(StudentAnswer.user_id == student.id)
        .all()
    )

    active_enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == student.id,
            Enrollment.ativo == True,
        )
        .first()
    )

    by_subject = defaultdict(list)

    for grade in grades:
        assessment = grade.assessment
        if not assessment:
            continue

        subject_name = (
            assessment.subject.nome
            if assessment.subject
            else "Disciplina"
        )

        pct = _grade_percent(grade)
        if pct is not None:
            by_subject[subject_name].append(pct)

    subjects = [
        {
            "disciplina": name,
            "media_percentual": _average(values),
            "avaliacoes": len(values),
        }
        for name, values in by_subject.items()
    ]

    subjects.sort(
        key=lambda item: (
            item["media_percentual"]
            if item["media_percentual"] is not None
            else 999
        )
    )

    total = len(attendance_rows)

    present = sum(
        1
        for row in attendance_rows
        if str(row.status or "").strip().lower()
        == "presente"
    )

    absences = sum(
        1
        for row in attendance_rows
        if str(row.status or "").strip().lower()
        == "falta"
    )

    late = sum(
        1
        for row in attendance_rows
        if str(row.status or "").strip().lower()
        == "atraso"
    )

    attendance_rate = (
        round((present / total) * 100, 1)
        if total
        else None
    )

    answer_scores = [
        score
        for score in (
            _answer_percent(answer)
            for answer in answers
        )
        if score is not None
    ]

    return {
        "serie": student.serie,
        "objetivo_declarado": student.objetivo,
        "dificuldades_declaradas": student.dificuldades,
        "horas_estudo_dia": student.horas_estudo,
        "classroom_id": (
            active_enrollment.classroom_id
            if active_enrollment
            else None
        ),
        "media_geral_percentual": _average([
            item["media_percentual"]
            for item in subjects
        ]),
        "desempenho_por_disciplina": subjects,
        "frequencia": {
            "registros": total,
            "presentes": present,
            "faltas": absences,
            "atrasos": late,
            "taxa_presenca": attendance_rate,
        },
        "respostas_avaliadas": {
            "quantidade": len(answer_scores),
            "media_percentual": _average(answer_scores),
        },
    }


def classify_profile(metrics: dict) -> str:
    grade = metrics.get("media_geral_percentual")
    attendance = (
        metrics.get("frequencia", {})
        .get("taxa_presenca")
    )

    if grade is None and attendance is None:
        return "dados_insuficientes"

    if (
        grade is not None
        and attendance is not None
        and grade >= 80
        and attendance >= 90
    ):
        return "alto_desempenho"

    if (
        grade is not None
        and attendance is not None
        and grade < 50
        and attendance < 75
    ):
        return "risco_pedagogico"

    if (
        (grade is not None and grade < 60)
        or (
            attendance is not None
            and attendance < 80
        )
    ):
        return "atencao"

    return "estavel"
