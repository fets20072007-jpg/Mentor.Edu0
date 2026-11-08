from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    User,
    Grade,
    Assessment,
    Teacher,
    Subject,
    Enrollment,
    Classroom
)

from app.schema.grade import (
    GradeCreate,
    GradeUpdate,
    GradeResponse
)

from app.services.academic.grade_service import (
    create_grade,
    get_all_grades,
    get_grade_by_id,
    get_student_grades,
    get_assessment_grades,
    update_grade
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_student,
    require_teacher,
    require_admin
)


router = APIRouter(
    prefix="/grades",
    tags=["Grades"]
)


# =========================================================
# AUXILIAR
# LOCALIZAR PERFIL DO PROFESSOR
# =========================================================

def get_teacher_profile(
    db: Session,
    current_user: User
):

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

    return teacher


# =========================================================
# AUXILIAR
# VALIDAR AVALIAÇÃO DO PROFESSOR
#
# Usada em ações de propriedade:
# lançar nota, editar nota e consultar notas
# da própria avaliação.
# =========================================================

def validate_teacher_assessment(
    db: Session,
    assessment_id: int,
    teacher: Teacher
):

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id,
            Assessment.teacher_id == teacher.id
        )
        .first()
    )

    if not assessment:

        raise HTTPException(
            status_code=404,
            detail=(
                "Avaliação não encontrada ou "
                "não pertence ao professor autenticado."
            )
        )

    subject = (
        db.query(Subject)
        .filter(
            Subject.id == assessment.subject_id
        )
        .first()
    )

    if not subject:

        raise HTTPException(
            status_code=404,
            detail=(
                "Disciplina da avaliação "
                "não encontrada."
            )
        )

    return assessment, subject


# =========================================================
# PROFESSOR
# LANÇAR NOTA
# =========================================================

@router.post(
    "",
    response_model=GradeResponse
)
def register_grade(

    grade: GradeCreate,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(
        get_db
    )

):

    teacher = get_teacher_profile(
        db,
        current_user
    )

    assessment, subject = (
        validate_teacher_assessment(
            db,
            grade.assessment_id,
            teacher
        )
    )

    # -----------------------------------------------------
    # CONFIRMA ALUNO
    # -----------------------------------------------------

    student = (
        db.query(User)
        .filter(
            User.id
            == grade.student_id
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
                "O usuário informado "
                "não é um aluno."
            )
        )

    # -----------------------------------------------------
    # CONFIRMA MATRÍCULA ATIVA NA TURMA DA AVALIAÇÃO
    # -----------------------------------------------------

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id
            == student.id,

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
                "Este aluno não possui "
                "matrícula ativa na turma "
                "desta avaliação."
            )
        )

    # -----------------------------------------------------
    # IMPEDE NOTA DUPLICADA
    # -----------------------------------------------------

    existing_grade = (
        db.query(Grade)
        .filter(
            Grade.assessment_id
            == grade.assessment_id,

            Grade.student_id
            == grade.student_id
        )
        .first()
    )

    if existing_grade:

        raise HTTPException(
            status_code=400,
            detail=(
                "Este aluno já possui uma "
                "nota registrada para esta "
                "avaliação."
            )
        )

    return create_grade(
        db,
        grade
    )


# =========================================================
# ALUNO
# MINHAS NOTAS
# =========================================================

@router.get(
    "/me",
    response_model=list[GradeResponse]
)
def my_grades(

    current_user: User = Depends(
        require_student
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_student_grades(
        db,
        current_user.id
    )


# =========================================================
# PROFESSOR
# NOTAS DE UMA AVALIAÇÃO
#
# Apenas o professor responsável pela avaliação.
# DT não ganha direito de alterar ou controlar
# avaliações de outros professores.
# =========================================================

@router.get(
    "/assessment/{assessment_id}",
    response_model=list[GradeResponse]
)
def assessment_grades(

    assessment_id: int,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(
        get_db
    )

):

    teacher = get_teacher_profile(
        db,
        current_user
    )

    validate_teacher_assessment(
        db,
        assessment_id,
        teacher
    )

    return get_assessment_grades(
        db,
        assessment_id
    )


# =========================================================
# ADMINISTRAÇÃO
# CONSULTAR TODAS AS NOTAS
# =========================================================

@router.get(
    "/",
    response_model=list[GradeResponse]
)
def list_grades(

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_all_grades(
        db
    )


# =========================================================
# PROFESSOR
# ALTERAR NOTA
#
# Somente o professor dono da avaliação.
# =========================================================

@router.patch(
    "/{grade_id}",
    response_model=GradeResponse
)
def edit_grade(

    grade_id: int,

    grade_update: GradeUpdate,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(
        get_db
    )

):

    grade = get_grade_by_id(
        db,
        grade_id
    )

    if not grade:

        raise HTTPException(
            status_code=404,
            detail="Nota não encontrada."
        )

    teacher = get_teacher_profile(
        db,
        current_user
    )

    validate_teacher_assessment(
        db,
        grade.assessment_id,
        teacher
    )

    return update_grade(
        db,
        grade,
        grade_update
    )


# =========================================================
# CONSULTAR UMA NOTA
#
# ALUNO:
# somente a própria nota.
#
# PROFESSOR COMUM:
# nota de avaliação própria.
#
# DT:
# também pode consultar nota individual de aluno
# da turma pela qual é Diretor de Turma.
#
# ADMINISTRAÇÃO:
# leitura institucional.
#
# SUPORTE:
# bloqueado.
# =========================================================

@router.get(
    "/{grade_id}",
    response_model=GradeResponse
)
def grade_by_id(

    grade_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    grade = get_grade_by_id(
        db,
        grade_id
    )

    if not grade:

        raise HTTPException(
            status_code=404,
            detail="Nota não encontrada."
        )

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()

    # -----------------------------------------------------
    # ALUNO
    # -----------------------------------------------------

    if tipo == "aluno":

        if (
            grade.student_id
            != current_user.id
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "O aluno não possui "
                    "acesso a esta nota."
                )
            )

        return grade

    # -----------------------------------------------------
    # PROFESSOR / DT
    # -----------------------------------------------------

    if tipo == "professor":

        teacher = get_teacher_profile(
            db,
            current_user
        )

        assessment = (
            db.query(Assessment)
            .filter(
                Assessment.id
                == grade.assessment_id
            )
            .first()
        )

        if not assessment:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Avaliação da nota "
                    "não encontrada."
                )
            )

        # Professor responsável pela avaliação
        is_owner = (
            assessment.teacher_id
            == teacher.id
        )

        # Verifica se o professor é DT da turma
        classroom = (
            db.query(Classroom)
            .filter(
                Classroom.id
                == assessment.classroom_id
            )
            .first()
        )

        is_dt = (
            classroom is not None
            and classroom.teacher_id
            == teacher.id
        )

        if not is_owner and not is_dt:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Professor sem acesso "
                    "a esta nota."
                )
            )

        return grade

    # -----------------------------------------------------
    # ADMINISTRAÇÃO
    # -----------------------------------------------------

    if tipo in [
        "administracao",
        "administração"
    ]:

        return grade

    # -----------------------------------------------------
    # SUPORTE / OUTROS
    # -----------------------------------------------------

    raise HTTPException(
        status_code=403,
        detail=(
            "Usuário sem permissão "
            "para acessar esta nota."
        )
    )