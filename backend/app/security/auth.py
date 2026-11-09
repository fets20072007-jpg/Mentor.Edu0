from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordBearer
)

from jose import (
    JWTError,
    jwt
)

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import User

from app.core.config import (
    SECRET_KEY,
    ALGORITHM
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=(
            status.HTTP_401_UNAUTHORIZED
        ),
        detail="Credenciais inválidas.",
        headers={
            "WWW-Authenticate":
                "Bearer"
        }
    )


    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[
                ALGORITHM
            ]
        )


        email = payload.get(
            "sub"
        )


        if (
            not email
            or not isinstance(
                email,
                str
            )
        ):

            raise credentials_exception


    except JWTError:

        raise credentials_exception


    email_normalizado = (
        email
        .strip()
        .lower()
    )


    usuario = (
        db.query(User)
        .filter(
            func.lower(User.email)
            == email_normalizado
        )
        .first()
    )


    if usuario is None:

        raise credentials_exception


    # Conta desativada invalida inclusive
    # tokens emitidos anteriormente.

    if usuario.ativo is False:

        raise credentials_exception


    return usuario