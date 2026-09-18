from fastapi import Depends, HTTPException, status

from app.database.models import User
from app.security.auth import get_current_user


def require_student(
    current_user: User = Depends(get_current_user)
):

    if current_user.tipo != "Aluno":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para alunos."
        )

    return current_user


def require_teacher(
    current_user: User = Depends(get_current_user)
):

    if current_user.tipo != "Professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para professores."
        )

    return current_user


def require_admin(
    current_user: User = Depends(get_current_user)
):

    if current_user.tipo != "Administracao":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para a administração."
        )

    return current_user


def require_teacher_or_admin(
    current_user: User = Depends(get_current_user)
):

    if current_user.tipo not in [
        "Professor",
        "Administracao"
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para professores ou administração."
        )

    return current_user