from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import User
from app.security.auth import get_current_user
from app.core.security import verify_password, hash_password

router = APIRouter(prefix="/password", tags=["Password"])

class PasswordChange(BaseModel):
    senha_atual: str
    nova_senha: str = Field(min_length=6)

@router.post("/change")
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(payload.senha_atual, current_user.senha):
        raise HTTPException(status_code=400, detail="Senha atual incorreta.")

    if payload.senha_atual == payload.nova_senha:
        raise HTTPException(status_code=400, detail="A nova senha deve ser diferente da senha atual.")

    current_user.senha = hash_password(payload.nova_senha)
    db.commit()
    return {"message": "Senha alterada com sucesso."}
