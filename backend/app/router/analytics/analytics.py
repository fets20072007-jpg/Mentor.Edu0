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

from app.security.auth import get_current_user

from app.services.analytics.grade_analytics_service import (
    calculate_student_average
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/average")
def student_average(
    student_id: int,
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # =====================================================
    # CONFIRMA ALUNO
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
    # CONFIRMA DISCIPLINA
    # =====================================================

    disciplina = (
        db.query(Subject)
        .filter(
            Subject.id == subject_id
        )
        .first()
    )

    if not disciplina:
        raise HTTPException(
            status_code=404,
            detail="Disciplina não encontrada."
        )


    # =====================================================
    # MATRÍCULA ATIVA
    # =====================================================

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
            status_code=404,
            detail="Aluno sem matrícula ativa."
        )


    # =====================================================
    # DISCIPLINA PRECISA SER DA TURMA DO ALUNO
    # =====================================================

    if disciplina.classroom_id != matricula.classroom_id:
        raise HTTPException(
            status_code=403,
            detail=(
                "A disciplina informada não pertence "
                "à turma deste aluno."
            )
        )


    # =====================================================
    # TIPO DO USUÁRIO LOGADO
    # =====================================================

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()


    # =====================================================
    # SUPORTE
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
    # =====================================================

    if tipo == "aluno":

        if current_user.id != student_id:
            raise HTTPException(
                status_code=403,
                detail=(
                    "O aluno não possui acesso "
                    "ao desempenho de outro aluno."
                )
            )


    # =====================================================
    # PROFESSOR
    # =====================================================

    elif tipo == "professor":

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


        # -------------------------------------------------
        # TURMA DO ALUNO
        # -------------------------------------------------

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


        # -------------------------------------------------
        # DIRETOR DE TURMA
        # -------------------------------------------------

        is_dt = (
            turma.teacher_id == teacher.id
        )

        if not is_dt:

            # Professor comum só pode consultar
            # a própria disciplina.

            if disciplina.teacher_id != teacher.id:
                raise HTTPException(
                    status_code=403,
                    detail=(
                        "Este professor não possui acesso "
                        "ao desempenho desta disciplina."
                    )
                )


    # =====================================================
    # ADMINISTRAÇÃO
    # =====================================================

    elif tipo in [
        "administracao",
        "administração"
    ]:

        pass


    # =====================================================
    # OUTROS PERFIS
    # =====================================================

    else:
        raise HTTPException(
            status_code=403,
            detail=(
                "Usuário sem permissão para "
                "consultar dados de desempenho."
            )
        )


    # =====================================================
    # CALCULA MÉDIA
    # =====================================================

    media = calculate_student_average(
        db,
        student_id,
        subject_id
    )

    return {
        "student_id": student_id,
        "subject_id": subject_id,
        "average": media
    }