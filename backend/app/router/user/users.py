from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import User

from app.schema.users import (
    UserCreate,
    UserResponse,
    UserUpdate
)

from app.core.security import hash_password

from app.security.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    hashed_password = hash_password(
        user.senha
    )

    novo_usuario = User(
        nome=user.nome,
        email=user.email,
        senha=hashed_password,

        tipo=user.tipo,

        bio=user.bio,
        escola=user.escola,
        serie=user.serie,
        idade=user.idade,

        objetivo=user.objetivo,
        materias_favoritas=user.materias_favoritas,
        dificuldades=user.dificuldades,
        horas_estudo=user.horas_estudo
    )

    db.add(novo_usuario)

    db.commit()

    db.refresh(novo_usuario)

    return novo_usuario


@router.get(
    "/",
    response_model=list[UserResponse]
)
def list_users(
    db: Session = Depends(get_db)
):

    return db.query(User).all()

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.put(
    "/me",
    response_model=UserResponse
)
def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    update_data = user_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        setattr(
            current_user,
            key,
            value
        )

    db.commit()

    db.refresh(current_user)

    return current_user


@router.delete("/me")
def delete_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db.delete(current_user)

    db.commit()

    return {
        "message": "Usuário deletado com sucesso"
    }