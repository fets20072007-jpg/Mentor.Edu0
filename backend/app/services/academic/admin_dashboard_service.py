from sqlalchemy.orm import Session

from app.database.models import (
    User,
    Teacher,
    Classroom
)

from app.services.academic.assessment_service import (
    get_student_assessment_result
)

def get_admin_teachers(
    db: Session
):
    teachers = (
        db.query(Teacher)
        .all()
    )

    results = []

    for teacher in teachers:

        user = (
            db.query(User)
            .filter(
                User.id == teacher.user_id
            )
            .first()
        )

        if not user:
            continue

        results.append({
            "user_id":
                user.id,

            "nome":
                user.nome,

            "email":
                user.email,

            "especialidade":
                teacher.especialidade,

            "ativo":
                teacher.ativo
        })

    return results


def get_admin_students(
    db: Session,
    nome: str | None = None,
    escola: str | None = None,
    serie: str | None = None
):
    query = (
        db.query(User)
        .filter(
            User.tipo.ilike("aluno")
        )
    )

    if escola:
        query = query.filter(
            User.escola.ilike(
                f"%{escola.strip()}%"
            )
        )

    if serie:
        query = query.filter(
            User.serie.ilike(
                f"%{serie.strip()}%"
            )
        )

    students = query.all()

    results = []

    for student in students:

        if nome:
            if (
                nome.strip().lower()
                not in student.nome.lower()
            ):
                continue

        results.append({
            "user_id": student.id,
            "nome": student.nome,
            "email": student.email,
            "escola": student.escola,
            "serie": student.serie
        })

    results.sort(
        key=lambda item:
            item["nome"].lower()
    )

    return results

def get_admin_classrooms(
    db: Session
):
    classrooms = (
        db.query(Classroom)
        .all()
    )

    return [
        {
            "classroom_id":
                classroom.id,

            "nome":
                classroom.nome,

            "ano_letivo":
                getattr(
                    classroom,
                    "ano_letivo",
                    None
                )
        }
        for classroom in classrooms
    ]

from app.database.models import Assessment


def get_admin_summary(
    db: Session
):
    total_alunos = (
        db.query(User)
        .filter(
            User.tipo.ilike("aluno")
        )
        .count()
    )

    total_professores = (
        db.query(Teacher)
        .count()
    )

    total_turmas = (
        db.query(Classroom)
        .count()
    )

    total_avaliacoes = (
        db.query(Assessment)
        .count()
    )

    avaliacoes_ativas = (
        db.query(Assessment)
        .filter(
            Assessment.ativa == True
        )
        .count()
    )

    return {
        "total_alunos":
            total_alunos,

        "total_professores":
            total_professores,

        "total_turmas":
            total_turmas,

        "total_avaliacoes":
            total_avaliacoes,

        "avaliacoes_ativas":
            avaliacoes_ativas
    }

def get_admin_teachers(
    db: Session,
    nome: str | None = None,
    especialidade: str | None = None,
    ativo: bool | None = None
):
    query = db.query(Teacher)

    if especialidade:
        query = query.filter(
            Teacher.especialidade.ilike(
                f"%{especialidade.strip()}%"
            )
        )

    if ativo is not None:
        query = query.filter(
            Teacher.ativo == ativo
        )

    teachers = query.all()

    results = []

    for teacher in teachers:
        user = (
            db.query(User)
            .filter(
                User.id == teacher.user_id
            )
            .first()
        )

        if not user:
            continue

        if nome:
            if nome.strip().lower() not in user.nome.lower():
                continue

        results.append({
            "user_id": user.id,
            "nome": user.nome,
            "email": user.email,
            "especialidade": teacher.especialidade,
            "ativo": teacher.ativo
        })

    results.sort(
        key=lambda item: item["nome"].lower()
    )

    return results

from fastapi import HTTPException


def get_admin_teacher_by_id(
    db: Session,
    user_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == user_id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado."
        )

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário do professor não encontrado."
        )

    return {
        "user_id": user.id,
        "nome": user.nome,
        "email": user.email,
        "especialidade": teacher.especialidade,
        "ativo": teacher.ativo
    }

def get_admin_student_by_id(
    db: Session,
    user_id: int
):
    student = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tipo.ilike("aluno")
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado."
        )

    return {
        "user_id": student.id,
        "nome": student.nome,
        "email": student.email,
        "escola": student.escola,
        "serie": student.serie
    }


def get_admin_classroom_by_id(
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

    return {
        "classroom_id": classroom.id,
        "nome": classroom.nome,
        "ano_letivo": classroom.ano
    }

from app.database.models import (
    User,
    Teacher,
    Classroom,
    Assessment,
    Question,
    StudentAnswer
)


def get_admin_teacher_summary(
    db: Session,
    user_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == user_id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado."
        )

    assessments = (
        db.query(Assessment)
        .filter(
            Assessment.teacher_id == teacher.id
        )
        .all()
    )

    classroom_ids = {
        assessment.classroom_id
        for assessment in assessments
        if assessment.classroom_id is not None
    }

    student_ids = set()

    for assessment in assessments:

        questions = (
            db.query(Question)
            .filter(
                Question.assessment_id == assessment.id
            )
            .all()
        )

        question_ids = [
            question.id
            for question in questions
        ]

        if not question_ids:
            continue

        answers = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.question_id.in_(
                    question_ids
                )
            )
            .all()
        )

        for answer in answers:
            student_ids.add(
                answer.user_id
            )

    return {
        "user_id":
            user_id,

        "total_avaliacoes":
            len(assessments),

        "total_turmas":
            len(classroom_ids),

        "total_alunos_avaliados":
            len(student_ids)
    }


def get_admin_classroom_summary(
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

    assessments = (
        db.query(Assessment)
        .filter(
            Assessment.classroom_id == classroom_id
        )
        .all()
    )

    teacher_ids = {
        assessment.teacher_id
        for assessment in assessments
    }

    student_ids = set()
    percentuais = []

    for assessment in assessments:

        questions = (
            db.query(Question)
            .filter(
                Question.assessment_id == assessment.id
            )
            .all()
        )

        question_ids = [
            question.id
            for question in questions
        ]

        if not question_ids:
            continue

        answers = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.question_id.in_(
                    question_ids
                )
            )
            .all()
        )

        latest_answers = {}

        for answer in answers:

            key = (
                answer.user_id,
                answer.question_id
            )

            current = latest_answers.get(
                key
            )

            if (
                current is None
                or answer.id > current.id
            ):
                latest_answers[key] = answer

        for answer in latest_answers.values():

            student_ids.add(
                answer.user_id
            )

            if answer.percentual_final is not None:
                percentuais.append(
                    answer.percentual_final
                )

    if percentuais:
        percentual_medio = (
            sum(percentuais)
            / len(percentuais)
        )
    else:
        percentual_medio = 0

    if percentual_medio < 50:
        status = "Baixo"
    elif percentual_medio < 70:
        status = "Regular"
    elif percentual_medio < 85:
        status = "Bom"
    else:
        status = "Excelente"

    return {
        "classroom_id":
            classroom_id,

        "total_avaliacoes":
            len(assessments),

        "total_professores":
            len(teacher_ids),

        "total_alunos_avaliados":
            len(student_ids),

        "percentual_medio":
            round(
                percentual_medio,
                2
            ),

        "status":
            status
    }

def get_admin_student_summary(
    db: Session,
    user_id: int
):
    student = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.tipo.ilike("aluno")
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado."
        )

    answers = (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.user_id == user_id
        )
        .all()
    )

    assessment_ids = set()

    for answer in answers:

        question = (
            db.query(Question)
            .filter(
                Question.id == answer.question_id
            )
            .first()
        )

        if (
            question
            and question.assessment_id
            is not None
        ):
            assessment_ids.add(
                question.assessment_id
            )

    notas = []
    percentuais = []
    subject_ids = set()

    for assessment_id in assessment_ids:

        assessment = (
            db.query(Assessment)
            .filter(
                Assessment.id == assessment_id
            )
            .first()
        )

        if not assessment:
            continue

        if assessment.subject_id is not None:
            subject_ids.add(
                assessment.subject_id
            )

        result = get_student_assessment_result(
            db=db,
            assessment_id=assessment_id,
            user_id=user_id
        )

        notas.append(
            result["nota_final"]
        )

        percentuais.append(
            result["percentual"]
        )

    if notas:
        media_geral = (
            sum(notas)
            / len(notas)
        )

        percentual_medio = (
            sum(percentuais)
            / len(percentuais)
        )

        if percentual_medio < 50:
            status = "Baixo"

        elif percentual_medio < 70:
            status = "Regular"

        elif percentual_medio < 85:
            status = "Bom"

        else:
            status = "Excelente"

    else:
        media_geral = 0
        percentual_medio = 0
        status = "Sem dados"

    return {
        "user_id":
            user_id,

        "total_avaliacoes":
            len(assessment_ids),

        "total_disciplinas":
            len(subject_ids),

        "media_geral":
            round(media_geral, 2),

        "percentual_medio":
            round(percentual_medio, 2),

        "status":
            status
    }