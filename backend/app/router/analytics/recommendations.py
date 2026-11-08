from fastapi import (
    APIRouter,
    Depends
)

from app.database.models import User

from app.core.permissions import (
    require_student
)

from app.services.analytics.recommendation_service import (
    generate_schedule
)

from app.schema.recommendation import (
    DayRecommendation
)


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


# =========================================================
# ALUNO
# GERAR RECOMENDAÇÃO DE ESTUDOS
# =========================================================

@router.get(
    "/generate",
    response_model=list[DayRecommendation]
)
def generate_recommendation(
    current_user: User = Depends(require_student)
):

    return generate_schedule(
        current_user
    )