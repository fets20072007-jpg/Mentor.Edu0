from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func

from app.database.models import (
    StudentAnswer,
    Question,
    Assessment,
    Teacher,
    Enrollment
)


# =========================================================
# CÁLCULO DE PONTUAÇÃO
# =========================================================

def calcular_pontuacao(
    peso: float,
    percentual: float
):

    return peso * (
        percentual / 100
    )


# =========================================================
# REGISTRAR RESPOSTA DO ALUNO
# =========================================================

def register_answer(
    db: Session,
    question_id: int,
    current_user,
    data
):

    # -----------------------------------------------------
    # QUESTÃO
    # -----------------------------------------------------

    question = (
        db.query(Question)
        .filter(
            Question.id
            == question_id
        )
        .first()
    )

    if not question:

        raise HTTPException(
            status_code=404,
            detail="Questão não encontrada."
        )


    # -----------------------------------------------------
    # QUESTÃO PRECISA PERTENCER A UMA AVALIAÇÃO
    # -----------------------------------------------------

    if question.assessment_id is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Questão não encontrada "
                "ou sem acesso."
            )
        )


    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id
            == question.assessment_id
        )
        .first()
    )

    if not assessment:

        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )


    # -----------------------------------------------------
    # AVALIAÇÃO ATIVA
    # -----------------------------------------------------

    if not assessment.ativa:

        raise HTTPException(
            status_code=403,
            detail=(
                "Esta avaliação não está "
                "disponível para respostas."
            )
        )


    # -----------------------------------------------------
    # MATRÍCULA DO ALUNO NA TURMA
    # -----------------------------------------------------

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id
            == current_user.id,

            Enrollment.classroom_id
            == assessment.classroom_id,

            Enrollment.ativo
            == True
        )
        .first()
    )

    if not enrollment:

        raise HTTPException(
            status_code=403,
            detail=(
                "Você não possui matrícula ativa "
                "na turma desta avaliação."
            )
        )


    # -----------------------------------------------------
    # BLOQUEIA RESPOSTA DUPLICADA
    # -----------------------------------------------------

    existing_answer = (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.user_id
            == current_user.id,

            StudentAnswer.question_id
            == question.id
        )
        .first()
    )

    if existing_answer:

        raise HTTPException(
            status_code=409,
            detail=(
                "Esta questão já foi respondida."
            )
        )


    # -----------------------------------------------------
    # RESPOSTA NÃO PODE ESTAR VAZIA
    # -----------------------------------------------------

    resposta = (
        data.resposta.strip()
        if data.resposta
        else ""
    )

    if not resposta:

        raise HTTPException(
            status_code=400,
            detail=(
                "A resposta não pode estar vazia."
            )
        )


    # =====================================================
    # CORREÇÃO AUTOMÁTICA
    #
    # Questão objetiva:
    # 0% ou 100%.
    #
    # Questões não objetivas:
    # ficam pendentes para o professor.
    # =====================================================

    percentual_final = None
    pontuacao_obtida = None


    tipo_questao = (
        question.tipo
        or ""
    ).strip().lower()


    if tipo_questao == "objetiva":

        if not question.resposta_correta:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Questão objetiva sem "
                    "resposta correta cadastrada."
                )
            )


        resposta_aluno = (
            resposta
            .strip()
            .upper()
        )

        resposta_correta = (
            question.resposta_correta
            .strip()
            .upper()
        )


        if (
            resposta_aluno
            == resposta_correta
        ):

            percentual_final = 100

        else:

            percentual_final = 0


        peso = (
            question.peso
            or 1.0
        )

        pontuacao_obtida = (
            calcular_pontuacao(
                peso,
                percentual_final
            )
        )


    # =====================================================
    # SALVA RESPOSTA
    # =====================================================

    answer = StudentAnswer(

        resposta=resposta,

        tempo_resposta=getattr(
            data,
            "tempo_resposta",
            None
        ),

        percentual_final=(
            percentual_final
        ),

        pontuacao_obtida=(
            pontuacao_obtida
        ),

        corrigida_ia=False,

        revisada_professor=False,

        question_id=(
            question.id
        ),

        user_id=(
            current_user.id
        )
    )


    db.add(
        answer
    )


    try:

        db.commit()


    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Esta questão já foi respondida."
            )
        )


    db.refresh(
        answer
    )

    return answer


# =========================================================
# CORREÇÕES PENDENTES DO PROFESSOR
#
# Retorna apenas:
#
# - respostas de avaliações do professor;
# - questões não objetivas;
# - respostas ainda não revisadas pelo professor.
#
# DT NÃO recebe respostas de avaliações de outros professores.
# =========================================================

def get_pending_answers(
    db: Session,
    teacher_user_id: int
):

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id
            == teacher_user_id
        )
        .first()
    )

    if not teacher:

        raise HTTPException(
            status_code=404,
            detail=(
                "Perfil de professor "
                "não encontrado."
            )
        )


    answers = (
        db.query(StudentAnswer)
        .join(
            Question,
            StudentAnswer.question_id
            == Question.id
        )
        .join(
            Assessment,
            Question.assessment_id
            == Assessment.id
        )
        .filter(
            Assessment.teacher_id
            == teacher.id,

            StudentAnswer.revisada_professor
            == False,

            or_(
                Question.tipo.is_(None),

                func.lower(
                    func.trim(
                        Question.tipo
                    )
                )
                != "objetiva"
            )
        )
        .order_by(
            StudentAnswer.id.asc()
        )
        .all()
    )

    return answers


# =========================================================
# CORREÇÃO / REVISÃO DO PROFESSOR
# =========================================================

def review_answer(
    db: Session,
    answer_id: int,
    teacher_user_id: int,
    percentual_professor: float
):

    # -----------------------------------------------------
    # VALIDA PERCENTUAL
    # -----------------------------------------------------

    percentuais_validos = [
        0,
        25,
        50,
        75,
        100
    ]


    if (
        percentual_professor
        not in percentuais_validos
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "O percentual deve ser "
                "0, 25, 50, 75 ou 100."
            )
        )


    # -----------------------------------------------------
    # PROFESSOR
    # -----------------------------------------------------

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id
            == teacher_user_id
        )
        .first()
    )

    if not teacher:

        raise HTTPException(
            status_code=404,
            detail=(
                "Perfil de professor "
                "não encontrado."
            )
        )


    # -----------------------------------------------------
    # RESPOSTA
    # -----------------------------------------------------

    answer = (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.id
            == answer_id
        )
        .first()
    )

    if not answer:

        raise HTTPException(
            status_code=404,
            detail="Resposta não encontrada."
        )


    # -----------------------------------------------------
    # QUESTÃO
    # -----------------------------------------------------

    question = (
        db.query(Question)
        .filter(
            Question.id
            == answer.question_id
        )
        .first()
    )

    if not question:

        raise HTTPException(
            status_code=404,
            detail="Questão não encontrada."
        )


    # -----------------------------------------------------
    # AVALIAÇÃO
    #
    # Somente o professor proprietário pode corrigir.
    # Ser DT da turma NÃO permite corrigir
    # avaliação de outro professor.
    # -----------------------------------------------------

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id
            == question.assessment_id,

            Assessment.teacher_id
            == teacher.id
        )
        .first()
    )

    if not assessment:

        raise HTTPException(
            status_code=404,
            detail=(
                "Esta resposta não pertence "
                "a uma avaliação deste professor."
            )
        )


    # -----------------------------------------------------
    # CALCULA PONTUAÇÃO
    # -----------------------------------------------------

    peso = (
        question.peso
        or 1.0
    )

    pontuacao = (
        calcular_pontuacao(
            peso,
            percentual_professor
        )
    )


    # -----------------------------------------------------
    # SALVA REVISÃO
    # -----------------------------------------------------

    answer.percentual_professor = (
        percentual_professor
    )

    answer.percentual_final = (
        percentual_professor
    )

    answer.pontuacao_obtida = (
        pontuacao
    )

    answer.revisada_professor = True


    db.commit()

    db.refresh(
        answer
    )

    return answer