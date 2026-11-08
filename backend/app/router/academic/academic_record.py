from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    User,
    Teacher,
    Subject,
    Enrollment,
    Classroom
)

from app.schema.academic_record import (
    AcademicRecordResponse
)

from app.services.academic.academic_record_service import (
    generate_academic_record
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_student
)


router = APIRouter(
    prefix="/academic-record",
    tags=["Academic Record"]
)


# =========================================================
# ALUNO
# MEU PRÓPRIO HISTÓRICO ACADÊMICO
# =========================================================

@router.get(
    "/me",
    response_model=AcademicRecordResponse
)
def my_academic_record(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):

    boletim = generate_academic_record(
        db,
        current_user.id
    )

    if boletim is None:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado."
        )

    return boletim


# =========================================================
# CONSULTAR HISTÓRICO ACADÊMICO
# =========================================================

@router.get(
    "/{student_id}",
    response_model=AcademicRecordResponse
)
def get_academic_record(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # =====================================================
    # CONFIRMA SE O USUÁRIO INFORMADO É ALUNO
    # =====================================================

    aluno = (
        db.query(User)
        .filter(
            User.id == student_id
        )
        .first()
    )

    if not aluno:
        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado."
        )

    tipo_aluno = (
        aluno.tipo
        or ""
    ).strip().lower()

    if tipo_aluno != "aluno":
        raise HTTPException(
            status_code=400,
            detail="O usuário informado não é um aluno."
        )


    # =====================================================
    # TIPO DO USUÁRIO AUTENTICADO
    # =====================================================

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()


    # =====================================================
    # SUPORTE
    # NUNCA ACESSA DADOS PEDAGÓGICOS
    # =====================================================

    if tipo == "suporte":

        raise HTTPException(
            status_code=403,
            detail=(
                "O Suporte não possui acesso "
                "a dados pedagógicos dos alunos."
            )
        )


    # =====================================================
    # ALUNO
    # SÓ PODE CONSULTAR O PRÓPRIO HISTÓRICO
    # =====================================================

    if tipo == "aluno":

        if current_user.id != student_id:
            raise HTTPException(
                status_code=403,
                detail=(
                    "O aluno não possui acesso "
                    "ao histórico acadêmico "
                    "de outro aluno."
                )
            )

        boletim = generate_academic_record(
            db,
            student_id
        )

        if boletim is None:
            raise HTTPException(
                status_code=404,
                detail="Histórico acadêmico não encontrado."
            )

        return boletim


    # =====================================================
    # PROFESSOR
    # =====================================================

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


        # =================================================
        # MATRÍCULA ATIVA DO ALUNO
        # =================================================

        matricula = (
            db.query(Enrollment)
            .filter(
                Enrollment.user_id == student_id,
                Enrollment.ativo == True
            )
            .first()
        )

        if not matricula:
            raise HTTPException(
                status_code=403,
                detail=(
                    "O aluno não possui "
                    "matrícula ativa."
                )
            )


        # =================================================
        # TURMA DO ALUNO
        # =================================================

        turma = (
            db.query(Classroom)
            .filter(
                Classroom.id == matricula.classroom_id
            )
            .first()
        )

        if not turma:
            raise HTTPException(
                status_code=404,
                detail="Turma não encontrada."
            )


        # =================================================
        # DIRETOR DE TURMA - DT
        # =================================================

        is_dt = (
            turma.teacher_id == teacher.id
        )

        if is_dt:

            # O DT pode consultar todas as disciplinas
            # somente dos alunos da turma pela qual
            # ele é responsável.

            boletim = generate_academic_record(
                db,
                student_id
            )

            if boletim is None:
                raise HTTPException(
                    status_code=404,
                    detail="Histórico acadêmico não encontrado."
                )

            return boletim


        # =================================================
        # PROFESSOR COMUM
        # SOMENTE AS PRÓPRIAS DISCIPLINAS
        # =================================================

        disciplinas_professor = (
            db.query(Subject)
            .filter(
                Subject.teacher_id == teacher.id,
                Subject.classroom_id == matricula.classroom_id
            )
            .all()
        )

        if not disciplinas_professor:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Este professor não leciona "
                    "para este aluno."
                )
            )

        subject_ids = [
            disciplina.id
            for disciplina in disciplinas_professor
        ]

        boletim = generate_academic_record(
            db,
            student_id,
            allowed_subject_ids=subject_ids
        )

        if boletim is None:
            raise HTTPException(
                status_code=404,
                detail="Histórico acadêmico não encontrado."
            )

        return boletim


    # =====================================================
    # ADMINISTRAÇÃO
    # ACESSO PEDAGÓGICO COMPLETO
    # =====================================================

    if tipo in [
        "administracao",
        "administração"
    ]:

        boletim = generate_academic_record(
            db,
            student_id
        )

        if boletim is None:
            raise HTTPException(
                status_code=404,
                detail="Histórico acadêmico não encontrado."
            )

        return boletim


    # =====================================================
    # QUALQUER OUTRO PERFIL
    # =====================================================

    raise HTTPException(
        status_code=403,
        detail=(
            "Usuário sem permissão para "
            "consultar histórico acadêmico."
        )
    )