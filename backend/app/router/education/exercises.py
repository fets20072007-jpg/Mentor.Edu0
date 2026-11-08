from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    Exercise,
    Chapter,
    User
)

from app.schema.exercises import (
    ExerciseCreate,
    ExerciseResponse,
    ExerciseSafeResponse
)

from app.services.education.exercise_service import (
    create_exercise
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_teacher
)

from app.core.permissions import (
    require_teacher,
    require_library_reader
)


router = APIRouter(
    prefix="/library",
    tags=["Library Exercises"]
)


# =========================================================
# AUXILIAR
# PROFESSOR / ADMINISTRAÇÃO / SUPORTE
# =========================================================

def require_exercise_full_access(
    current_user: User
):

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()

    tipos_permitidos = [
        "professor",
        "administracao",
        "administração"
    ]

    if tipo not in tipos_permitidos:
        raise HTTPException(
            status_code=403,
            detail=(
                "Usuário sem permissão para "
                "consultar o gabarito deste exercício."
            )
        )


# =========================================================
# SUPORTE
# CADASTRAR EXERCÍCIO INSTITUCIONAL
# =========================================================

@router.post(
    "/chapters/{chapter_id}/exercises",
    response_model=ExerciseResponse
)
def register_exercise(
    chapter_id: int,
    exercise: ExerciseCreate,

    current_user: User = Depends(
    require_teacher
),

    db: Session = Depends(get_db)
):

    chapter = (
        db.query(Chapter)
        .filter(
            Chapter.id == chapter_id
        )
        .first()
    )

    if not chapter:
        raise HTTPException(
            status_code=404,
            detail="Capítulo não encontrado."
        )

    return create_exercise(
        db,
        chapter_id,
        exercise
    )


# =========================================================
# LISTAR EXERCÍCIOS
# VERSÃO SEGURA
# TODOS OS USUÁRIOS AUTENTICADOS
# =========================================================

@router.get(
    "/chapters/{chapter_id}/exercises",
    response_model=list[ExerciseSafeResponse]
)
def list_exercises(
    chapter_id: int,

    current_user: User = Depends(
        require_library_reader
    ),

    db: Session = Depends(get_db)
):

    chapter = (
        db.query(Chapter)
        .filter(
            Chapter.id == chapter_id
        )
        .first()
    )

    if not chapter:
        raise HTTPException(
            status_code=404,
            detail="Capítulo não encontrado."
        )

    return (
        db.query(Exercise)
        .filter(
            Exercise.chapter_id == chapter_id
        )
        .all()
    )


# =========================================================
# LISTAR EXERCÍCIOS
# VERSÃO COMPLETA
# PROFESSOR / ADMINISTRAÇÃO / SUPORTE
# =========================================================

@router.get(
    "/chapters/{chapter_id}/exercises/full",
    response_model=list[ExerciseResponse]
)
def list_exercises_full(
    chapter_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    require_exercise_full_access(
        current_user
    )

    chapter = (
        db.query(Chapter)
        .filter(
            Chapter.id == chapter_id
        )
        .first()
    )

    if not chapter:
        raise HTTPException(
            status_code=404,
            detail="Capítulo não encontrado."
        )

    return (
        db.query(Exercise)
        .filter(
            Exercise.chapter_id == chapter_id
        )
        .all()
    )


# =========================================================
# CONSULTAR EXERCÍCIO
# VERSÃO SEGURA
# =========================================================

@router.get(
    "/exercises/{exercise_id}",
    response_model=ExerciseSafeResponse
)
def get_exercise(
    exercise_id: int,

    current_user: User = Depends(
    require_library_reader
    ),

    db: Session = Depends(get_db)
):

    exercise = (
        db.query(Exercise)
        .filter(
            Exercise.id == exercise_id
        )
        .first()
    )

    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercício não encontrado."
        )

    return exercise


# =========================================================
# CONSULTAR EXERCÍCIO
# VERSÃO COMPLETA
# =========================================================

@router.get(
    "/exercises/{exercise_id}/full",
    response_model=ExerciseResponse
)
def get_exercise_full(
    exercise_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):

    require_exercise_full_access(
        current_user
    )

    exercise = (
        db.query(Exercise)
        .filter(
            Exercise.id == exercise_id
        )
        .first()
    )

    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercício não encontrado."
        )

    return exercise