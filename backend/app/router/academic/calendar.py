from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.database.models import User, AcademicEvent
from app.security.auth import get_current_user
from app.core.permissions import require_admin

router = APIRouter(prefix='/academic-calendar', tags=['Academic Calendar'])

class EventCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    tipo: str = 'Evento'
    visibilidade: str = 'todos'
    data_inicio: str


def _role(user: User) -> str:
    return (user.tipo or '').strip().lower()

@router.get('')
def list_events(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role = _role(current_user)
    query = db.query(AcademicEvent).filter(AcademicEvent.ativo == True)
    if role == 'aluno':
        query = query.filter(AcademicEvent.visibilidade.in_(['todos','alunos']))
    elif role == 'professor':
        query = query.filter(AcademicEvent.visibilidade.in_(['todos','professores']))
    return query.order_by(AcademicEvent.data_inicio.asc()).all()

@router.post('')
def create_event(payload: EventCreate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    if payload.visibilidade not in {'todos','alunos','professores'}:
        raise HTTPException(status_code=400, detail='Visibilidade inválida.')
    try:
        dt = datetime.fromisoformat(payload.data_inicio)
    except ValueError:
        raise HTTPException(status_code=400, detail='Data inválida.')
    event = AcademicEvent(titulo=payload.titulo.strip(),descricao=(payload.descricao or '').strip() or None,tipo=payload.tipo.strip() or 'Evento',visibilidade=payload.visibilidade,data_inicio=dt,ativo=True)
    db.add(event);db.commit();db.refresh(event);return event

@router.delete('/{event_id}')
def delete_event(event_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    event=db.query(AcademicEvent).filter(AcademicEvent.id==event_id).first()
    if not event: raise HTTPException(status_code=404,detail='Evento não encontrado.')
    event.ativo=False;db.commit();return {'message':'Evento removido.'}
