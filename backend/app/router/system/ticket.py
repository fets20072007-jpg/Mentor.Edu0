from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database.dependencies import (
    get_db
)

from app.database.models import (
    User
)

from app.schema.ticket import (
    TicketCreate,
    TicketStatusUpdate,
    TicketResponse
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
    get_support_tickets,
    get_pending_ticket_count,
    update_ticket_status
)


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


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