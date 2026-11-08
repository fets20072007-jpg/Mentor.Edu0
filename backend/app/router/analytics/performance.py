from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    StudentAnswer,
    User
)

from app.core.permissions import (
    require_student
)

from app.schema.performance import (
    PerformanceResponse
)

from app.services.analytics.performance_service import (
    calculate_performance
)


router = APIRouter(
    prefix="/performance",
    tags=["Performance"]
)


# =========================================================
# ALUNO
# MEU DESEMPENHO GERAL
# =========================================================

@router.get(
    "/me",
    response_model=PerformanceResponse
)
def my_performance(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):

    respostas = (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.user_id == current_user.id
        )
        .all()
    )

    return calculate_performance(
        respostas
    )