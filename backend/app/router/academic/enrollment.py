from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import (
    User,
    Enrollment,
    Classroom,
    Teacher,
    Subject
)

from app.schema.enrollment import (
    EnrollmentCreate,
    EnrollmentTransfer,
    EnrollmentResponse
)

from app.core.permissions import (
    require_admin,
    require_student,
    require_teacher_or_admin
)


router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)


# =========================================================
# ADMINISTRAÇÃO
# CRIAR MATRÍCULA
# =========================================================

@router.post(
    "",
    response_model=EnrollmentResponse
)
def register_enrollment(
    enrollment: EnrollmentCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # VERIFICA ALUNO
    # -----------------------------------------------------

    student = (
        db.query(User)
        .filter(
            User.id == enrollment.user_id
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
            detail="A matrícula só pode ser vinculada a um aluno."
        )

    # -----------------------------------------------------
    # VERIFICA TURMA
    # -----------------------------------------------------

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id == enrollment.classroom_id
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
                "Não é possível matricular "
                "o aluno em uma turma inativa."
            )
        )

    # -----------------------------------------------------
    # IMPEDE MAIS DE UMA MATRÍCULA ATIVA
    # -----------------------------------------------------

    active_enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == student.id,
            Enrollment.ativo == True
        )
        .first()
    )

    if active_enrollment:
        raise HTTPException(
            status_code=400,
            detail="Este aluno já possui uma matrícula ativa."
        )

    # -----------------------------------------------------
    # CRIA MATRÍCULA
    # -----------------------------------------------------

    new_enrollment = Enrollment(
        user_id=student.id,
        classroom_id=classroom.id,
        data_matricula=datetime.now(),
        ativo=True
    )

    db.add(new_enrollment)

    # Mantém User e Enrollment sincronizados.
    student.classroom_id = classroom.id

    db.commit()
    db.refresh(new_enrollment)

    return new_enrollment


# =========================================================
# ADMINISTRAÇÃO
# LISTAR TODAS AS MATRÍCULAS
# =========================================================

@router.get(
    "",
    response_model=list[EnrollmentResponse]
)
def list_enrollments(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):

    return (
        db.query(Enrollment)
        .order_by(
            Enrollment.id.desc()
        )
        .all()
    )


# =========================================================
# ALUNO
# MINHAS MATRÍCULAS
# =========================================================

@router.get(
    "/me",
    response_model=list[EnrollmentResponse]
)
def my_enrollments(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):

    return (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == current_user.id
        )
        .order_by(
            Enrollment.id.desc()
        )
        .all()
    )


# =========================================================
# PROFESSOR / ADMINISTRAÇÃO
# ALUNOS DE UMA TURMA
# =========================================================

@router.get(
    "/classroom/{classroom_id}",
    response_model=list[EnrollmentResponse]
)
def classroom_enrollments(
    classroom_id: int,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()

    # -----------------------------------------------------
    # VERIFICA TURMA
    # -----------------------------------------------------

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
            db.query(Enrollment)
            .filter(
                Enrollment.classroom_id == classroom_id,
                Enrollment.ativo == True
            )
            .all()
        )

    # -----------------------------------------------------
    # PROFESSOR
    # Professor comum: turma em que leciona.
    # DT: turma pela qual é responsável.
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

        teaches_class = (
            db.query(Subject)
            .filter(
                Subject.teacher_id == teacher.id,
                Subject.classroom_id == classroom_id
            )
            .first()
        )

        is_dt = (
            classroom.teacher_id == teacher.id
        )

        if not teaches_class and not is_dt:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Este professor não possui "
                    "acesso a esta turma."
                )
            )

        return (
            db.query(Enrollment)
            .filter(
                Enrollment.classroom_id == classroom_id,
                Enrollment.ativo == True
            )
            .all()
        )

    raise HTTPException(
        status_code=403,
        detail="Usuário sem permissão para consultar esta turma."
    )

# =========================================================
# ADMINISTRAÇÃO
# TRANSFERIR ALUNO DE TURMA
#
# A matrícula anterior permanece como histórico.
# Apenas deixa de ser ativa.
# =========================================================

@router.patch(
    "/student/{student_id}/classroom",
    response_model=EnrollmentResponse
)
def transfer_student_classroom(

    student_id: int,

    data: EnrollmentTransfer,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    # -----------------------------------------------------
    # ALUNO
    # -----------------------------------------------------

    student = (
        db.query(User)
        .filter(
            User.id == student_id
        )
        .first()
    )

    if not student:

        raise HTTPException(
            status_code=404,
            detail="Aluno não encontrado."
        )

    tipo = (
        student.tipo
        or ""
    ).strip().lower()

    if tipo != "aluno":

        raise HTTPException(
            status_code=400,
            detail=(
                "A transferência só pode "
                "ser realizada para alunos."
            )
        )


    # -----------------------------------------------------
    # NOVA TURMA
    # -----------------------------------------------------

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id
            == data.classroom_id
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
                "Não é possível matricular "
                "o aluno em uma turma inativa."
            )
        )


    # -----------------------------------------------------
    # MATRÍCULA ATUAL
    # -----------------------------------------------------

    active_enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id
            == student.id,

            Enrollment.ativo
            == True
        )
        .first()
    )


    # Já está nesta turma.
    if (
        active_enrollment
        and active_enrollment.classroom_id
        == classroom.id
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Este aluno já está "
                "matriculado nesta turma."
            )
        )


    # -----------------------------------------------------
    # DESATIVA A MATRÍCULA ANTERIOR
    # -----------------------------------------------------

    if active_enrollment:

        active_enrollment.ativo = False


    # -----------------------------------------------------
    # CRIA NOVA MATRÍCULA
    # -----------------------------------------------------

    new_enrollment = Enrollment(

        user_id=student.id,

        classroom_id=classroom.id,

        data_matricula=datetime.now(),

        ativo=True
    )

    db.add(
        new_enrollment
    )


    # -----------------------------------------------------
    # MANTÉM CAMPO LEGADO SINCRONIZADO
    # -----------------------------------------------------

    student.classroom_id = (
        classroom.id
    )


    # Tudo ocorre na mesma transação.
    db.commit()

    db.refresh(
        new_enrollment
    )

    return new_enrollment