from fastapi import Depends, HTTPException, status

from app.database.models import User
from app.security.auth import get_current_user


# =========================================================
# AUXILIAR
# =========================================================

def normalize_user_type(user: User) -> str:
    return (
        user.tipo
        or ""
    ).strip().lower()


# =========================================================
# ALUNO
# =========================================================

def require_student(
    current_user: User = Depends(get_current_user)
):

    tipo = normalize_user_type(
        current_user
    )

    if tipo != "aluno":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para alunos."
        )

    return current_user


# =========================================================
# PROFESSOR
# =========================================================

def require_teacher(
    current_user: User = Depends(get_current_user)
):

    tipo = normalize_user_type(
        current_user
    )

    if tipo != "professor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para professores."
        )

    return current_user


# =========================================================
# ADMINISTRAÇÃO
# =========================================================

def require_admin(
    current_user: User = Depends(get_current_user)
):

    tipo = normalize_user_type(
        current_user
    )

    if tipo not in [
        "administracao",
        "administração"
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para a Administração."
        )

    return current_user


# =========================================================
# PROFESSOR OU ADMINISTRAÇÃO
# =========================================================

def require_teacher_or_admin(
    current_user: User = Depends(get_current_user)
):

    tipo = normalize_user_type(
        current_user
    )

    if tipo not in [
        "professor",
        "administracao",
        "administração"
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Acesso permitido apenas para "
                "professores ou Administração."
            )
        )

    return current_user


# =========================================================
# SUPORTE
# =========================================================

def require_support(
    current_user: User = Depends(get_current_user)
):

    tipo = normalize_user_type(
        current_user
    )

    if tipo != "suporte":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas ao Suporte."
        )

    return current_user


# =========================================================
# ADMINISTRAÇÃO OU SUPORTE
# =========================================================

def require_admin_or_support(
    current_user: User = Depends(get_current_user)
):

    tipo = normalize_user_type(
        current_user
    )

    if tipo not in [
        "administracao",
        "administração",
        "suporte"
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Acesso permitido apenas para "
                "Administração ou Suporte."
            )
        )

    return current_user


# =========================================================
# LEITOR DA BIBLIOTECA PEDAGÓGICA
# ALUNO / PROFESSOR / ADMINISTRAÇÃO
# SUPORTE NÃO ACESSA CONTEÚDO PEDAGÓGICO
# =========================================================

def require_library_reader(
    current_user: User = Depends(get_current_user)
):

    tipo = normalize_user_type(
        current_user
    )

    if tipo not in [
        "aluno",
        "professor",
        "administracao",
        "administração"
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Usuário sem permissão para acessar "
                "conteúdo pedagógico da biblioteca."
            )
        )

    return current_user