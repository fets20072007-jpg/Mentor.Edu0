from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    User,
    Teacher,
    Subject,
    Classroom,
    Enrollment,
    Attendance
)

from app.schema.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceJustification
)

from app.security.auth import get_current_user

from app.core.permissions import (
    require_student,
    require_teacher,
    require_admin,
    require_teacher_or_admin
)


router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


# =========================================================
# FINALIZA FALTAS PENDENTES APÓS 24 HORAS
# =========================================================

def finalizar_faltas_pendentes(
    db: Session
):
    limite = datetime.now() - timedelta(hours=24)

    faltas = (
        db.query(Attendance)
        .filter(
            Attendance.status == "falta_pendente",
            Attendance.data < limite
        )
        .all()
    )

    for falta in faltas:
        falta.status = "falta_nao_justificada"
        falta.justificada = False

    if faltas:
        db.commit()


# =========================================================
# PROFESSOR
# REGISTRAR PRESENÇA / FALTA
# =========================================================

@router.post(
    "/",
    response_model=AttendanceResponse
)
def register_attendance(
    attendance: AttendanceCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # LOCALIZA O PROFESSOR
    # -----------------------------------------------------

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == current_user.id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor não encontrado."
        )

    # -----------------------------------------------------
    # CONFIRMA QUE A DISCIPLINA É DO PROFESSOR
    # -----------------------------------------------------

    subject = (
        db.query(Subject)
        .filter(
            Subject.id == attendance.subject_id,
            Subject.teacher_id == teacher.id
        )
        .first()
    )

    if not subject:
        raise HTTPException(
            status_code=403,
            detail=(
                "Esta disciplina não pertence "
                "ao professor autenticado."
            )
        )

    # -----------------------------------------------------
    # CONFIRMA VÍNCULO DA DISCIPLINA COM A TURMA
    # -----------------------------------------------------

    if subject.classroom_id != attendance.classroom_id:
        raise HTTPException(
            status_code=400,
            detail=(
                "A disciplina informada não pertence "
                "a esta turma."
            )
        )

    # -----------------------------------------------------
    # CONFIRMA TURMA
    # -----------------------------------------------------

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id == attendance.classroom_id
        )
        .first()
    )

    if not classroom:
        raise HTTPException(
            status_code=404,
            detail="Turma não encontrada."
        )

    # -----------------------------------------------------
    # CONFIRMA ALUNO
    # -----------------------------------------------------

    student = (
        db.query(User)
        .filter(
            User.id == attendance.student_id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado."
        )

    tipo_student = (
        student.tipo
        or ""
    ).strip().lower()

    if tipo_student != "aluno":
        raise HTTPException(
            status_code=400,
            detail="O usuário informado não é um aluno."
        )

    # -----------------------------------------------------
    # CONFIRMA MATRÍCULA ATIVA NA TURMA
    # -----------------------------------------------------

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == student.id,
            Enrollment.classroom_id == classroom.id,
            Enrollment.ativo == True
        )
        .first()
    )

    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail=(
                "Este aluno não possui matrícula ativa "
                "nesta turma."
            )
        )

    # -----------------------------------------------------
    # NORMALIZA STATUS
    # -----------------------------------------------------

    status = (
        attendance.status
        or ""
    ).strip().lower()

    if status not in [
        "presente",
        "falta"
    ]:
        raise HTTPException(
            status_code=400,
            detail=(
                "Status inválido. Utilize "
                "'presente' ou 'falta'."
            )
        )

    # -----------------------------------------------------
    # DEFINE SITUAÇÃO FINAL
    # -----------------------------------------------------

    if status == "presente":

        status_final = "presente"

        justificada = False
        motivo = None
        arquivo = None

    else:

        motivo = attendance.motivo
        arquivo = attendance.arquivo

        if attendance.justificada:

            if not motivo:
                raise HTTPException(
                    status_code=400,
                    detail="Informe o motivo da justificativa."
                )

            status_final = "falta_justificada"
            justificada = True

        else:

            status_final = "falta_pendente"
            justificada = False

    # -----------------------------------------------------
    # IMPEDE DUPLICAÇÃO
    # MESMO ALUNO + DISCIPLINA + DIA
    # -----------------------------------------------------

    agora = datetime.now()

    inicio_dia = datetime.combine(
        agora.date(),
        time.min
    )

    fim_dia = datetime.combine(
        agora.date(),
        time.max
    )

    registro_existente = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == student.id,
            Attendance.subject_id == subject.id,
            Attendance.data >= inicio_dia,
            Attendance.data <= fim_dia
        )
        .first()
    )

    if registro_existente:
        raise HTTPException(
            status_code=400,
            detail=(
                "A frequência deste aluno já foi "
                "registrada hoje nesta disciplina."
            )
        )

    # -----------------------------------------------------
    # CRIA REGISTRO
    # -----------------------------------------------------

    new_attendance = Attendance(
        data=agora,

        status=status_final,
        justificada=justificada,

        motivo=motivo,
        arquivo=arquivo,
        observacao=attendance.observacao,

        teacher_id=teacher.id,
        student_id=student.id,
        classroom_id=classroom.id,
        subject_id=subject.id
    )

    db.add(new_attendance)

    db.commit()
    db.refresh(new_attendance)

    return new_attendance


# =========================================================
# ADMINISTRAÇÃO
# CONSULTAR TODA A FREQUÊNCIA
# =========================================================

@router.get(
    "/",
    response_model=list[AttendanceResponse]
)
def list_attendance(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):

    finalizar_faltas_pendentes(db)

    return (
        db.query(Attendance)
        .order_by(
            Attendance.data.desc()
        )
        .all()
    )


# =========================================================
# ALUNO
# MINHA FREQUÊNCIA
# =========================================================

@router.get(
    "/me",
    response_model=list[AttendanceResponse]
)
def my_attendance(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):

    finalizar_faltas_pendentes(db)

    return (
        db.query(Attendance)
        .filter(
            Attendance.student_id == current_user.id
        )
        .order_by(
            Attendance.data.desc()
        )
        .all()
    )


# =========================================================
# ALUNO
# RESUMO DA MINHA FREQUÊNCIA
# =========================================================

@router.get(
    "/me/summary"
)
def my_attendance_summary(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):

    finalizar_faltas_pendentes(db)

    registros = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == current_user.id
        )
        .all()
    )

    total = len(registros)

    presentes = sum(
        1
        for item in registros
        if item.status == "presente"
    )

    justificadas = sum(
        1
        for item in registros
        if item.status == "falta_justificada"
    )

    nao_justificadas = sum(
        1
        for item in registros
        if item.status == "falta_nao_justificada"
    )

    pendentes = sum(
        1
        for item in registros
        if item.status == "falta_pendente"
    )

    percentual = (
        round(
            (presentes / total) * 100,
            2
        )
        if total > 0
        else 0
    )

    return {
        "aulas_registradas": total,
        "presencas": presentes,
        "faltas_justificadas": justificadas,
        "faltas_nao_justificadas": nao_justificadas,
        "faltas_pendentes": pendentes,
        "percentual_presenca": percentual
    }


# =========================================================
# PROFESSOR
# REGISTROS FEITOS POR MIM
# =========================================================

@router.get(
    "/teacher/me",
    response_model=list[AttendanceResponse]
)
def my_teacher_attendance(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):

    finalizar_faltas_pendentes(db)

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == current_user.id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor não encontrado."
        )

    return (
        db.query(Attendance)
        .filter(
            Attendance.teacher_id == teacher.id
        )
        .order_by(
            Attendance.data.desc()
        )
        .all()
    )


# =========================================================
# PROFESSOR
# FALTAS PENDENTES
# =========================================================

@router.get(
    "/teacher/pending",
    response_model=list[AttendanceResponse]
)
def teacher_pending_attendance(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):

    finalizar_faltas_pendentes(db)

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == current_user.id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor não encontrado."
        )

    return (
        db.query(Attendance)
        .filter(
            Attendance.teacher_id == teacher.id,
            Attendance.status == "falta_pendente"
        )
        .order_by(
            Attendance.data.desc()
        )
        .all()
    )


# =========================================================
# PROFESSOR / ADMINISTRAÇÃO
# FREQUÊNCIA DE UMA TURMA
#
# PROFESSOR COMUM:
# vê somente registros da própria atuação.
#
# DT:
# vê toda a frequência da turma pela qual é responsável.
# =========================================================

@router.get(
    "/classroom/{classroom_id}",
    response_model=list[AttendanceResponse]
)
def classroom_attendance(
    classroom_id: int,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):

    finalizar_faltas_pendentes(db)

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()

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

    # -----------------------------------------------------
    # ADMINISTRAÇÃO
    # -----------------------------------------------------

    if tipo in [
        "administracao",
        "administração"
    ]:

        return (
            db.query(Attendance)
            .filter(
                Attendance.classroom_id == classroom_id
            )
            .order_by(
                Attendance.data.desc()
            )
            .all()
        )

    # -----------------------------------------------------
    # PROFESSOR
    # -----------------------------------------------------

    if tipo == "professor":

        teacher = (
            db.query(Teacher)
            .filter(
                Teacher.user_id == current_user.id
            )
            .first()
        )

        if not teacher:
            raise HTTPException(
                status_code=404,
                detail="Perfil de professor não encontrado."
            )

        is_dt = (
            classroom.teacher_id == teacher.id
        )

        teaches_class = (
            db.query(Subject)
            .filter(
                Subject.teacher_id == teacher.id,
                Subject.classroom_id == classroom_id
            )
            .first()
        )

        if not teaches_class and not is_dt:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Este professor não possui "
                    "acesso a esta turma."
                )
            )

        # DT pode consultar todos os registros da turma.
        if is_dt:

            return (
                db.query(Attendance)
                .filter(
                    Attendance.classroom_id == classroom_id
                )
                .order_by(
                    Attendance.data.desc()
                )
                .all()
            )

        # Professor comum vê somente registros feitos por ele.
        return (
            db.query(Attendance)
            .filter(
                Attendance.classroom_id == classroom_id,
                Attendance.teacher_id == teacher.id
            )
            .order_by(
                Attendance.data.desc()
            )
            .all()
        )

    raise HTTPException(
        status_code=403,
        detail="Usuário sem permissão para consultar esta turma."
    )


# =========================================================
# PROFESSOR / ADMINISTRAÇÃO
# RESUMO DA FREQUÊNCIA DA TURMA
#
# PROFESSOR COMUM:
# resumo da própria atuação.
#
# DT:
# resumo completo da turma.
# =========================================================

@router.get(
    "/classroom/{classroom_id}/summary"
)
def classroom_attendance_summary(
    classroom_id: int,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):

    finalizar_faltas_pendentes(db)

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()

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

    # -----------------------------------------------------
    # PROFESSOR
    # -----------------------------------------------------

    if tipo == "professor":

        teacher = (
            db.query(Teacher)
            .filter(
                Teacher.user_id == current_user.id
            )
            .first()
        )

        if not teacher:
            raise HTTPException(
                status_code=404,
                detail="Perfil de professor não encontrado."
            )

        is_dt = (
            classroom.teacher_id == teacher.id
        )

        teaches_class = (
            db.query(Subject)
            .filter(
                Subject.teacher_id == teacher.id,
                Subject.classroom_id == classroom_id
            )
            .first()
        )

        if not teaches_class and not is_dt:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Este professor não possui "
                    "acesso a esta turma."
                )
            )

        if is_dt:

            registros = (
                db.query(Attendance)
                .filter(
                    Attendance.classroom_id == classroom_id
                )
                .all()
            )

        else:

            registros = (
                db.query(Attendance)
                .filter(
                    Attendance.classroom_id == classroom_id,
                    Attendance.teacher_id == teacher.id
                )
                .all()
            )

    # -----------------------------------------------------
    # ADMINISTRAÇÃO
    # -----------------------------------------------------

    elif tipo in [
        "administracao",
        "administração"
    ]:

        registros = (
            db.query(Attendance)
            .filter(
                Attendance.classroom_id == classroom_id
            )
            .all()
        )

    else:

        raise HTTPException(
            status_code=403,
            detail="Usuário sem permissão."
        )

    total = len(registros)

    presentes = sum(
        1
        for item in registros
        if item.status == "presente"
    )

    justificadas = sum(
        1
        for item in registros
        if item.status == "falta_justificada"
    )

    nao_justificadas = sum(
        1
        for item in registros
        if item.status == "falta_nao_justificada"
    )

    pendentes = sum(
        1
        for item in registros
        if item.status == "falta_pendente"
    )

    percentual = (
        round(
            (presentes / total) * 100,
            2
        )
        if total > 0
        else 0
    )

    return {
        "classroom_id": classroom_id,
        "registros": total,
        "presencas": presentes,
        "faltas_justificadas": justificadas,
        "faltas_nao_justificadas": nao_justificadas,
        "faltas_pendentes": pendentes,
        "percentual_presenca": percentual
    }


# =========================================================
# ALUNO / PROFESSOR
# JUSTIFICAR FALTA
#
# DT NÃO PODE ALTERAR REGISTRO DE OUTRO PROFESSOR.
# =========================================================

@router.patch(
    "/{attendance_id}/justify",
    response_model=AttendanceResponse
)
def justify_attendance(
    attendance_id: int,
    justification: AttendanceJustification,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    finalizar_faltas_pendentes(db)

    attendance = (
        db.query(Attendance)
        .filter(
            Attendance.id == attendance_id
        )
        .first()
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Registro de frequência não encontrado."
        )

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()

    # -----------------------------------------------------
    # ALUNO
    # -----------------------------------------------------

    if tipo == "aluno":

        if attendance.student_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Esta falta não pertence ao aluno."
            )

    # -----------------------------------------------------
    # PROFESSOR
    # -----------------------------------------------------

    elif tipo == "professor":

        teacher = (
            db.query(Teacher)
            .filter(
                Teacher.user_id == current_user.id
            )
            .first()
        )

        if (
            not teacher
            or attendance.teacher_id != teacher.id
        ):
            raise HTTPException(
                status_code=403,
                detail=(
                    "Este registro não pertence "
                    "ao professor."
                )
            )

    else:

        raise HTTPException(
            status_code=403,
            detail=(
                "Usuário sem permissão para "
                "justificar esta falta."
            )
        )

    # -----------------------------------------------------
    # PRECISA ESTAR PENDENTE
    # -----------------------------------------------------

    if attendance.status != "falta_pendente":
        raise HTTPException(
            status_code=400,
            detail=(
                "Esta falta não está pendente "
                "de justificativa."
            )
        )

    # -----------------------------------------------------
    # CONFERE PRAZO DE 24 HORAS
    # -----------------------------------------------------

    limite = (
        attendance.data
        + timedelta(hours=24)
    )

    if datetime.now() > limite:

        attendance.status = "falta_nao_justificada"
        attendance.justificada = False

        db.commit()

        raise HTTPException(
            status_code=400,
            detail=(
                "O prazo de 24 horas para "
                "justificativa terminou."
            )
        )

    # -----------------------------------------------------
    # REGISTRA JUSTIFICATIVA
    # -----------------------------------------------------

    attendance.status = "falta_justificada"
    attendance.justificada = True

    attendance.motivo = justification.motivo
    attendance.arquivo = justification.arquivo

    if justification.observacao:
        attendance.observacao = (
            justification.observacao
        )

    db.commit()
    db.refresh(attendance)

    return attendance


# =========================================================
# CONSULTAR UM REGISTRO ESPECÍFICO
#
# ALUNO:
# somente o próprio registro.
#
# PROFESSOR COMUM:
# somente registro feito por ele.
#
# DT:
# qualquer registro da turma da qual é DT.
#
# ADMINISTRAÇÃO:
# acesso institucional.
# =========================================================

@router.get(
    "/{attendance_id}",
    response_model=AttendanceResponse
)
def attendance_by_id(
    attendance_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    finalizar_faltas_pendentes(db)

    attendance = (
        db.query(Attendance)
        .filter(
            Attendance.id == attendance_id
        )
        .first()
    )

    if not attendance:
        raise HTTPException(
            status_code=404,
            detail="Registro de frequência não encontrado."
        )

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()

    # -----------------------------------------------------
    # ALUNO
    # -----------------------------------------------------

    if tipo == "aluno":

        if attendance.student_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail=(
                    "O aluno não possui acesso "
                    "a este registro."
                )
            )

        return attendance

    # -----------------------------------------------------
    # PROFESSOR
    # -----------------------------------------------------

    if tipo == "professor":

        teacher = (
            db.query(Teacher)
            .filter(
                Teacher.user_id == current_user.id
            )
            .first()
        )

        if not teacher:
            raise HTTPException(
                status_code=404,
                detail="Perfil de professor não encontrado."
            )

        classroom = (
            db.query(Classroom)
            .filter(
                Classroom.id == attendance.classroom_id
            )
            .first()
        )

        is_owner = (
            attendance.teacher_id == teacher.id
        )

        is_dt = (
            classroom is not None
            and classroom.teacher_id == teacher.id
        )

        if not is_owner and not is_dt:
            raise HTTPException(
                status_code=403,
                detail="Professor sem acesso a este registro."
            )

        return attendance

    # -----------------------------------------------------
    # ADMINISTRAÇÃO
    # -----------------------------------------------------

    if tipo in [
        "administracao",
        "administração"
    ]:
        return attendance

    raise HTTPException(
        status_code=403,
        detail=(
            "Usuário sem permissão para "
            "acessar este registro."
        )
    )