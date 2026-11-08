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
    LibraryQuestion
)

from app.core.permissions import (
    require_teacher
)

from app.schema.library_question import (
    LibraryQuestionCreate,
    LibraryQuestionUpdate,
    LibraryQuestionResponse
)

from app.services.education.library_question_service import (
    create_library_question
)


router = APIRouter(
    prefix="/library/question-bank",
    tags=["Question Bank"]
)


# =========================================================
# PERFIL DO PROFESSOR
# =========================================================

def get_teacher_profile(
    db: Session,
    current_user: User
):

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

    return teacher


# =========================================================
# CRIAR QUESTÃO
# =========================================================

@router.post(
    "",
    response_model=LibraryQuestionResponse
)
def register_library_question(
    data: LibraryQuestionCreate,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):

    teacher = get_teacher_profile(
        db,
        current_user
    )


    # Professor somente pode cadastrar questão
    # vinculada a uma disciplina que ele ministra.

    subject = (
        db.query(Subject)
        .filter(
            Subject.id == data.subject_id,
            Subject.teacher_id == teacher.id
        )
        .first()
    )

    if not subject:
        raise HTTPException(
            status_code=403,
            detail=(
                "O professor não possui acesso "
                "a esta disciplina."
            )
        )

    return create_library_question(
        db,
        teacher.id,
        data
    )


# =========================================================
# MINHAS QUESTÕES
# =========================================================

@router.get(
    "/me",
    response_model=list[LibraryQuestionResponse]
)
def my_library_questions(
    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):

    teacher = get_teacher_profile(
        db,
        current_user
    )

    return (
        db.query(LibraryQuestion)
        .filter(
            LibraryQuestion.teacher_id == teacher.id,
            LibraryQuestion.ativa == True
        )
        .order_by(
            LibraryQuestion.criado_em.desc()
        )
        .all()
    )


# =========================================================
# QUESTÕES COMPARTILHADAS
# =========================================================

@router.get(
    "/shared",
    response_model=list[LibraryQuestionResponse]
)
def shared_library_questions(
    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):

    teacher = get_teacher_profile(
        db,
        current_user
    )

    return (
        db.query(LibraryQuestion)
        .filter(
            LibraryQuestion.compartilhada == True,
            LibraryQuestion.ativa == True,
            LibraryQuestion.teacher_id != teacher.id
        )
        .order_by(
            LibraryQuestion.criado_em.desc()
        )
        .all()
    )


# =========================================================
# CONSULTAR UMA QUESTÃO
# =========================================================

@router.get(
    "/{question_id}",
    response_model=LibraryQuestionResponse
)
def get_library_question(
    question_id: int,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):

    teacher = get_teacher_profile(
        db,
        current_user
    )

    question = (
        db.query(LibraryQuestion)
        .filter(
            LibraryQuestion.id == question_id,
            LibraryQuestion.ativa == True
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Questão não encontrada."
        )

    if (
        question.teacher_id != teacher.id
        and not question.compartilhada
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Esta questão pertence ao "
                "banco privado de outro professor."
            )
        )

    return question


# =========================================================
# EDITAR MINHA QUESTÃO
# =========================================================

@router.patch(
    "/{question_id}",
    response_model=LibraryQuestionResponse
)
def update_library_question(
    question_id: int,
    data: LibraryQuestionUpdate,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):

    teacher = get_teacher_profile(
        db,
        current_user
    )

    question = (
        db.query(LibraryQuestion)
        .filter(
            LibraryQuestion.id == question_id,
            LibraryQuestion.ativa == True
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Questão não encontrada."
        )

    if question.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail=(
                "Somente o autor pode "
                "editar esta questão."
            )
        )

    dados = data.model_dump(
        exclude_unset=True
    )

    for campo, valor in dados.items():
        setattr(
            question,
            campo,
            valor
        )

    db.commit()

    db.refresh(question)

    return question


# =========================================================
# REMOVER MINHA QUESTÃO
# SOFT DELETE
# =========================================================

@router.delete(
    "/{question_id}"
)
def delete_library_question(
    question_id: int,

    current_user: User = Depends(
        require_teacher
    ),

    db: Session = Depends(get_db)
):

    teacher = get_teacher_profile(
        db,
        current_user
    )

    question = (
        db.query(LibraryQuestion)
        .filter(
            LibraryQuestion.id == question_id,
            LibraryQuestion.ativa == True
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Questão não encontrada."
        )

    if question.teacher_id != teacher.id:
        raise HTTPException(
            status_code=403,
            detail=(
                "Somente o autor pode "
                "remover esta questão."
            )
        )

    question.ativa = False

    db.commit()

    return {
        "message": "Questão removida do banco."
    }