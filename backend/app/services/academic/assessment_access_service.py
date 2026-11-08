from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import (
    User,
    Teacher,
    Assessment,
    Question,
    StudentAnswer,
    Enrollment
)

from app.services.system.notification_service import (
    create_notification
)


# =========================================================
# PROFESSOR DONO DA AVALIACAO
# =========================================================

def get_owned_assessment(

    db: Session,

    assessment_id: int,

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


    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id
            == assessment_id,

            Assessment.teacher_id
            == teacher.id
        )
        .first()
    )


    if not assessment:

        raise HTTPException(
            status_code=404,
            detail=(
                "Avaliação não encontrada "
                "ou não pertence a este professor."
            )
        )


    return assessment


# =========================================================
# ALUNO + AVALIACAO
# =========================================================

def get_student_assessment(

    db: Session,

    assessment_id: int,

    student_id: int

):

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id
            == assessment_id,

            Assessment.ativa
            == True
        )
        .first()
    )


    if not assessment:

        raise HTTPException(
            status_code=404,
            detail=(
                "Avaliação não encontrada "
                "ou inativa."
            )
        )


    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id
            == student_id,

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
                "O aluno não possui matrícula "
                "ativa na turma desta avaliação."
            )
        )


    return assessment


# =========================================================
# STATUS DA AVALIACAO
# =========================================================

def get_assessment_status(
    assessment: Assessment
):

    agora = datetime.now()


    if not assessment.ativa:

        return "inativa"


    if (
        assessment.data_abertura
        and agora
        < assessment.data_abertura
    ):

        return "agendada"


    if (
        assessment.data_encerramento
        and agora
        > assessment.data_encerramento
    ):

        return "encerrada"


    return "disponivel"


# =========================================================
# PODE RESPONDER?
# =========================================================

def assessment_can_be_answered(
    assessment: Assessment
):

    return (
        get_assessment_status(
            assessment
        )
        == "disponivel"
    )


# =========================================================
# VALIDAR JANELA DE RESPOSTAS
# =========================================================

def ensure_student_can_answer(

    db: Session,

    assessment_id: int,

    student_id: int

):

    assessment = get_student_assessment(

        db=db,

        assessment_id=assessment_id,

        student_id=student_id
    )


    status = get_assessment_status(
        assessment
    )


    if status == "agendada":

        raise HTTPException(
            status_code=403,
            detail=(
                "Esta avaliação ainda "
                "não foi liberada."
            )
        )


    if status == "encerrada":

        raise HTTPException(
            status_code=403,
            detail=(
                "O prazo desta avaliação "
                "já foi encerrado."
            )
        )


    if status == "inativa":

        raise HTTPException(
            status_code=403,
            detail=(
                "Esta avaliação está inativa."
            )
        )


    return assessment


# =========================================================
# ACESSO AS QUESTOES
#
# DURANTE A AVALIACAO:
# aluno pode ver normalmente.
#
# DEPOIS DO PRAZO:
# somente se liberar_prova=True.
# =========================================================

def ensure_student_can_view_questions(

    db: Session,

    assessment_id: int,

    student_id: int

):

    assessment = get_student_assessment(

        db=db,

        assessment_id=assessment_id,

        student_id=student_id
    )


    status = get_assessment_status(
        assessment
    )


    if status == "agendada":

        raise HTTPException(
            status_code=403,
            detail=(
                "Esta avaliação ainda "
                "não foi liberada."
            )
        )


    if (
        status == "encerrada"
        and not assessment.liberar_prova
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "A prova ainda não foi "
                "liberada para consulta."
            )
        )


    return assessment


# =========================================================
# RESULTADO DO ALUNO
# =========================================================

def ensure_student_result_released(

    db: Session,

    assessment_id: int,

    student_id: int

):

    assessment = get_student_assessment(

        db=db,

        assessment_id=assessment_id,

        student_id=student_id
    )


    if not assessment.liberar_resultado:

        raise HTTPException(
            status_code=403,
            detail=(
                "O resultado desta avaliação "
                "ainda não foi liberado."
            )
        )


    return assessment


# =========================================================
# CONFIGURAR JANELA / LIBERACOES
# =========================================================

def update_assessment_access(

    db: Session,

    assessment_id: int,

    teacher_user_id: int,

    data

):

    assessment = get_owned_assessment(

        db=db,

        assessment_id=assessment_id,

        teacher_user_id=teacher_user_id
    )


    update_data = (
        data.model_dump(
            exclude_unset=True
        )
    )


    # -----------------------------------------------------
    # DATAS RESULTANTES
    # -----------------------------------------------------

    data_abertura = (
        update_data.get(
            "data_abertura",
            assessment.data_abertura
        )
    )


    data_encerramento = (
        update_data.get(
            "data_encerramento",
            assessment.data_encerramento
        )
    )


    if (
        data_abertura is not None
        and data_encerramento is not None
        and data_abertura >= data_encerramento
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "A data de encerramento deve "
                "ser posterior à data de abertura."
            )
        )


    # -----------------------------------------------------
    # BLOQUEIA GABARITO / PROVA / RESULTADO
    # ANTES DO FIM QUANDO EXISTE PRAZO
    # -----------------------------------------------------

    agora = datetime.now()


    requested_release = any(
        update_data.get(field) is True
        for field in [
            "liberar_resultado",
            "liberar_prova",
            "liberar_gabarito"
        ]
    )


    if (
        requested_release
        and data_encerramento is not None
        and agora <= data_encerramento
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Não é possível liberar prova, "
                "resultado ou gabarito antes "
                "do encerramento da avaliação."
            )
        )


    # -----------------------------------------------------
    # VERIFICA SE HOUVE NOVA LIBERACAO
    # -----------------------------------------------------

    old_result = bool(
        assessment.liberar_resultado
    )

    old_test = bool(
        assessment.liberar_prova
    )

    old_key = bool(
        assessment.liberar_gabarito
    )


    # -----------------------------------------------------
    # APLICA ALTERACOES
    # -----------------------------------------------------

    for field, value in (
        update_data.items()
    ):

        setattr(
            assessment,
            field,
            value
        )


    new_release = (

        (
            not old_result
            and assessment.liberar_resultado
        )

        or

        (
            not old_test
            and assessment.liberar_prova
        )

        or

        (
            not old_key
            and assessment.liberar_gabarito
        )
    )


    # =====================================================
    # NOTIFICACOES
    # =====================================================

    if new_release:

        enrollments = (
            db.query(Enrollment)
            .filter(
                Enrollment.classroom_id
                == assessment.classroom_id,

                Enrollment.ativo
                == True
            )
            .all()
        )


        for enrollment in enrollments:

            create_notification(

                db=db,

                user_id=enrollment.user_id,

                titulo=(
                    "Avaliação atualizada"
                ),

                mensagem=(
                    f"Novos dados da avaliação "
                    f"'{assessment.titulo}' "
                    f"foram liberados."
                ),

                tipo="Avaliacao",

                link=(
                    f"/assessments/"
                    f"{assessment.id}"
                )
            )


    db.commit()

    db.refresh(
        assessment
    )


    return {
        "assessment_id":
            assessment.id,

        "data_abertura":
            assessment.data_abertura,

        "data_encerramento":
            assessment.data_encerramento,

        "liberar_resultado":
            assessment.liberar_resultado,

        "liberar_prova":
            assessment.liberar_prova,

        "liberar_gabarito":
            assessment.liberar_gabarito,

        "status":
            get_assessment_status(
                assessment
            )
    }


# =========================================================
# DISPONIBILIDADE DO ALUNO
# =========================================================

def get_student_availability(

    db: Session,

    assessment_id: int,

    student_id: int

):

    assessment = get_student_assessment(

        db=db,

        assessment_id=assessment_id,

        student_id=student_id
    )


    status = get_assessment_status(
        assessment
    )


    return {

        "assessment_id":
            assessment.id,

        "status":
            status,

        "pode_responder":
            status == "disponivel",

        "data_abertura":
            assessment.data_abertura,

        "data_encerramento":
            assessment.data_encerramento,

        "resultado_liberado":
            assessment.liberar_resultado,

        "prova_liberada":
            assessment.liberar_prova,

        "gabarito_liberado":
            assessment.liberar_gabarito
    }


# =========================================================
# PROVA RESPONDIDA
# =========================================================

def get_student_submission(

    db: Session,

    assessment_id: int,

    student_id: int

):

    assessment = get_student_assessment(

        db=db,

        assessment_id=assessment_id,

        student_id=student_id
    )


    if not assessment.liberar_prova:

        raise HTTPException(
            status_code=403,
            detail=(
                "A prova respondida ainda "
                "não foi liberada."
            )
        )


    questions = (
        db.query(Question)
        .filter(
            Question.assessment_id
            == assessment.id
        )
        .order_by(
            Question.id.asc()
        )
        .all()
    )


    result = []


    for question in questions:

        answer = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.question_id
                == question.id,

                StudentAnswer.user_id
                == student_id
            )
            .first()
        )


        result.append({

            "question_id":
                question.id,

            "enunciado":
                question.enunciado,

            "resposta":
                (
                    answer.resposta
                    if answer
                    else None
                )
        })


    return result


# =========================================================
# GABARITO
# =========================================================

def get_student_answer_key(

    db: Session,

    assessment_id: int,

    student_id: int

):

    assessment = get_student_assessment(

        db=db,

        assessment_id=assessment_id,

        student_id=student_id
    )


    if not assessment.liberar_gabarito:

        raise HTTPException(
            status_code=403,
            detail=(
                "O gabarito ainda "
                "não foi liberado."
            )
        )


    questions = (
        db.query(Question)
        .filter(
            Question.assessment_id
            == assessment.id
        )
        .order_by(
            Question.id.asc()
        )
        .all()
    )


    return [

        {
            "question_id":
                question.id,

            "enunciado":
                question.enunciado,

            "resposta_correta":
                question.resposta_correta,

            "explicacao":
                question.explicacao
        }

        for question in questions
    ]