from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import StudySession, User
from app.schema.study_session import (
    StudySessionCreate,
    StudySessionUpdate,
    StudySessionResponse
)
from app.security.auth import get_current_user

router = APIRouter(
    prefix="/study-sessions",
    tags=["Study Sessions"]
)


@router.post("/", response_model=StudySessionResponse)
def create_study_session(
    session_data: StudySessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_session = StudySession(
        materia=session_data.materia,
        assunto=session_data.assunto,
        duracao_minutos=session_data.duracao_minutos,
        dificuldade_sentida=session_data.dificuldade_sentida,
        concluida=session_data.concluida,
        data_sessao=session_data.data_sessao,
        observacoes=session_data.observacoes,
        user_id=current_user.id
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.get("/", response_model=list[StudySessionResponse])
def list_my_study_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    ).all()

    return sessions


@router.get("/{session_id}", response_model=StudySessionResponse)
def get_study_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sessão de estudo não encontrada"
        )

    return session


@router.put("/{session_id}", response_model=StudySessionResponse)
def update_study_session(
    session_id: int,
    session_update: StudySessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sessão de estudo não encontrada"
        )

    update_data = session_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(session, key, value)

    db.commit()
    db.refresh(session)

    return session


@router.delete("/{session_id}")
def delete_study_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Sessão de estudo não encontrada"
        )

    db.delete(session)
    db.commit()

    return {"message": "Sessão deletada com sucesso"}