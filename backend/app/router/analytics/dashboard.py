from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (

    User,

    StudentAnswer,

    Book

)

from app.security.auth import get_current_user

from app.schema.dashboard import StudentDashboard

router = APIRouter(

    prefix="/dashboard",

    tags=["Dashboard"]

)


@router.get(

    "/me",

    response_model=StudentDashboard

)

def dashboard(

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

    total = len(respostas)

    acertos = sum(

        1

        for r in respostas

        if r.correta

    )

    erros = total - acertos

    tempos = [

        r.tempo_resposta

        for r in respostas

        if r.tempo_resposta is not None

    ]

    if len(tempos) > 0:

        tempo_medio = int(

            sum(tempos) / len(tempos)

        )

    else:

        tempo_medio = 0

    livros = db.query(Book).count()

    return StudentDashboard(

        nome=current_user.nome,

        horas_estudo=current_user.horas_estudo or 0,

        questoes_respondidas=total,

        acertos=acertos,

        erros=erros,

        tempo_medio=tempo_medio,

        livros_recomendados=livros,

        ultima_recomendacao="Continue seguindo seu cronograma."

    )