from datetime import (
    datetime,
    timedelta
)

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.models import (
    Attendance,
    Teacher
)


# =========================================================
# EDITAR FREQUENCIA
#
# Somente o professor que lancou.
# Prazo maximo: 24 horas.
# =========================================================

def edit_attendance(

    db: Session,

    attendance_id: int,

    teacher_user_id: int,

    data

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


    attendance = (
        db.query(Attendance)
        .filter(
            Attendance.id
            == attendance_id
        )
        .first()
    )


    if not attendance:

        raise HTTPException(
            status_code=404,
            detail=(
                "Registro de frequência "
                "não encontrado."
            )
        )


    # =====================================================
    # SOMENTE O PROFESSOR DONO
    # =====================================================

    if (
        attendance.teacher_id
        != teacher.id
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Somente o professor que "
                "registrou esta frequência "
                "pode alterá-la."
            )
        )


    # =====================================================
    # PRAZO DE 24 HORAS
    # =====================================================

    limite = (
        attendance.data
        + timedelta(
            hours=24
        )
    )


    if datetime.now() > limite:

        raise HTTPException(
            status_code=400,
            detail=(
                "O prazo de 24 horas para "
                "alterar esta frequência terminou."
            )
        )


    # =====================================================
    # STATUS
    # =====================================================

    status = (
        data.status
        or ""
    ).strip().lower()


    if status not in [
        "presente",
        "falta"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "Status inválido. "
                "Utilize presente ou falta."
            )
        )


    # =====================================================
    # PRESENTE
    # =====================================================

    if status == "presente":

        attendance.status = (
            "presente"
        )

        attendance.justificada = False

        attendance.motivo = None

        attendance.arquivo = None


    # =====================================================
    # FALTA
    # =====================================================

    else:

        if data.justificada:

            motivo = (
                data.motivo
                or ""
            ).strip()


            if not motivo:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Informe o motivo da "
                        "falta justificada."
                    )
                )


            attendance.status = (
                "falta_justificada"
            )

            attendance.justificada = True

            attendance.motivo = (
                motivo
            )

            attendance.arquivo = (
                data.arquivo
            )


        else:

            attendance.status = (
                "falta_pendente"
            )

            attendance.justificada = False

            attendance.motivo = None

            attendance.arquivo = None


    if data.observacao is not None:

        attendance.observacao = (
            data.observacao
        )


    db.commit()

    db.refresh(
        attendance
    )


    return attendance