import unicodedata

from datetime import time

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.models import (
    User,
    Teacher,
    Classroom,
    Subject,
    Enrollment,
    ClassSchedule
)


# =========================================================
# NORMALIZAR TEXTO
# =========================================================

def normalize_text(
    value: str
):

    value = (
        value
        or ""
    ).strip().lower()

    value = unicodedata.normalize(
        "NFKD",
        value
    )

    return "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )


# =========================================================
# DIA DA SEMANA
# =========================================================

def normalize_weekday(
    value: str
):

    value = normalize_text(
        value
    )

    value = (
        value
        .replace("-", " ")
    )

    value = " ".join(
        value.split()
    )


    mapping = {

        "segunda":
            "Segunda-feira",

        "segunda feira":
            "Segunda-feira",

        "terca":
            "Terça-feira",

        "terca feira":
            "Terça-feira",

        "quarta":
            "Quarta-feira",

        "quarta feira":
            "Quarta-feira",

        "quinta":
            "Quinta-feira",

        "quinta feira":
            "Quinta-feira",

        "sexta":
            "Sexta-feira",

        "sexta feira":
            "Sexta-feira",

        "sabado":
            "Sábado",

        "domingo":
            "Domingo"
    }


    if value not in mapping:

        raise HTTPException(
            status_code=400,
            detail=(
                "Dia da semana inválido."
            )
        )


    return mapping[value]


# =========================================================
# VALIDAR HORARIO
# =========================================================

def validate_time_range(

    hora_inicio: time,

    hora_fim: time

):

    if hora_inicio >= hora_fim:

        raise HTTPException(
            status_code=400,
            detail=(
                "A hora final deve ser "
                "posterior à hora inicial."
            )
        )


# =========================================================
# DISCIPLINA
# =========================================================

def get_active_subject(

    db: Session,

    subject_id: int

):

    subject = (
        db.query(Subject)
        .filter(
            Subject.id
            == subject_id,

            Subject.ativa
            == True
        )
        .first()
    )


    if not subject:

        raise HTTPException(
            status_code=404,
            detail=(
                "Disciplina não encontrada "
                "ou inativa."
            )
        )


    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id
            == subject.classroom_id
        )
        .first()
    )


    if not classroom:

        raise HTTPException(
            status_code=404,
            detail="Turma não encontrada."
        )


    if not classroom.ativa:

        raise HTTPException(
            status_code=400,
            detail=(
                "Não é possível criar horário "
                "para uma turma inativa."
            )
        )


    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.id
            == subject.teacher_id
        )
        .first()
    )


    if not teacher:

        raise HTTPException(
            status_code=404,
            detail=(
                "Professor responsável "
                "não encontrado."
            )
        )


    if not teacher.ativo:

        raise HTTPException(
            status_code=400,
            detail=(
                "O professor responsável "
                "está inativo."
            )
        )


    return subject


# =========================================================
# CONFLITOS
#
# Impede:
#
# 1. duas aulas na mesma turma ao mesmo tempo;
# 2. professor em duas turmas ao mesmo tempo.
# =========================================================

def validate_conflicts(

    db: Session,

    subject: Subject,

    dia_semana: str,

    hora_inicio: time,

    hora_fim: time,

    ignore_schedule_id: int | None = None

):

    # -----------------------------------------------------
    # CONFLITO DA TURMA
    # -----------------------------------------------------

    classroom_conflict_query = (

        db.query(ClassSchedule)

        .join(
            Subject,
            ClassSchedule.subject_id
            == Subject.id
        )

        .filter(

            ClassSchedule.ativo
            == True,

            Subject.classroom_id
            == subject.classroom_id,

            ClassSchedule.dia_semana
            == dia_semana,

            ClassSchedule.hora_inicio
            < hora_fim,

            ClassSchedule.hora_fim
            > hora_inicio
        )
    )


    if ignore_schedule_id is not None:

        classroom_conflict_query = (
            classroom_conflict_query
            .filter(
                ClassSchedule.id
                != ignore_schedule_id
            )
        )


    classroom_conflict = (
        classroom_conflict_query
        .first()
    )


    if classroom_conflict:

        raise HTTPException(
            status_code=400,
            detail=(
                "Já existe outra aula desta turma "
                "nesse intervalo de horário."
            )
        )


    # -----------------------------------------------------
    # CONFLITO DO PROFESSOR
    # -----------------------------------------------------

    teacher_conflict_query = (

        db.query(ClassSchedule)

        .join(
            Subject,
            ClassSchedule.subject_id
            == Subject.id
        )

        .filter(

            ClassSchedule.ativo
            == True,

            Subject.teacher_id
            == subject.teacher_id,

            ClassSchedule.dia_semana
            == dia_semana,

            ClassSchedule.hora_inicio
            < hora_fim,

            ClassSchedule.hora_fim
            > hora_inicio
        )
    )


    if ignore_schedule_id is not None:

        teacher_conflict_query = (
            teacher_conflict_query
            .filter(
                ClassSchedule.id
                != ignore_schedule_id
            )
        )


    teacher_conflict = (
        teacher_conflict_query
        .first()
    )


    if teacher_conflict:

        raise HTTPException(
            status_code=400,
            detail=(
                "O professor já possui outra aula "
                "nesse intervalo de horário."
            )
        )


# =========================================================
# CONVERTER PARA RESPOSTA
# =========================================================

def schedule_to_response(

    db: Session,

    schedule: ClassSchedule

):

    subject = (
        db.query(Subject)
        .filter(
            Subject.id
            == schedule.subject_id
        )
        .first()
    )


    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id
            == subject.classroom_id
        )
        .first()
    )


    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.id
            == subject.teacher_id
        )
        .first()
    )


    turma_nome = (
        getattr(
            classroom,
            "nome",
            None
        )
        or getattr(
            classroom,
            "turma",
            None
        )
        or str(
            classroom.id
        )
    )


    return {

        "id":
            schedule.id,

        "subject_id":
            subject.id,

        "disciplina":
            subject.nome,

        "classroom_id":
            classroom.id,

        "turma":
            turma_nome,

        "teacher_id":
            teacher.id,

        "professor":
            teacher.nome,

        "dia_semana":
            schedule.dia_semana,

        "hora_inicio":
            schedule.hora_inicio,

        "hora_fim":
            schedule.hora_fim,

        "ativo":
            schedule.ativo
    }


# =========================================================
# CRIAR HORARIO
# ADMINISTRACAO
# =========================================================

def create_schedule(

    db: Session,

    data

):

    subject = get_active_subject(
        db,
        data.subject_id
    )


    dia_semana = normalize_weekday(
        data.dia_semana
    )


    validate_time_range(
        data.hora_inicio,
        data.hora_fim
    )


    validate_conflicts(

        db=db,

        subject=subject,

        dia_semana=dia_semana,

        hora_inicio=data.hora_inicio,

        hora_fim=data.hora_fim
    )


    schedule = ClassSchedule(

        subject_id=subject.id,

        dia_semana=dia_semana,

        hora_inicio=data.hora_inicio,

        hora_fim=data.hora_fim,

        ativo=True
    )


    db.add(
        schedule
    )

    db.commit()

    db.refresh(
        schedule
    )


    return schedule_to_response(
        db,
        schedule
    )


# =========================================================
# LISTAR TODOS
# ADMINISTRACAO
# =========================================================

def get_all_schedules(
    db: Session
):

    schedules = (

        db.query(ClassSchedule)

        .filter(
            ClassSchedule.ativo
            == True
        )

        .all()
    )


    return [

        schedule_to_response(
            db,
            schedule
        )

        for schedule in schedules
    ]


# =========================================================
# HORARIOS DE UMA TURMA
# =========================================================

def get_classroom_schedules(

    db: Session,

    classroom_id: int

):

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id
            == classroom_id
        )
        .first()
    )


    if not classroom:

        raise HTTPException(
            status_code=404,
            detail="Turma não encontrada."
        )


    schedules = (

        db.query(ClassSchedule)

        .join(
            Subject,
            ClassSchedule.subject_id
            == Subject.id
        )

        .filter(

            ClassSchedule.ativo
            == True,

            Subject.ativa
            == True,

            Subject.classroom_id
            == classroom_id
        )

        .all()
    )


    return [

        schedule_to_response(
            db,
            schedule
        )

        for schedule in schedules
    ]


# =========================================================
# MEUS HORARIOS
#
# ALUNO:
# horario da turma ativa.
#
# PROFESSOR:
# horarios das disciplinas dele.
#
# ADMINISTRACAO:
# todos.
#
# SUPORTE:
# sem acesso pedagogico.
# =========================================================

def get_my_schedules(

    db: Session,

    current_user: User

):

    tipo = normalize_text(
        current_user.tipo
    )


    # -----------------------------------------------------
    # ALUNO
    # -----------------------------------------------------

    if tipo == "aluno":

        enrollment = (

            db.query(Enrollment)

            .filter(

                Enrollment.user_id
                == current_user.id,

                Enrollment.ativo
                == True
            )

            .first()
        )


        if not enrollment:

            return []


        return get_classroom_schedules(
            db,
            enrollment.classroom_id
        )


    # -----------------------------------------------------
    # PROFESSOR
    # -----------------------------------------------------

    if tipo == "professor":

        teacher = (

            db.query(Teacher)

            .filter(
                Teacher.user_id
                == current_user.id
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


        schedules = (

            db.query(ClassSchedule)

            .join(
                Subject,
                ClassSchedule.subject_id
                == Subject.id
            )

            .filter(

                ClassSchedule.ativo
                == True,

                Subject.ativa
                == True,

                Subject.teacher_id
                == teacher.id
            )

            .all()
        )


        return [

            schedule_to_response(
                db,
                schedule
            )

            for schedule in schedules
        ]


    # -----------------------------------------------------
    # ADMINISTRACAO
    # -----------------------------------------------------

    if tipo in [
        "administracao",
        "administracao"
    ]:

        return get_all_schedules(
            db
        )


    # -----------------------------------------------------
    # SUPORTE OU OUTRO PERFIL
    # -----------------------------------------------------

    raise HTTPException(
        status_code=403,
        detail=(
            "Usuário sem acesso "
            "aos horários acadêmicos."
        )
    )


# =========================================================
# ATUALIZAR HORARIO
# ADMINISTRACAO
# =========================================================

def update_schedule(

    db: Session,

    schedule_id: int,

    data

):

    schedule = (

        db.query(ClassSchedule)

        .filter(
            ClassSchedule.id
            == schedule_id,

            ClassSchedule.ativo
            == True
        )

        .first()
    )


    if not schedule:

        raise HTTPException(
            status_code=404,
            detail="Horário não encontrado."
        )


    subject_id = (
        data.subject_id
        if data.subject_id is not None
        else schedule.subject_id
    )


    subject = get_active_subject(
        db,
        subject_id
    )


    dia_semana = (

        normalize_weekday(
            data.dia_semana
        )

        if data.dia_semana
        is not None

        else schedule.dia_semana
    )


    hora_inicio = (

        data.hora_inicio

        if data.hora_inicio
        is not None

        else schedule.hora_inicio
    )


    hora_fim = (

        data.hora_fim

        if data.hora_fim
        is not None

        else schedule.hora_fim
    )


    validate_time_range(
        hora_inicio,
        hora_fim
    )


    validate_conflicts(

        db=db,

        subject=subject,

        dia_semana=dia_semana,

        hora_inicio=hora_inicio,

        hora_fim=hora_fim,

        ignore_schedule_id=(
            schedule.id
        )
    )


    schedule.subject_id = (
        subject.id
    )

    schedule.dia_semana = (
        dia_semana
    )

    schedule.hora_inicio = (
        hora_inicio
    )

    schedule.hora_fim = (
        hora_fim
    )


    db.commit()

    db.refresh(
        schedule
    )


    return schedule_to_response(
        db,
        schedule
    )


# =========================================================
# DESATIVAR HORARIO
# =========================================================

def deactivate_schedule(

    db: Session,

    schedule_id: int

):

    schedule = (

        db.query(ClassSchedule)

        .filter(
            ClassSchedule.id
            == schedule_id,

            ClassSchedule.ativo
            == True
        )

        .first()
    )


    if not schedule:

        raise HTTPException(
            status_code=404,
            detail="Horário não encontrado."
        )


    schedule.ativo = False


    db.commit()


    return {
        "message":
            "Horário desativado com sucesso."
    }