import unicodedata

from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import (
    Ticket,
    User
)

from app.services.system.notification_service import (
    create_notification
)


# =========================================================
# NORMALIZA TEXTO
# =========================================================

def normalize_text(
    value: str
):

    value = (
        value
        or ""
    ).strip().lower()

    value = unicodedata.normalize(
        "NFKD",
        value
    )

    return "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )


# =========================================================
# PRIORIDADE
# =========================================================

def normalize_priority(
    prioridade: str
):

    value = normalize_text(
        prioridade
    )


    mapping = {

        "baixa":
            "Baixa",

        "media":
            "Media",

        "alta":
            "Alta"
    }


    if value not in mapping:

        raise HTTPException(
            status_code=400,
            detail=(
                "Prioridade inválida. "
                "Use Baixa, Media ou Alta."
            )
        )


    return mapping[value]


# =========================================================
# STATUS
# =========================================================

def normalize_status(
    status: str
):

    value = normalize_text(
        status
    )

    # Normaliza espaços também
    value = " ".join(
        value.split()
    )

    mapping = {

        "aberto":
            "Aberto",

        "em analise":
            "Em análise",

        "analise":
            "Em análise",

        "em andamento":
            "Em análise",

        "resolvido":
            "Resolvido"
    }


    if value not in mapping:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Status inválido: '{status}'. "
                "Use Aberto, Em análise ou Resolvido."
            )
        )


    return mapping[value]


# =========================================================
# CRIAR CHAMADO
# =========================================================

def create_ticket(

    db: Session,

    current_user,

    data

):

    titulo = (
        data.titulo
        or ""
    ).strip()


    descricao = (
        data.descricao
        or ""
    ).strip()


    categoria = (
        data.categoria
        or "Sistema"
    ).strip()


    if not titulo:

        raise HTTPException(
            status_code=400,
            detail=(
                "O título do chamado "
                "é obrigatório."
            )
        )


    if not descricao:

        raise HTTPException(
            status_code=400,
            detail=(
                "A descrição do chamado "
                "é obrigatória."
            )
        )


    prioridade = normalize_priority(
        data.prioridade
    )


    ticket = Ticket(

        titulo=titulo,

        descricao=descricao,

        categoria=categoria,

        prioridade=prioridade,

        status="Aberto",

        requester_id=(
            current_user.id
        )
    )


    db.add(
        ticket
    )

    # Precisamos do ID antes do commit.
    db.flush()


    # =====================================================
    # NOTIFICA O SOLICITANTE
    # =====================================================

    create_notification(

        db=db,

        user_id=current_user.id,

        titulo="Chamado aberto",

        mensagem=(
            f"Seu chamado #{ticket.id} "
            f"foi registrado com sucesso."
        ),

        tipo="Chamado",

        link=f"/tickets/{ticket.id}"
    )


    # =====================================================
    # NOTIFICA TODOS OS USUÁRIOS DE SUPORTE
    # =====================================================

    support_users = (
        db.query(User)
        .filter(
            func.lower(
                User.tipo
            )
            == "suporte"
        )
        .all()
    )


    for support in support_users:

        # Caso o próprio Suporte abra chamado,
        # evita notificação duplicada.

        if (
            support.id
            == current_user.id
        ):

            continue


        create_notification(

            db=db,

            user_id=support.id,

            titulo="Novo chamado",

            mensagem=(
                f"Novo chamado #{ticket.id}: "
                f"{ticket.titulo}"
            ),

            tipo="Chamado",

            link=f"/tickets/{ticket.id}"
        )


    db.commit()

    db.refresh(
        ticket
    )

    return ticket


# =========================================================
# CHAMADOS DO PRÓPRIO USUÁRIO
# =========================================================

def get_user_tickets(

    db: Session,

    user_id: int

):

    return (
        db.query(Ticket)
        .filter(
            Ticket.requester_id
            == user_id
        )
        .order_by(
            Ticket.id.desc()
        )
        .all()
    )


# =========================================================
# FILA DO SUPORTE
# =========================================================

def get_support_tickets(
    db: Session
):

    return (
        db.query(Ticket)
        .order_by(
            Ticket.id.desc()
        )
        .all()
    )


# =========================================================
# CONTADOR DE PENDÊNCIAS DO SUPORTE
#
# Outro badge vermelho para o frontend.
# =========================================================

def get_pending_ticket_count(
    db: Session
):

    return (
        db.query(Ticket)
        .filter(
            Ticket.status.in_(
                [
                    "Aberto",
                    "Em análise"
                ]
            )
        )
        .count()
    )


# =========================================================
# ALTERAR STATUS
#
# Somente Suporte.
# =========================================================

def update_ticket_status(

    db: Session,

    ticket_id: int,

    support_user,

    data

):

    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id
            == ticket_id
        )
        .first()
    )


    if not ticket:

        raise HTTPException(
            status_code=404,
            detail="Chamado não encontrado."
        )


    novo_status = normalize_status(
        data.status
    )


    # -----------------------------------------------------
    # PARA RESOLVER, PRECISA INFORMAR SOLUÇÃO
    # -----------------------------------------------------

    if (
        novo_status
        == "Resolvido"
    ):

        solucao = (
            data.solucao
            or ""
        ).strip()


        if not solucao:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Informe a solução antes "
                    "de marcar o chamado como resolvido."
                )
            )


        ticket.solucao = (
            solucao
        )


    elif data.solucao:

        ticket.solucao = (
            data.solucao.strip()
        )


    ticket.status = (
        novo_status
    )


    # O último Suporte que movimentou
    # o chamado fica como responsável.

    ticket.assigned_support_id = (
        support_user.id
    )


    # =====================================================
    # NOTIFICA QUEM ABRIU
    # =====================================================

    create_notification(

        db=db,

        user_id=(
            ticket.requester_id
        ),

        titulo=(
            "Chamado atualizado"
        ),

        mensagem=(
            f"O chamado #{ticket.id} "
            f"agora está com status: "
            f"{ticket.status}."
        ),

        tipo="Chamado",

        link=f"/tickets/{ticket.id}"
    )


    db.commit()

    db.refresh(
        ticket
    )

    return ticket