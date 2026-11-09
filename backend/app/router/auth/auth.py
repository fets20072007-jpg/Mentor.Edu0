from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordRequestForm
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.dependencies import get_db
from app.database.models import User

from app.core.security import (
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    email_normalizado = (
        form_data.username
        or ""
    ).strip().lower()


    db_user = (
        db.query(User)
        .filter(
            func.lower(User.email)
            == email_normalizado
        )
        .first()
    )


    # =====================================================
    # RESPOSTA GENERICA
    #
    # Nao informa se o problema foi
    # e-mail, senha ou conta desativada.
    # =====================================================

    if not db_user:

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Credenciais inválidas.",
            headers={
                "WWW-Authenticate":
                    "Bearer"
            }
        )


    if not verify_password(
        form_data.password,
        db_user.senha
    ):

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Credenciais inválidas.",
            headers={
                "WWW-Authenticate":
                    "Bearer"
            }
        )


    if db_user.ativo is False:

        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Credenciais inválidas.",
            headers={
                "WWW-Authenticate":
                    "Bearer"
            }
        )


    token = create_access_token({
        "sub": db_user.email
    })


    return {
        "access_token": token,
        "token_type": "bearer"
    }