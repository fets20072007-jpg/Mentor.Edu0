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
    get_student_summary
)

from app.core.permissions import (
    require_student,
    require_teacher
)

from app.schema.student_summary import (
    StudentSummaryResponse
)


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
    db: Session = Depends(get_db)
):
    return get_all_assessments(db)


# =========================================================
# BUSCAR AVALIAÇÃO
# =========================================================

@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse
)
def assessment_by_id(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    return get_assessment_by_id(
        db,
        assessment_id
    )


# =========================================================
# PROFESSOR - CRIAR QUESTÃO
# =========================================================

@router.post(
    "/{assessment_id}/questions",
    response_model=QuestionResponse
)
def create_assessment_question(
    assessment_id: int,
    question: QuestionCreate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )

    new_question = Question(
        tipo=question.tipo,
        enunciado=question.enunciado,

        alternativa_a=question.alternativa_a,
        alternativa_b=question.alternativa_b,
        alternativa_c=question.alternativa_c,
        alternativa_d=question.alternativa_d,

        resposta_correta=question.resposta_correta,
        explicacao=question.explicacao,

        dificuldade=question.dificuldade,
        peso=question.peso,
        categoria=question.categoria,

        criterio_0=question.criterio_0,
        criterio_25=question.criterio_25,
        criterio_50=question.criterio_50,
        criterio_75=question.criterio_75,
        criterio_100=question.criterio_100,

        chapter_id=question.chapter_id,
        assessment_id=assessment.id
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


# =========================================================
# LISTAR QUESTÕES
# =========================================================

@router.get(
    "/{assessment_id}/questions",
    response_model=list[QuestionResponse]
)
def list_assessment_questions(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )

    return (
        db.query(Question)
        .filter(
            Question.assessment_id == assessment_id
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
    data: AssessmentUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    return update_assessment(
        db,
        assessment_id,
        data
    )


# =========================================================
# PROFESSOR - EDITAR QUESTÃO
# =========================================================

@router.patch(
    "/{assessment_id}/questions/{question_id}",
    response_model=QuestionResponse
)
def update_assessment_question(
    assessment_id: int,
    question_id: int,
    data: QuestionUpdate,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
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

    update_data = data.model_dump(
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


# =========================================================
# ALUNO - VER PRÓPRIO RESULTADO
# =========================================================

@router.get(
    "/{assessment_id}/results/me",
    response_model=AssessmentResultResponse
)
def my_assessment_result(
    assessment_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    return get_student_assessment_result(
        db,
        assessment_id,
        current_user.id
    )


# =========================================================
# PROFESSOR - VER RESULTADO DE UM ALUNO
# =========================================================

@router.get(
    "/{assessment_id}/results/students/{student_id}",
    response_model=AssessmentResultResponse
)
def student_assessment_result(
    assessment_id: int,
    student_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    return get_student_result_for_teacher(
        db,
        assessment_id,
        student_id
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
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    return get_assessment_results(
        db,
        assessment_id
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