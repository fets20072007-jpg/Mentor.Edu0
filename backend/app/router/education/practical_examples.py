from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    PracticalExample,
    Chapter,
    User
)

from app.schema.practical_example import (
    PracticalExampleCreate,
    PracticalExampleResponse
)

from app.services.education.practical_example_service import (
    create_example
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_teacher,
    require_library_reader
)


router = APIRouter(
    prefix="/library",
    tags=["Library Practical Examples"]
)


# =========================================================
# PROFESSOR
# CADASTRAR EXEMPLO PRÁTICO
# =========================================================

@router.post(
    "/chapters/{chapter_id}/examples",
    response_model=PracticalExampleResponse
)
def register_example(
    chapter_id: int,
    example: PracticalExampleCreate,

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

    return create_example(
        db,
        chapter_id,
        example
    )


# =========================================================
# LISTAR EXEMPLOS PRÁTICOS
# USUÁRIOS AUTENTICADOS
# =========================================================

@router.get(
    "/chapters/{chapter_id}/examples",
    response_model=list[PracticalExampleResponse]
)
def list_examples(
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
        db.query(PracticalExample)
        .filter(
            PracticalExample.chapter_id == chapter_id
        )
        .all()
    )


# =========================================================
# CONSULTAR EXEMPLO PRÁTICO
# USUÁRIOS AUTENTICADOS
# =========================================================

@router.get(
    "/examples/{example_id}",
    response_model=PracticalExampleResponse
)
def get_example(
    example_id: int,

    current_user: User = Depends(
    require_library_reader
),

    db: Session = Depends(get_db)
):

    example = (
        db.query(PracticalExample)
        .filter(
            PracticalExample.id == example_id
        )
        .first()
    )

    if not example:
        raise HTTPException(
            status_code=404,
            detail="Exemplo prático não encontrado."
        )

    return example