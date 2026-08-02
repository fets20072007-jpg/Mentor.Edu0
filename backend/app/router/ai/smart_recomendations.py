from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (

    StudentAnswer,

    User

)

from app.security.auth import get_current_user

from app.services.education.recommendation_engine import (

    generate_smart_recommendation

)

from app.schema.smart_recommendation import (

    SmartRecommendation

)

router = APIRouter(

    prefix="/smart-recommendations",

    tags=["Smart Recommendations"]

)


@router.get(

    "/me",

    response_model=list[SmartRecommendation]

)

def smart_recommendation(

    current_user: User = Depends(

        get_current_user

    ),

    db: Session = Depends(get_db)

):

    respostas = (

        db.query(StudentAnswer)

        .filter(

            StudentAnswer.user_id == current_user.id

        )

        .all()

    )

    return generate_smart_recommendation(

        respostas

    )