from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import User, Assessment, Question

from app.schema.assessment import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse
)

from app.schema.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse
)

from app.schema.question_student import QuestionStudentResponse

from app.schema.assessment_result import (
    AssessmentResultResponse
)

from app.schema.assessment_results import (
    AssessmentStudentResultResponse
)

from app.schema.assessment_history import (
    AssessmentHistoryResponse
)

from app.services.academic.assessment_service import (
    create_assessment,
    get_all_assessments,
    get_assessment_by_id,
    update_assessment,
    get_student_assessment_result,
    get_student_result_for_teacher,
    get_assessment_results,
    get_student_assessment_history,
    get_student_assessment_history_filtered,
    get_student_summary,
    get_student_summary_by_subject,
    get_student_evolution,
    get_teacher_classroom_summary,
    get_teacher_students_difficulties,
    get_teacher_students_performance,
    get_student_content_difficulties,
    get_teacher_questions_difficulties,
    get_student_analysis_data,
    get_teacher_assessment,
    get_assessments_for_user,
    get_assessment_for_user

)

from app.core.permissions import (
    require_student,
    require_teacher
)

from app.schema.student_summary import (
    StudentSummaryResponse
)

from app.schema.student_subject_summary import (
    StudentSubjectSummaryResponse
)

from app.schema.student_evolution import (
    StudentEvolutionResponse
)

from app.schema.teacher_classroom_summary import (
    TeacherClassroomSummaryResponse
)

from app.schema.teacher_student_difficulty import (
    TeacherStudentDifficultyResponse
)

from app.schema.teacher_student_performance import (
    TeacherStudentPerformanceResponse
)

from app.schema.student_content_difficulty import (
    StudentContentDifficultyResponse
)

from app.schema.question_difficulty import (
    QuestionDifficultyResponse
)

from app.schema.student_analysis_data import (
    StudentAnalysisDataResponse
)

from app.services.academic.assessment_access_service import (
    ensure_student_can_view_questions,
    ensure_student_result_released
)

from app.security.auth import get_current_user
router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"]
)


# =========================================================
# PROFESSOR - CRIAR AVALIAÇÃO
# =========================================================

@router.post(
    "",
    response_model=AssessmentResponse
)
def register_assessment(
    assessment: AssessmentCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    return create_assessment(
        db,
        current_user.id,
        assessment
    )


# =========================================================
# LISTAR AVALIAÇÕES
# =========================================================

@router.get(
    "/",
    response_model=list[AssessmentResponse]
)
def list_assessments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_assessments_for_user(
        db=db,
        current_user=current_user
    )

# =========================================================
# BUSCAR AVALIAÇÃO
# =========================================================

@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse
)
def assessment_details(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_assessment_for_user(
        db=db,
        assessment_id=assessment_id,
        current_user=current_user
    )


# =========================================================
# LISTAR QUESTÕES
# =========================================================

@router.get(
    "/{assessment_id}/questions",
    response_model=list[
        QuestionStudentResponse
    ]
)
def assessment_questions(

    assessment_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    assessment = get_assessment_for_user(

        db=db,

        assessment_id=assessment_id,

        current_user=current_user
    )


    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()


    if tipo == "aluno":

        ensure_student_can_view_questions(

            db=db,

            assessment_id=assessment.id,

            student_id=current_user.id
        )


    return (
        db.query(Question)
        .filter(
            Question.assessment_id
            == assessment.id
        )
        .all()
    )

# =========================================================
# PROFESSOR - EDITAR AVALIAÇÃO
# =========================================================

@router.patch(
    "/{assessment_id}",
    response_model=AssessmentResponse
)
def edit_assessment(
    assessment_id: int,
    assessment: AssessmentUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    return update_assessment(
        db=db,
        assessment_id=assessment_id,
        teacher_user_id=current_user.id,
        data=assessment
    )


# =========================================================
# ALUNO - VER PRÓPRIO RESULTADO
# =========================================================

@router.get(
    "/{assessment_id}/results/me",
    response_model=AssessmentResultResponse
)
def my_assessment_result(

    assessment_id: int,

    current_user: User = Depends(
        require_student
    ),

    db: Session = Depends(
        get_db
    )

):

    ensure_student_result_released(

        db=db,

        assessment_id=assessment_id,

        student_id=current_user.id
    )


    return get_student_assessment_result(

        db,

        assessment_id,

        current_user.id
    )

# =========================================================
# PROFESSOR - VER RESULTADOS DA TURMA
# =========================================================

@router.get(
    "/{assessment_id}/results",
    response_model=list[AssessmentStudentResultResponse]
)
def assessment_results(
    assessment_id: int,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):
    get_teacher_assessment(
        db=db,
        assessment_id=assessment_id,
        teacher_user_id=current_user.id
    )

    return get_assessment_results(
        db=db,
        assessment_id=assessment_id
    )

@router.get(
    "/{assessment_id}/questions/teacher",
    response_model=list[QuestionResponse]
)
def teacher_assessment_questions(
    assessment_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    assessment = get_teacher_assessment(
        db=db,
        assessment_id=assessment_id,
        teacher_user_id=current_user.id
    )

    return (
        db.query(Question)
        .filter(
            Question.assessment_id == assessment.id
        )
        .all()
    )


# =========================================================
# ALUNO - HISTÓRICO
# =========================================================

@router.get(
    "/history/me",
    response_model=list[AssessmentHistoryResponse]
)
def my_assessment_history(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    return get_student_assessment_history(
        db,
        current_user.id
    )


# =========================================================
# ALUNO - HISTÓRICO COM FILTROS
# =========================================================

@router.get(
    "/history/me/filter",
    response_model=list[AssessmentHistoryResponse]
)
def my_assessment_history_filtered(
    subject_id: int | None = None,
    semestre: int | None = None,
    ano_letivo: int | None = None,

    classroom_id: int | None = None,
    teacher_id: int | None = None,

    tipo: str | None = None,

    data_inicio: date | None = None,
    data_fim: date | None = None,

    status_desempenho: str | None = None,

    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    return get_student_assessment_history_filtered(
        db=db,
        user_id=current_user.id,

        subject_id=subject_id,
        semestre=semestre,
        ano_letivo=ano_letivo,

        classroom_id=classroom_id,
        teacher_id=teacher_id,

        tipo=tipo,

        data_inicio=data_inicio,
        data_fim=data_fim,

        status_desempenho=status_desempenho
    )

@router.get(
    "/summary/me",
    response_model=StudentSummaryResponse
)
def my_summary(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    return get_student_summary(
        db,
        current_user.id
    )

@router.get(
    "/summary/me/subjects",
    response_model=list[StudentSubjectSummaryResponse]
)
def my_subject_summary(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    return get_student_summary_by_subject(
        db,
        current_user.id
    )

@router.get(
    "/summary/me/evolution",
    response_model=list[StudentEvolutionResponse]
)
def my_evolution(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    return get_student_evolution(
        db,
        current_user.id
    )

@router.get(
    "/teacher/summary/classrooms",
    response_model=list[TeacherClassroomSummaryResponse]
)
def teacher_classroom_summary(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    return get_teacher_classroom_summary(
        db,
        current_user.id
    )

@router.get(
    "/teacher/difficulties/students",
    response_model=list[TeacherStudentDifficultyResponse]
)
def teacher_students_difficulties(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    return get_teacher_students_difficulties(
        db,
        current_user.id
    )

@router.get(
    "/teacher/students/performance",
    response_model=list[
        TeacherStudentPerformanceResponse
    ]
)
def teacher_students_performance(
    nome: str | None = None,
    status: str | None = None,
    subject_id: int | None = None,
    categoria: str | None = None,
    classroom_id: int | None = None,
    semestre: int | None = None,
    ano_letivo: int | None = None,
    ordem: str = "menor_media",

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):
    return get_teacher_students_performance(
        db=db,
        user_id=current_user.id,
        nome=nome,
        status=status,
        subject_id=subject_id,
        categoria=categoria,
        classroom_id=classroom_id,
        semestre=semestre,
        ano_letivo=ano_letivo,
        ordem=ordem
    )

@router.get(
    "/teacher/students/{student_id}/difficulties",
    response_model=list[
        StudentContentDifficultyResponse
    ]
)
def student_content_difficulties(
    student_id: int,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):
    return get_student_content_difficulties(
        db=db,
        teacher_user_id=current_user.id,
        student_id=student_id
    )

@router.get(
    "/teacher/questions/difficulties",
    response_model=list[
        QuestionDifficultyResponse
    ]
)
def teacher_questions_difficulties(
    subject_id: int | None = None,
    classroom_id: int | None = None,
    categoria: str | None = None,
    student_id: int | None = None,
    semestre: int | None = None,
    ano_letivo: int | None = None,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):
    return get_teacher_questions_difficulties(
        db=db,
        teacher_user_id=current_user.id,
        subject_id=subject_id,
        classroom_id=classroom_id,
        categoria=categoria,
        student_id=student_id,
        semestre=semestre,
        ano_letivo=ano_letivo
    )

@router.get(
    "/teacher/students/{student_id}/analysis-data",
    response_model=StudentAnalysisDataResponse
)
def student_analysis_data(
    student_id: int,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):
    return get_student_analysis_data(
        db=db,
        teacher_user_id=current_user.id,
        student_id=student_id
    )

@router.post(
    "/{assessment_id}/questions",
    response_model=QuestionResponse
)
def add_question_to_assessment(
    assessment_id: int,
    question: QuestionCreate,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):
    get_teacher_assessment(
        db=db,
        assessment_id=assessment_id,
        teacher_user_id=current_user.id
    )

    question.assessment_id = assessment_id

    nova_questao = Question(
        **question.model_dump()
    )

    db.add(nova_questao)
    db.commit()
    db.refresh(nova_questao)

    return nova_questao

@router.patch(
    "/{assessment_id}/questions/{question_id}",
    response_model=QuestionResponse
)
def edit_assessment_question(
    assessment_id: int,
    question_id: int,
    question_data: QuestionUpdate,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):
    # Confirma que a avaliação pertence ao professor
    get_teacher_assessment(
        db=db,
        assessment_id=assessment_id,
        teacher_user_id=current_user.id
    )

    # Confirma que a questão pertence à avaliação
    question = (
        db.query(Question)
        .filter(
            Question.id == question_id,
            Question.assessment_id == assessment_id
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Questão não encontrada nesta avaliação."
        )

    update_data = question_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            question,
            field,
            value
        )

    db.commit()
    db.refresh(question)

    return question

@router.get(
    "/{assessment_id}/results/students/{student_id}",
    response_model=AssessmentResultResponse
)
def assessment_student_result(
    assessment_id: int,
    student_id: int,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):
    get_teacher_assessment(
        db=db,
        assessment_id=assessment_id,
        teacher_user_id=current_user.id
    )

    return get_student_result_for_teacher(
        db=db,
        assessment_id=assessment_id,
        student_id=student_id
    )