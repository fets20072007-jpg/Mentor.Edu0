from fastapi import APIRouter

from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (

    StudentAnswer,

    User

)

from app.security.auth import (

    get_current_user

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


@router.get(

    "/me",

    response_model=PerformanceResponse

)

def my_performance(

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

    return calculate_performance(

        respostas

    )