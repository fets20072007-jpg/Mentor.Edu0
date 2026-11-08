from datetime import date, datetime, time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import Assessment


def get_admin_assessments(
    db: Session,
    titulo: str | None = None,
    teacher_id: int | None = None,
    classroom_id: int | None = None,
    subject_id: int | None = None,
    tipo: str | None = None,
    semestre: int | None = None,
    ano_letivo: int | None = None,
    ativa: bool | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    ordem: str = "mais_recentes"
):
    query = db.query(Assessment)

    # Pesquisa pelo título
    if titulo:
        query = query.filter(
            Assessment.titulo.ilike(
                f"%{titulo.strip()}%"
            )
        )

    # Professor
    if teacher_id is not None:
        query = query.filter(
            Assessment.teacher_id == teacher_id
        )

    # Turma
    if classroom_id is not None:
        query = query.filter(
            Assessment.classroom_id == classroom_id
        )

    # Disciplina
    if subject_id is not None:
        query = query.filter(
            Assessment.subject_id == subject_id
        )

    # Tipo de avaliação
    if tipo:
        query = query.filter(
            Assessment.tipo.ilike(
                f"%{tipo.strip()}%"
            )
        )

    # Semestre
    if semestre is not None:
        query = query.filter(
            Assessment.semestre == semestre
        )

    # Ano letivo
    if ano_letivo is not None:
        query = query.filter(
            Assessment.ano_letivo == ano_letivo
        )

    # Ativa / inativa
    if ativa is not None:
        query = query.filter(
            Assessment.ativa == ativa
        )

    # Data inicial
    if data_inicio is not None:
        inicio = datetime.combine(
            data_inicio,
            time.min
        )

        query = query.filter(
            Assessment.data >= inicio
        )

    # Data final
    if data_fim is not None:
        fim = datetime.combine(
            data_fim,
            time.max
        )

        query = query.filter(
            Assessment.data <= fim
        )

    # Ordenação
    if ordem == "mais_antigas":
        query = query.order_by(
            Assessment.data.asc()
        )

    elif ordem == "titulo":
        query = query.order_by(
            Assessment.titulo.asc()
        )

    else:
        query = query.order_by(
            Assessment.data.desc()
        )

    assessments = query.all()

    return [
        {
            "assessment_id": assessment.id,
            "titulo": assessment.titulo,
            "descricao": assessment.descricao,
            "tipo": assessment.tipo,
            "data": assessment.data,
            "valor": assessment.valor,
            "ativa": assessment.ativa,
            "semestre": assessment.semestre,
            "ano_letivo": assessment.ano_letivo,
            "teacher_id": assessment.teacher_id,
            "classroom_id": assessment.classroom_id,
            "subject_id": assessment.subject_id
        }
        for assessment in assessments
    ]


def get_admin_assessment_by_id(
    db: Session,
    assessment_id: int
):
    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação não encontrada."
        )

    return {
        "assessment_id":
            assessment.id,

        "titulo":
            assessment.titulo,

        "descricao":
            assessment.descricao,

        "tipo":
            assessment.tipo,

        "data":
            assessment.data,

        "valor":
            assessment.valor,

        "ativa":
            assessment.ativa,

        "semestre":
            assessment.semestre,

        "ano_letivo":
            assessment.ano_letivo,

        "teacher_id":
            assessment.teacher_id,

        "classroom_id":
            assessment.classroom_id,

        "subject_id":
            assessment.subject_id
    }