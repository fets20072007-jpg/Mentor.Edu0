from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import (
    Notification
)


# =========================================================
# CRIAR NOTIFICAÇÃO
#
# Função interna.
# Outros módulos poderão chamá-la futuramente.
# =========================================================

def create_notification(

    db: Session,

    user_id: int,

    titulo: str,

    mensagem: str,

    tipo: str = "Sistema",

    link: str | None = None,

    commit: bool = False

):

    notification = Notification(

        user_id=user_id,

        titulo=titulo.strip(),

        mensagem=mensagem.strip(),

        tipo=tipo.strip(),

        link=link,

        lida=False
    )

    db.add(
        notification
    )

    if commit:

        db.commit()

        db.refresh(
            notification
        )

    return notification


# =========================================================
# MINHAS NOTIFICAÇÕES
# =========================================================

def get_user_notifications(

    db: Session,

    user_id: int

):

    return (
        db.query(Notification)
        .filter(
            Notification.user_id
            == user_id
        )
        .order_by(
            Notification.id.desc()
        )
        .all()
    )


# =========================================================
# CONTAGEM NÃO LIDAS
#
# Isso será usado naquele badge vermelho do frontend.
# =========================================================

def get_unread_count(

    db: Session,

    user_id: int

):

    return (
        db.query(Notification)
        .filter(
            Notification.user_id
            == user_id,

            Notification.lida
            == False
        )
        .count()
    )


# =========================================================
# MARCAR UMA NOTIFICAÇÃO COMO LIDA
# =========================================================

def mark_notification_read(

    db: Session,

    notification_id: int,

    user_id: int

):

    notification = (
        db.query(Notification)
        .filter(
            Notification.id
            == notification_id,

            Notification.user_id
            == user_id
        )
        .first()
    )

    if not notification:

        raise HTTPException(
            status_code=404,
            detail="Notificação não encontrada."
        )


    if not notification.lida:

        notification.lida = True

        notification.lida_em = (
            datetime.utcnow()
        )

        db.commit()

        db.refresh(
            notification
        )

    return notification


# =========================================================
# MARCAR TODAS COMO LIDAS
# =========================================================

def mark_all_notifications_read(

    db: Session,

    user_id: int

):

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id
            == user_id,

            Notification.lida
            == False
        )
        .all()
    )


    agora = datetime.utcnow()


    for notification in notifications:

        notification.lida = True

        notification.lida_em = (
            agora
        )


    db.commit()

    return {
        "message":
            "Todas as notificações foram marcadas como lidas.",

        "total":
            len(notifications)
    }