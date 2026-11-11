from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import (
    get_db
)

from app.database.models import (
    User,
    Ticket
)

from app.schema.ticket import (
    TicketCreate,
    TicketStatusUpdate,
    TicketResponse,
    TicketRecipientResponse,
    ForgotPasswordRequest
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_support
)

from app.services.system.ticket_service import (
    create_ticket,
    get_user_tickets,
    get_user_inbox,
    get_ticket_recipients,
    get_support_tickets,
    get_pending_ticket_count,
    update_ticket_status
)


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


@router.post("/forgot-password", status_code=202)
def forgot_password_request(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    from app.database.models import Ticket
    from app.services.system.notification_service import create_notification
    from sqlalchemy import func
    email = str(data.email).strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if user:
        ticket = Ticket(titulo="Recuperação de senha", descricao=f"Solicitação de recuperação de senha para {user.email}.", categoria="Acesso", prioridade="Alta", status="Aberto", destinatario_perfil="Suporte", requester_id=user.id)
        db.add(ticket); db.flush()
        for support in db.query(User).filter(func.lower(User.tipo) == "suporte").all():
            create_notification(db=db, user_id=support.id, titulo="Recuperação de senha", mensagem=f"Novo pedido de recuperação de senha #{ticket.id}.", tipo="Chamado", link=f"/tickets/{ticket.id}")
        db.commit()
    return {"message": "Se o e-mail estiver cadastrado, a solicitação foi enviada ao suporte."}


# =========================================================
# QUALQUER USUÁRIO AUTENTICADO
# ABRIR CHAMADO
# =========================================================

@router.post(
    "",
    response_model=TicketResponse
)
def register_ticket(

    data: TicketCreate,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    return create_ticket(
        db=db,
        current_user=current_user,
        data=data
    )


# =========================================================
# MEUS CHAMADOS
# =========================================================

@router.get(
    "/me",
    response_model=list[
        TicketResponse
    ]
)
def my_tickets(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_user_tickets(
        db=db,
        user_id=current_user.id
    )


@router.get(
    "/recipients",
    response_model=list[TicketRecipientResponse]
)
def ticket_recipients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_ticket_recipients(db, current_user)


@router.get(
    "/inbox",
    response_model=list[TicketResponse]
)
def ticket_inbox(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_inbox(db, current_user.id)


@router.patch(
    "/{ticket_id}/respond",
    response_model=TicketResponse
)
def respond_to_ticket(
    ticket_id: int,
    data: TicketStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Chamado não encontrado.")
    if ticket.destinatario_user_id != current_user.id and (current_user.tipo or "").strip().lower() != "suporte":
        raise HTTPException(status_code=403, detail="Este chamado não foi direcionado a você.")
    return update_ticket_status(
        db=db, ticket_id=ticket_id, support_user=current_user, data=data
    )


# =========================================================
# SUPORTE
# CONTADOR DE CHAMADOS PENDENTES
# =========================================================

@router.get(
    "/support/pending-count"
)
def support_pending_count(

    current_user: User = Depends(
        require_support
    ),

    db: Session = Depends(
        get_db
    )

):

    return {
        "pendentes":
            get_pending_ticket_count(
                db
            )
    }


# =========================================================
# SUPORTE
# LISTAR TODOS OS CHAMADOS
# =========================================================

@router.get(
    "",
    response_model=list[
        TicketResponse
    ]
)
def list_tickets(

    current_user: User = Depends(
        require_support
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_support_tickets(
        db
    )


# =========================================================
# SUPORTE
# ALTERAR STATUS
# =========================================================

@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse
)
def change_ticket_status(

    ticket_id: int,

    data: TicketStatusUpdate,

    current_user: User = Depends(
        require_support
    ),

    db: Session = Depends(
        get_db
    )

):

    return update_ticket_status(

        db=db,

        ticket_id=ticket_id,

        support_user=current_user,

        data=data
    )