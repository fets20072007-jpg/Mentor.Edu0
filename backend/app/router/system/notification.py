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

# ==========================================================
# MENTOR EDU 9B3 - STUDY REMINDER BRIDGE
# ==========================================================
# 1. Espelha study_focus_alerts na área geral de Notificações.
# 2. Cria cobrança interna quando o aluno volta após horas fora.
# 3. Não depende do Web Push para a notificação interna existir.
# ==========================================================

from datetime import datetime as _me9b3_datetime, timedelta as _me9b3_timedelta
from sqlalchemy import text as _me9b3_text, inspect as _me9b3_inspect
from sqlalchemy.orm import Session as _Me9B3Session
from app.database.dependencies import get_db as _me9b3_get_db
from app.database.models import (
    Notification as _Me9B3Notification,
    User as _Me9B3User,
)
from app.security.auth import get_current_user as _me9b3_get_current_user


def _me9b3_level_from_row(row):
    for key in (
        "nivel",
        "nivel_atual",
        "nivel_alerta",
        "nivel_urgencia",
        "urgencia",
        "level",
        "alert_level",
        "last_level",
        "ultimo_nivel",
    ):
        value = row.get(key)
        if value not in (None, ""):
            return str(value).strip().lower()
    return "lembrete"


def _me9b3_focus_copy(level):
    normalized = (level or "").lower()

    if "critic" in normalized or "crít" in normalized:
        return (
            "Sessão de estudo precisa de atenção",
            "Você está há bastante tempo longe desta sessão. "
            "Volte ao Mentor Edu para retomar o foco."
        )

    if "alto" in normalized or "high" in normalized:
        return (
            "Sua sessão de estudo está esperando",
            "Seu tempo fora da sessão aumentou. "
            "Que tal voltar e concluir o que você planejou?"
        )

    if (
        "medio" in normalized
        or "médio" in normalized
        or "medium" in normalized
    ):
        return (
            "Lembrete da sua sessão de estudo",
            "Você tem uma sessão de estudo que ainda precisa da sua atenção."
        )

    return (
        "Lembrete de estudo",
        "Sua sessão continua pendente. "
        "Abra o Mentor Edu quando puder e continue de onde parou."
    )


def _me9b3_upsert_focus_notification(db, user_id, row):
    session_id = row.get("session_id")
    if session_id is None:
        return (0, 0)

    level = _me9b3_level_from_row(row)
    title, message = _me9b3_focus_copy(level)
    link = f"#/study-sessions?mentor_session={session_id}"
    now = _me9b3_datetime.utcnow()

    existing = (
        db.query(_Me9B3Notification)
        .filter(
            _Me9B3Notification.user_id == user_id,
            _Me9B3Notification.tipo == "MentorEstudo",
            _Me9B3Notification.link == link,
            _Me9B3Notification.lida == False,
        )
        .order_by(_Me9B3Notification.criado_em.desc())
        .first()
    )

    if existing:
        changed = (
            existing.titulo != title
            or existing.mensagem != message
        )
        if changed:
            existing.titulo = title
            existing.mensagem = message
            existing.criado_em = now
            return (0, 1)
        return (0, 0)

    recent_cutoff = now - _me9b3_timedelta(hours=6)
    recent = (
        db.query(_Me9B3Notification)
        .filter(
            _Me9B3Notification.user_id == user_id,
            _Me9B3Notification.tipo == "MentorEstudo",
            _Me9B3Notification.link == link,
            _Me9B3Notification.criado_em >= recent_cutoff,
        )
        .first()
    )

    if recent:
        return (0, 0)

    db.add(
        _Me9B3Notification(
            titulo=title,
            mensagem=message,
            tipo="MentorEstudo",
            link=link,
            lida=False,
            criado_em=now,
            user_id=user_id,
        )
    )
    return (1, 0)


def _me9b3_inactivity_notification(db, user_id, away_seconds):
    try:
        away_seconds = max(0.0, float(away_seconds or 0))
    except (TypeError, ValueError):
        away_seconds = 0.0

    # 6 horas fora: lembra sem ficar cobrando a cada instante.
    if away_seconds < 6 * 60 * 60:
        return 0

    hours = away_seconds / 3600.0
    now = _me9b3_datetime.utcnow()
    link = "mentor://study-inactivity"

    if hours >= 24:
        title = "Vamos retomar sua rotina de estudos?"
        message = (
            "Você passou mais de um dia longe do Mentor Edu. "
            "Veja suas sessões e escolha um próximo passo pequeno para recomeçar."
        )
    elif hours >= 12:
        title = "Seu Mentor sentiu sua falta"
        message = (
            "Já faz algumas horas desde sua última atividade. "
            "Dê uma olhada nas sessões de estudo e retome de onde parou."
        )
    else:
        title = "Que tal voltar aos estudos?"
        message = (
            "Você ficou algumas horas longe do Mentor Edu. "
            "Confira suas sessões pendentes e continue no seu ritmo."
        )

    unread = (
        db.query(_Me9B3Notification)
        .filter(
            _Me9B3Notification.user_id == user_id,
            _Me9B3Notification.tipo == "MentorEstudo",
            _Me9B3Notification.link == link,
            _Me9B3Notification.lida == False,
        )
        .first()
    )

    if unread:
        return 0

    recent_cutoff = now - _me9b3_timedelta(hours=6)
    recent = (
        db.query(_Me9B3Notification)
        .filter(
            _Me9B3Notification.user_id == user_id,
            _Me9B3Notification.tipo == "MentorEstudo",
            _Me9B3Notification.link == link,
            _Me9B3Notification.criado_em >= recent_cutoff,
        )
        .first()
    )

    if recent:
        return 0

    db.add(
        _Me9B3Notification(
            titulo=title,
            mensagem=message,
            tipo="MentorEstudo",
            link=link,
            lida=False,
            criado_em=now,
            user_id=user_id,
        )
    )
    return 1


@router.post("/me/study-reminder-sync")
def mentor_9b3_study_reminder_sync(
    payload: dict = None,
    current_user: _Me9B3User = Depends(_me9b3_get_current_user),
    db: _Me9B3Session = Depends(_me9b3_get_db),
):
    user_type = (
        getattr(current_user, "tipo", "")
        or ""
    ).strip().lower()

    if user_type not in ("aluno", "student"):
        return {
            "ok": True,
            "ignored": True,
            "reason": "not_student",
        }

    payload = payload or {}
    away_seconds = payload.get("away_seconds", 0)

    created = 0
    updated = 0
    focus_alerts = 0

    # A 9B.1 usa study_focus_alerts.
    # Fazemos reflexão da tabela para não depender do nome da classe ORM.
    try:
        bind = db.get_bind()
        table_names = set(
            _me9b3_inspect(bind).get_table_names()
        )

        if "study_focus_alerts" in table_names:
            rows = (
                db.execute(
                    _me9b3_text(
                        "SELECT * FROM study_focus_alerts "
                        "WHERE user_id = :user_id"
                    ),
                    {"user_id": current_user.id},
                )
                .mappings()
                .all()
            )

            focus_alerts = len(rows)

            for row in rows:
                added, changed = _me9b3_upsert_focus_notification(
                    db,
                    current_user.id,
                    row,
                )
                created += added
                updated += changed

    except Exception as exc:
        # O lembrete por inatividade continua funcionando mesmo
        # se a estrutura da 9B.1 estiver diferente.
        print(
            "[MENTOR 9B3] falha ao espelhar study_focus_alerts:",
            type(exc).__name__,
            str(exc),
        )

    created += _me9b3_inactivity_notification(
        db,
        current_user.id,
        away_seconds,
    )

    db.commit()

    try:
        away_hours = round(
            max(0.0, float(away_seconds or 0)) / 3600.0,
            2,
        )
    except (TypeError, ValueError):
        away_hours = 0.0

    return {
        "ok": True,
        "created": created,
        "updated": updated,
        "focus_alerts": focus_alerts,
        "away_hours": away_hours,
    }
