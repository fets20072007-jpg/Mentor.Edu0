print("RECOMMENDATIONS CARREGADO")

from fastapi import APIRouter

from fastapi import Depends

from app.database.models import User

from app.security.auth import get_current_user

from app.services.analytics.recommendation_service import generate_schedule
from app.schema.recommendation import DayRecommendation

router = APIRouter(

    prefix="/recommendations",

    tags=["Recommendations"]

)


@router.get(

    "/generate",

    response_model=list[DayRecommendation]

)

def generate_recommendation(

    current_user: User = Depends(

        get_current_user

    )

):

    return generate_schedule(

        current_user

    )