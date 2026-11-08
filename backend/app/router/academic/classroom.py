from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

import re
import unicodedata

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    User,
    Teacher,
    Classroom,
    Subject
)

from app.schema.classroom import (
    ClassroomCreate,
    ClassroomDTUpdate,
    ClassroomResponse
)

from app.services.academic.classroom_service import (
    create_classroom,
    get_classrooms
)

from app.core.permissions import (
    require_admin
)

from app.services.user.teacher_service import (
    get_classroom_teachers
)

from app.schema.teacher import (
    ClassroomTeacherResponse
)

router = APIRouter(
    prefix="/classrooms",
    tags=["Classrooms"]
)


# =========================================================
# NORMALIZA NOME DA TURMA
# =========================================================

def normalizar_nome_turma(
    nome: str
) -> str:

    nome = (
        nome
        or ""
    ).lower().strip()

    nome = unicodedata.normalize(
        "NFKD",
        nome
    )

    nome = "".join(
        c
        for c in nome
        if not unicodedata.combining(c)
    )

    nome = (
        nome
        .replace("º", "")
        .replace("ª", "")
    )

    nome = re.sub(
        r"\b(ano|serie|turma)\b",
        "",
        nome
    )

    nome = re.sub(
        r"[^a-z0-9]",
        "",
        nome
    )

    return nome


# =========================================================
# ADMINISTRAÇÃO
# CRIAR TURMA
# =========================================================

@router.post(
    "",
    response_model=ClassroomResponse
)
def register_classroom(

    classroom: ClassroomCreate,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    nome_normalizado = (
        normalizar_nome_turma(
            classroom.nome
        )
    )

    turmas_existentes = (
        db.query(Classroom)
        .filter(
            Classroom.ano
            == classroom.ano,

            Classroom.turno
            == classroom.turno
        )
        .all()
    )

    for turma_existente in (
        turmas_existentes
    ):

        if (
            normalizar_nome_turma(
                turma_existente.nome
            )
            == nome_normalizado
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Esta turma já está "
                    "cadastrada para este "
                    "ano e turno."
                )
            )

    return create_classroom(
        db,
        classroom
    )


# =========================================================
# ADMINISTRAÇÃO
# LISTAR TURMAS
# =========================================================

@router.get(
    "",
    response_model=list[
        ClassroomResponse
    ]
)
def list_classrooms(

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_classrooms(
        db
    )


# =========================================================
# ADMINISTRAÇÃO
# DEFINIR OU REMOVER DIRETOR DE TURMA
#
# teacher_id:
# - número = define DT
# - null = remove DT
# =========================================================

@router.patch(
    "/{classroom_id}/dt",
    response_model=ClassroomResponse
)
def update_classroom_dt(

    classroom_id: int,

    data: ClassroomDTUpdate,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id
            == classroom_id
        )
        .first()
    )

    if not classroom:

        raise HTTPException(
            status_code=404,
            detail="Turma não encontrada."
        )


    # =====================================================
    # REMOVER DT
    # =====================================================

    if data.teacher_id is None:

        classroom.teacher_id = None

        db.commit()

        db.refresh(
            classroom
        )

        return classroom


    # =====================================================
    # CONFIRMA PROFESSOR
    # =====================================================

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.id
            == data.teacher_id
        )
        .first()
    )

    if not teacher:

        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado."
        )

    if not teacher.ativo:

        raise HTTPException(
            status_code=400,
            detail=(
                "Professor inativo não pode "
                "ser Diretor de Turma."
            )
        )


    # =====================================================
    # PROFESSOR PRECISA ATUAR NA TURMA
    #
    # A atuação é definida pelas disciplinas.
    # =====================================================

    subject = (
        db.query(Subject)
        .filter(
            Subject.teacher_id
            == teacher.id,

            Subject.classroom_id
            == classroom.id,

            Subject.ativa
            == True
        )
        .first()
    )

    if not subject:

        raise HTTPException(
            status_code=400,
            detail=(
                "O professor precisa lecionar "
                "ao menos uma disciplina nesta "
                "turma antes de ser definido "
                "como Diretor de Turma."
            )
        )


    # =====================================================
    # DEFINE DT
    #
    # Como Classroom possui apenas um teacher_id,
    # cada turma possui no máximo um DT.
    # =====================================================

    classroom.teacher_id = (
        teacher.id
    )

    db.commit()

    db.refresh(
        classroom
    )

    return classroom

# =========================================================
# ADMINISTRAÇÃO
# PROFESSORES QUE ATUAM EM UMA TURMA
# =========================================================

@router.get(
    "/{classroom_id}/teachers",
    response_model=list[
        ClassroomTeacherResponse
    ]
)
def classroom_teachers(

    classroom_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_classroom_teachers(
        db,
        classroom_id
    )