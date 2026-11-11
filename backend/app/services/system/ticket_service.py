import unicodedata

from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import (
    Ticket,
    User,
    Teacher,
    Subject,
    Enrollment
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

def _recipient_user_for_ticket(db: Session, current_user, data):
    perfil = (getattr(data, "destinatario_perfil", None) or "Suporte").strip()
    recipient_id = getattr(data, "destinatario_user_id", None)

    if recipient_id is None:
        return perfil, None, perfil

    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Destinatário não encontrado.")

    recipient_type = normalize_text(recipient.tipo)
    target = normalize_text(perfil)
    allowed_types = {
        "professor": {"professor"},
        "suporte": {"suporte"},
        "administracao": {"administracao", "admin"},
        "admin": {"administracao", "admin"},
    }
    if target in allowed_types and recipient_type not in allowed_types[target]:
        raise HTTPException(status_code=400, detail="O usuário escolhido não pertence ao perfil selecionado.")

    # Aluno só pode direcionar chamado a professores que lecionam para sua turma.
    if normalize_text(current_user.tipo) == "aluno" and target == "professor":
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id,
            Enrollment.ativo == True
        ).first()
        if not enrollment:
            raise HTTPException(status_code=400, detail="Aluno sem matrícula ativa.")
        teacher = db.query(Teacher).filter(Teacher.user_id == recipient.id).first()
        teaches_student = False
        if teacher:
            teaches_student = db.query(Subject).filter(
                Subject.classroom_id == enrollment.classroom_id,
                Subject.teacher_id == teacher.id,
                Subject.ativa == True
            ).first() is not None
        if not teaches_student:
            raise HTTPException(status_code=403, detail="Este professor não leciona para o aluno.")

    return perfil, recipient, recipient.nome


def create_ticket(db: Session, current_user, data):
    titulo = (data.titulo or "").strip()
    descricao = (data.descricao or "").strip()
    categoria = (data.categoria or "Sistema").strip()
    if not titulo:
        raise HTTPException(status_code=400, detail="O título do chamado é obrigatório.")
    if not descricao:
        raise HTTPException(status_code=400, detail="A descrição do chamado é obrigatória.")

    prioridade = normalize_priority(data.prioridade)
    perfil, recipient, recipient_name = _recipient_user_for_ticket(db, current_user, data)

    ticket = Ticket(
        titulo=titulo,
        descricao=descricao,
        categoria=categoria,
        prioridade=prioridade,
        status="Aberto",
        destinatario_perfil=perfil,
        destinatario_user_id=recipient.id if recipient else None,
        destinatario_nome=recipient_name,
        requester_id=current_user.id
    )
    db.add(ticket)
    db.flush()

    create_notification(
        db=db, user_id=current_user.id, titulo="Chamado aberto",
        mensagem=f"Seu chamado #{ticket.id} foi registrado para {recipient_name}.",
        tipo="Chamado", link=f"/tickets/{ticket.id}"
    )

    if recipient:
        targets = [recipient]
    else:
        target_role = normalize_text(perfil)
        type_options = {
            "suporte": ["suporte"],
            "professor": ["professor"],
            "administracao": ["administracao", "admin"],
            "admin": ["administracao", "admin"],
        }.get(target_role, ["suporte"])
        targets = db.query(User).filter(func.lower(User.tipo).in_(type_options)).all()

    for target in targets:
        if target.id == current_user.id:
            continue
        create_notification(
            db=db, user_id=target.id, titulo="Novo chamado",
            mensagem=f"Novo chamado #{ticket.id}: {ticket.titulo}",
            tipo="Chamado", link=f"/tickets/{ticket.id}"
        )

    db.commit()
    db.refresh(ticket)
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


def get_user_inbox(db: Session, user_id: int):
    return (
        db.query(Ticket)
        .filter(Ticket.destinatario_user_id == user_id)
        .order_by(Ticket.id.desc())
        .all()
    )


def get_ticket_recipients(db: Session, current_user):
    result = []
    user_type = normalize_text(current_user.tipo)

    if user_type == "aluno":
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == current_user.id, Enrollment.ativo == True
        ).first()
        if enrollment:
            rows = (
                db.query(Teacher, Subject)
                .join(Subject, Subject.teacher_id == Teacher.id)
                .filter(
                    Subject.classroom_id == enrollment.classroom_id,
                    Subject.ativa == True,
                    Teacher.ativo == True
                )
                .order_by(Teacher.nome.asc(), Subject.nome.asc())
                .all()
            )
            grouped = {}
            for teacher, subject in rows:
                item = grouped.setdefault(teacher.user_id, {
                    "perfil": "Professor",
                    "user_id": teacher.user_id,
                    "nome": teacher.nome,
                    "subjects": []
                })
                item["subjects"].append(subject.nome)
            for item in grouped.values():
                result.append({
                    "perfil": item["perfil"],
                    "user_id": item["user_id"],
                    "nome": item["nome"],
                    "detalhe": ", ".join(item["subjects"])
                })

    for role_label, types in [("Suporte", ["suporte"]), ("Administração", ["administracao", "admin"])]:
        users = db.query(User).filter(func.lower(User.tipo).in_(types)).order_by(User.nome.asc()).all()
        for user in users:
            result.append({
                "perfil": role_label,
                "user_id": user.id,
                "nome": user.nome,
                "detalhe": user.email
            })

    return result


# =========================================================
# FILA DO SUPORTE
# =========================================================

def get_support_tickets(
    db: Session
):

    return (
        db.query(Ticket)
        .filter(func.lower(Ticket.destinatario_perfil) == "suporte")
        .order_by(Ticket.id.desc())
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
            func.lower(Ticket.destinatario_perfil) == "suporte",
            Ticket.status.in_(["Aberto", "Em análise"])
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