from datetime import date, datetime, time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import (
    Assessment,
    Question,
    StudentAnswer,
    User,
    Teacher
)

# =========================================================
# AVALIAÇÕES
# =========================================================

def create_assessment(
    db: Session,
    user_id: int,
    assessment
):
    """
    Cria uma avaliação para o professor autenticado.

    Recebemos o ID do User e localizamos o Teacher
    correspondente antes de criar a avaliação.
    """

    teacher = (
        db.query(Teacher)
        .filter(Teacher.user_id == user_id)
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor não encontrado."
        )

    nova = Assessment(
        titulo=assessment.titulo,
        descricao=assessment.descricao,
        tipo=assessment.tipo,
        data=assessment.data,
        valor=assessment.valor,

        ativa=assessment.ativa,
        semestre=assessment.semestre,
        ano_letivo=assessment.ano_letivo,

        teacher_id=teacher.id,
        classroom_id=assessment.classroom_id,
        subject_id=assessment.subject_id
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)

    return nova


def get_all_assessments(
    db: Session
):
    return db.query(Assessment).all()


def get_assessment_by_id(
    db: Session,
    assessment_id: int
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )

    return assessment


def update_assessment(
    db: Session,
    assessment_id: int,
    data
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            assessment,
            field,
            value
        )

    db.commit()
    db.refresh(assessment)

    return assessment


# =========================================================
# RESULTADO INDIVIDUAL
# =========================================================

def get_student_assessment_result(
    db: Session,
    assessment_id: int,
    user_id: int
):
    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )

    questions = (
        db.query(Question)
        .filter(
            Question.assessment_id == assessment_id
        )
        .all()
    )

    if not questions:
        return {
            "assessment_id": assessment_id,
            "user_id": user_id,

            "total_questoes": 0,
            "questoes_respondidas": 0,
            "questoes_corrigidas": 0,
            "questoes_pendentes": 0,

            "pontos_obtidos": 0,
            "pontos_possiveis": 0,

            "percentual": 0,
            "nota_final": 0
        }

    question_ids = [
        question.id
        for question in questions
    ]

    answers = (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.user_id == user_id,
            StudentAnswer.question_id.in_(
                question_ids
            )
        )
        .order_by(StudentAnswer.id)
        .all()
    )

    # Se houver mais de uma resposta para uma questão,
    # utiliza a mais recente.
    latest_answers = {}

    for answer in answers:
        latest_answers[
            answer.question_id
        ] = answer

    total_questoes = len(questions)

    questoes_respondidas = len(
        latest_answers
    )

    questoes_corrigidas = 0

    pontos_obtidos = 0.0

    pontos_possiveis = sum(
        question.peso or 1
        for question in questions
    )

    for answer in latest_answers.values():

        if answer.percentual_final is not None:

            questoes_corrigidas += 1

            pontos_obtidos += (
                answer.pontuacao_obtida or 0
            )

    # Aqui "pendente" significa:
    # respondeu, mas ainda não foi corrigida.
    questoes_pendentes = (
        questoes_respondidas
        - questoes_corrigidas
    )

    if pontos_possiveis > 0:

        percentual = (
            pontos_obtidos
            / pontos_possiveis
        ) * 100

    else:

        percentual = 0

    nota_final = (
        percentual / 100
    ) * (
        assessment.valor or 10
    )

    return {
        "assessment_id": assessment_id,
        "user_id": user_id,

        "total_questoes": total_questoes,
        "questoes_respondidas": questoes_respondidas,
        "questoes_corrigidas": questoes_corrigidas,
        "questoes_pendentes": questoes_pendentes,

        "pontos_obtidos": round(
            pontos_obtidos,
            2
        ),

        "pontos_possiveis": round(
            pontos_possiveis,
            2
        ),

        "percentual": round(
            percentual,
            2
        ),

        "nota_final": round(
            nota_final,
            2
        )
    }


# =========================================================
# RESULTADO DE UM ALUNO PARA O PROFESSOR
# =========================================================

def get_student_result_for_teacher(
    db: Session,
    assessment_id: int,
    student_id: int
):
    return get_student_assessment_result(
        db,
        assessment_id,
        student_id
    )


# =========================================================
# RESULTADOS DA TURMA
# =========================================================

def get_assessment_results(
    db: Session,
    assessment_id: int
):
    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )

    questions = (
        db.query(Question)
        .filter(
            Question.assessment_id
            == assessment_id
        )
        .all()
    )

    if not questions:
        return []

    question_ids = [
        question.id
        for question in questions
    ]

    answers = (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.question_id.in_(
                question_ids
            )
        )
        .all()
    )

    student_ids = list(
        {
            answer.user_id
            for answer in answers
        }
    )

    results = []

    for student_id in student_ids:

        result = (
            get_student_assessment_result(
                db,
                assessment_id,
                student_id
            )
        )

        student = (
            db.query(User)
            .filter(
                User.id == student_id
            )
            .first()
        )

        results.append({
            "user_id": student_id,

            "nome": (
                student.nome
                if student
                else "Aluno"
            ),

            "percentual":
                result["percentual"],

            "nota_final":
                result["nota_final"],

            "questoes_respondidas":
                result[
                    "questoes_respondidas"
                ],

            "questoes_corrigidas":
                result[
                    "questoes_corrigidas"
                ],

            "questoes_pendentes":
                result[
                    "questoes_pendentes"
                ]
        })

    return results


# =========================================================
# HISTÓRICO DO ALUNO
# =========================================================

def get_student_assessment_history(
    db: Session,
    user_id: int
):
    assessments = (
        db.query(Assessment)
        .all()
    )

    history = []

    for assessment in assessments:

        questions = (
            db.query(Question)
            .filter(
                Question.assessment_id
                == assessment.id
            )
            .all()
        )

        if not questions:
            continue

        question_ids = [
            question.id
            for question in questions
        ]

        answer = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.user_id
                == user_id,

                StudentAnswer.question_id.in_(
                    question_ids
                )
            )
            .first()
        )

        # Não coloca no histórico
        # avaliações nunca respondidas.
        if not answer:
            continue

        result = (
            get_student_assessment_result(
                db,
                assessment.id,
                user_id
            )
        )

        history.append({
            "assessment_id":
                assessment.id,

            "titulo":
                assessment.titulo,

            "subject_id":
                assessment.subject_id,

            "semestre":
                assessment.semestre,

            "ano_letivo":
                assessment.ano_letivo,

            "percentual":
                result["percentual"],

            "nota_final":
                result["nota_final"]
        })

    return history


# =========================================================
# CLASSIFICAÇÃO DE DESEMPENHO
# =========================================================

def classificar_desempenho(
    percentual: float
):

    if percentual < 50:
        return "Baixo"

    if percentual < 70:
        return "Regular"

    if percentual < 85:
        return "Bom"

    return "Excelente"


# =========================================================
# HISTÓRICO DO ALUNO COM FILTROS
# =========================================================

def get_student_assessment_history_filtered(
    db: Session,
    user_id: int,

    subject_id: int | None = None,
    semestre: int | None = None,
    ano_letivo: int | None = None,

    classroom_id: int | None = None,
    teacher_id: int | None = None,

    tipo: str | None = None,

    data_inicio: date | None = None,
    data_fim: date | None = None,

    status_desempenho: str | None = None
):

    assessments_query = (
        db.query(Assessment)
    )

    # DISCIPLINA
    if subject_id is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.subject_id
                == subject_id
            )
        )

    # SEMESTRE
    if semestre is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.semestre
                == semestre
            )
        )

    # ANO LETIVO
    if ano_letivo is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.ano_letivo
                == ano_letivo
            )
        )

    # TURMA
    if classroom_id is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.classroom_id
                == classroom_id
            )
        )

    # PROFESSOR
    if teacher_id is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.teacher_id
                == teacher_id
            )
        )

    # TIPO DE AVALIAÇÃO
    if tipo is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.tipo
                == tipo
            )
        )

    # DATA INICIAL
    if data_inicio is not None:

        inicio = datetime.combine(
            data_inicio,
            time.min
        )

        assessments_query = (
            assessments_query.filter(
                Assessment.data >= inicio
            )
        )

    # DATA FINAL
    if data_fim is not None:

        fim = datetime.combine(
            data_fim,
            time.max
        )

        assessments_query = (
            assessments_query.filter(
                Assessment.data <= fim
            )
        )

    assessments = (
        assessments_query.all()
    )

    history = []

    for assessment in assessments:

        questions = (
            db.query(Question)
            .filter(
                Question.assessment_id
                == assessment.id
            )
            .all()
        )

        if not questions:
            continue

        question_ids = [
            question.id
            for question in questions
        ]

        answer = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.user_id
                == user_id,

                StudentAnswer.question_id.in_(
                    question_ids
                )
            )
            .first()
        )

        # O aluno não respondeu
        # essa avaliação.
        if not answer:
            continue

        result = (
            get_student_assessment_result(
                db,
                assessment.id,
                user_id
            )
        )

        status = (
            classificar_desempenho(
                result["percentual"]
            )
        )

        if status_desempenho is not None:

            if (
                status.lower()
                != status_desempenho.lower()
            ):
                continue

        history.append({
            "assessment_id":
                assessment.id,

            "titulo":
                assessment.titulo,

            "subject_id":
                assessment.subject_id,

            "classroom_id":
                assessment.classroom_id,

            "teacher_id":
                assessment.teacher_id,

            "tipo":
                assessment.tipo,

            "semestre":
                assessment.semestre,

            "ano_letivo":
                assessment.ano_letivo,

            "percentual":
                result["percentual"],

            "nota_final":
                result["nota_final"],

            "status_desempenho":
                status
        })

    return history

def get_student_summary(
    db: Session,
    user_id: int
):
    history = get_student_assessment_history(
        db,
        user_id
    )

    if not history:
        return {
            "avaliacoes_realizadas": 0,
            "media_geral": 0,
            "percentual_medio": 0,
            "melhor_nota": None,
            "pior_nota": None,
            "melhor_percentual": None,
            "pior_percentual": None,
            "status_geral": "Sem dados"
        }

    notas = [
        item["nota_final"]
        for item in history
    ]

    percentuais = [
        item["percentual"]
        for item in history
    ]

    media_geral = (
        sum(notas)
        / len(notas)
    )

    percentual_medio = (
        sum(percentuais)
        / len(percentuais)
    )

    return {
        "avaliacoes_realizadas":
            len(history),

        "media_geral":
            round(media_geral, 2),

        "percentual_medio":
            round(percentual_medio, 2),

        "melhor_nota":
            round(max(notas), 2),

        "pior_nota":
            round(min(notas), 2),

        "melhor_percentual":
            round(max(percentuais), 2),

        "pior_percentual":
            round(min(percentuais), 2),

        "status_geral":
            classificar_desempenho(
                percentual_medio
            )
    }