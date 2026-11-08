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

from app.schema.notification import (
    NotificationResponse,
    NotificationCountResponse
)

from app.security.auth import (
    get_current_user
)

from app.services.system.notification_service import (
    get_user_notifications,
    get_unread_count,
    mark_notification_read,
    mark_all_notifications_read
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# =========================================================
# MINHAS NOTIFICAÇÕES
# =========================================================

@router.get(
    "/me",
    response_model=list[
        NotificationResponse
    ]
)
def my_notifications(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_user_notifications(

        db=db,

        user_id=current_user.id
    )


# =========================================================
# CONTAGEM NÃO LIDAS
#
# Badge vermelho do frontend.
# =========================================================

@router.get(
    "/me/unread-count",
    response_model=NotificationCountResponse
)
def unread_notifications(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    return {
        "nao_lidas":
            get_unread_count(
                db,
                current_user.id
            )
    }


# =========================================================
# MARCAR TODAS COMO LIDAS
# =========================================================

@router.patch(
    "/me/read-all"
)
def read_all_notifications(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    return mark_all_notifications_read(

        db=db,

        user_id=current_user.id
    )


# =========================================================
# MARCAR UMA COMO LIDA
# =========================================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def read_notification(

    notification_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    return mark_notification_read(

        db=db,

        notification_id=notification_id,

        user_id=current_user.id
    )