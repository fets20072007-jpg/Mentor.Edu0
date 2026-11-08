from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database.dependencies import get_db
from app.database.models import User

from app.core.permissions import require_admin

from app.schema.admin_assessment import (
    AdminAssessmentResponse
)

from app.services.academic.admin_assessment_service import (
    get_admin_assessments,
    get_admin_assessment_by_id
)

from app.schema.admin_users import (
    AdminTeacherResponse,
    AdminStudentResponse
)

from app.schema.admin_classroom import (
    AdminClassroomResponse
)

from app.services.academic.admin_dashboard_service import (
    get_admin_teachers,
    get_admin_students,
    get_admin_classrooms
)


from app.services.academic.admin_dashboard_service import (
    get_admin_teachers,
    get_admin_students,
    get_admin_classrooms,
    get_admin_summary,
    get_admin_teacher_by_id,
    get_admin_student_by_id,
    get_admin_classroom_by_id,
    get_admin_teacher_summary,
    get_admin_classroom_summary, 
    get_admin_student_summary
)

from app.schema.admin_summary import (
    AdminSummaryResponse
)

from app.schema.admin_detail_summary import (
    AdminTeacherSummaryResponse,
    AdminClassroomSummaryResponse,
    AdminStudentSummaryResponse
)
router = APIRouter(
    prefix="/admin",
    tags=["Administration"]
)

@router.get(
    "/assessments",
    response_model=list[AdminAssessmentResponse]
)
def admin_assessments(
    titulo: str | None = None,
    teacher_id: int | None = None,
    classroom_id: int | None = None,
    subject_id: int | None = None,
    tipo: str | None = None,
    semestre: int | None = None,
    ano_letivo: int | None = None,
    ativa: bool | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    ordem: str = "mais_recentes",

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_assessments(
        db=db,
        titulo=titulo,
        teacher_id=teacher_id,
        classroom_id=classroom_id,
        subject_id=subject_id,
        tipo=tipo,
        semestre=semestre,
        ano_letivo=ano_letivo,
        ativa=ativa,
        data_inicio=data_inicio,
        data_fim=data_fim,
        ordem=ordem
    )

@router.get(
    "/assessments/{assessment_id}",
    response_model=AdminAssessmentResponse
)
def admin_assessment_details(
    assessment_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_assessment_by_id(
        db=db,
        assessment_id=assessment_id
    )

@router.get(
    "/teachers",
    response_model=list[AdminTeacherResponse]
)
def admin_teachers(
    nome: str | None = None,
    especialidade: str | None = None,
    ativo: bool | None = None,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_teachers(
        db=db,
        nome=nome,
        especialidade=especialidade,
        ativo=ativo
    )


@router.get(
    "/students",
    response_model=list[AdminStudentResponse]
)
def admin_students(
    nome: str | None = None,
    escola: str | None = None,
    serie: str | None = None,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_students(
        db=db,
        nome=nome,
        escola=escola,
        serie=serie
    )


@router.get(
    "/classrooms",
    response_model=list[AdminClassroomResponse]
)
def admin_classrooms(
    current_user: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db)
):
    return get_admin_classrooms(
        db=db
    )

@router.get(
    "/summary",
    response_model=AdminSummaryResponse
)
def admin_summary(
    current_user: User = Depends(
        require_admin
    ),
    db: Session = Depends(get_db)
):
    return get_admin_summary(
        db=db
    )

@router.get(
    "/teachers/{user_id}",
    response_model=AdminTeacherResponse
)
def admin_teacher_details(
    user_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_teacher_by_id(
        db=db,
        user_id=user_id
    )

@router.get(
    "/students/{user_id}",
    response_model=AdminStudentResponse
)
def admin_student_details(
    user_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_student_by_id(
        db=db,
        user_id=user_id
    )


@router.get(
    "/classrooms/{classroom_id}",
    response_model=AdminClassroomResponse
)
def admin_classroom_details(
    classroom_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_classroom_by_id(
        db=db,
        classroom_id=classroom_id
    )

@router.get(
    "/teachers/{user_id}/summary",
    response_model=AdminTeacherSummaryResponse
)
def admin_teacher_summary(
    user_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_teacher_summary(
        db=db,
        user_id=user_id
    )


@router.get(
    "/classrooms/{classroom_id}/summary",
    response_model=AdminClassroomSummaryResponse
)
def admin_classroom_summary(
    classroom_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_classroom_summary(
        db=db,
        classroom_id=classroom_id
    )

@router.get(
    "/students/{user_id}/summary",
    response_model=AdminStudentSummaryResponse
)
def admin_student_summary(
    user_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(get_db)
):
    return get_admin_student_summary(
        db=db,
        user_id=user_id
    )
