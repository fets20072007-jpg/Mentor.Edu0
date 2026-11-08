from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.database.models import (
    User,
    Teacher,
    Classroom,
    Subject,
    Enrollment
)

from app.schema.subject import (
    SubjectCreate,
    SubjectResponse,
    SubjectTeacherUpdate
)

from app.security.auth import get_current_user

from app.core.permissions import (
    require_admin
)


router = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)


# =========================================================
# AUXILIAR
# NORMALIZA NOME DA DISCIPLINA
# =========================================================

def normalize_subject_name(nome: str) -> str:

    return (
        " ".join(
            nome.strip().split()
        )
        .casefold()
    )


# =========================================================
# ADMINISTRAÇÃO
# CRIAR DISCIPLINA
#
# REGRA:
# Uma disciplina pode existir somente uma vez por turma.
#
# O mesmo professor pode lecionar várias disciplinas
# diferentes na mesma turma.
# =========================================================

@router.post(
    "",
    response_model=SubjectResponse
)
def register_subject(

    subject: SubjectCreate,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    # -----------------------------------------------------
    # VERIFICA PROFESSOR
    # -----------------------------------------------------

    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.id
            == subject.teacher_id
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
                "receber disciplinas."
            )
        )


    # -----------------------------------------------------
    # VERIFICA TURMA
    # -----------------------------------------------------

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id
            == subject.classroom_id
        )
        .first()
    )

    if not classroom:

        raise HTTPException(
            status_code=404,
            detail="Turma não encontrada."
        )

    if not classroom.ativa:

        raise HTTPException(
            status_code=400,
            detail=(
                "Não é possível cadastrar "
                "disciplinas em uma turma inativa."
            )
        )


    # -----------------------------------------------------
    # NORMALIZA NOME
    # -----------------------------------------------------

    nome_limpo = (
        " ".join(
            subject.nome.strip().split()
        )
    )

    if not nome_limpo:

        raise HTTPException(
            status_code=400,
            detail=(
                "O nome da disciplina "
                "não pode estar vazio."
            )
        )

    nome_normalizado = (
        normalize_subject_name(
            nome_limpo
        )
    )


    # =====================================================
    # IMPEDE A MESMA DISCIPLINA DUAS VEZES NA TURMA
    #
    # PERMITIDO:
    #
    # 3A
    # Matemática       -> Professor Carlos
    # Formação Cidadã  -> Professor Carlos
    # Programação      -> Professor Carlos
    #
    # BLOQUEADO:
    #
    # 3A
    # Matemática       -> Professor Carlos
    # Matemática       -> Professor João
    # =====================================================

    subjects_classroom = (
        db.query(Subject)
        .filter(
            Subject.classroom_id
            == classroom.id,

            Subject.ativa
            == True
        )
        .all()
    )

    for existing_subject in subjects_classroom:

        existing_name = (
            normalize_subject_name(
                existing_subject.nome
            )
        )

        if (
            existing_name
            == nome_normalizado
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Esta disciplina já está "
                    "cadastrada nesta turma. "
                    "Se deseja trocar o professor, "
                    "altere o professor responsável "
                    "pela disciplina existente."
                )
            )


    # -----------------------------------------------------
    # CRIA DISCIPLINA
    # -----------------------------------------------------

    new_subject = Subject(

        nome=nome_limpo,

        carga_horaria=(
            subject.carga_horaria
        ),

        descricao=(
            subject.descricao
        ),

        teacher_id=(
            teacher.id
        ),

        classroom_id=(
            classroom.id
        ),

        ativa=True
    )

    db.add(
        new_subject
    )

    db.commit()

    db.refresh(
        new_subject
    )

    return new_subject


# =========================================================
# ADMINISTRAÇÃO
# LISTAR TODAS AS DISCIPLINAS
# =========================================================

@router.get(
    "",
    response_model=list[
        SubjectResponse
    ]
)
def list_subjects(

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return (
        db.query(Subject)
        .order_by(
            Subject.nome.asc()
        )
        .all()
    )


# =========================================================
# PROFESSOR / ALUNO / ADMINISTRAÇÃO
# MINHAS DISCIPLINAS
# =========================================================

@router.get(
    "/me",
    response_model=list[
        SubjectResponse
    ]
)
def my_subjects(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()


    # =====================================================
    # PROFESSOR
    #
    # Vê somente suas disciplinas ativas.
    # Pode possuir várias disciplinas na mesma turma.
    # =====================================================

    if tipo == "professor":

        teacher = (
            db.query(Teacher)
            .filter(
                Teacher.user_id
                == current_user.id
            )
            .first()
        )

        if not teacher:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Perfil de professor "
                    "não encontrado."
                )
            )

        return (
            db.query(Subject)
            .filter(
                Subject.teacher_id
                == teacher.id,

                Subject.ativa
                == True
            )
            .order_by(
                Subject.nome.asc()
            )
            .all()
        )


    # =====================================================
    # ALUNO
    #
    # O aluno NÃO possui vínculo individual
    # com disciplinas.
    #
    # Ele possui:
    #
    # Aluno
    #   ↓
    # Matrícula ativa
    #   ↓
    # Turma
    #   ↓
    # Todas as disciplinas da turma
    # =====================================================

    if tipo == "aluno":

        enrollment = (
            db.query(Enrollment)
            .filter(
                Enrollment.user_id
                == current_user.id,

                Enrollment.ativo
                == True
            )
            .first()
        )

        if not enrollment:

            return []

        return (
            db.query(Subject)
            .filter(
                Subject.classroom_id
                == enrollment.classroom_id,

                Subject.ativa
                == True
            )
            .order_by(
                Subject.nome.asc()
            )
            .all()
        )


    # =====================================================
    # ADMINISTRAÇÃO
    # =====================================================

    if tipo in [
        "administracao",
        "administração"
    ]:

        return (
            db.query(Subject)
            .order_by(
                Subject.nome.asc()
            )
            .all()
        )


    raise HTTPException(
        status_code=403,
        detail=(
            "Usuário sem permissão "
            "para acessar disciplinas."
        )
    )


# =========================================================
# PROFESSOR / ALUNO / ADMINISTRAÇÃO
# VER UMA DISCIPLINA
# =========================================================

@router.get(
    "/me/{subject_id}",
    response_model=SubjectResponse
)
def my_subject_by_id(

    subject_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()

    subject = (
        db.query(Subject)
        .filter(
            Subject.id == subject_id
        )
        .first()
    )

    if not subject:

        raise HTTPException(
            status_code=404,
            detail="Disciplina não encontrada."
        )


    # -----------------------------------------------------
    # PROFESSOR
    # -----------------------------------------------------

    if tipo == "professor":

        teacher = (
            db.query(Teacher)
            .filter(
                Teacher.user_id
                == current_user.id
            )
            .first()
        )

        if not teacher:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Perfil de professor "
                    "não encontrado."
                )
            )

        if (
            subject.teacher_id
            != teacher.id
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "Esta disciplina não "
                    "pertence a este professor."
                )
            )

        return subject


    # -----------------------------------------------------
    # ALUNO
    # -----------------------------------------------------

    if tipo == "aluno":

        enrollment = (
            db.query(Enrollment)
            .filter(
                Enrollment.user_id
                == current_user.id,

                Enrollment.ativo
                == True
            )
            .first()
        )

        if (
            not enrollment
            or subject.classroom_id
            != enrollment.classroom_id
            or not subject.ativa
        ):

            raise HTTPException(
                status_code=403,
                detail=(
                    "Esta disciplina não pertence "
                    "à turma do aluno."
                )
            )

        return subject


    # -----------------------------------------------------
    # ADMINISTRAÇÃO
    # -----------------------------------------------------

    if tipo in [
        "administracao",
        "administração"
    ]:

        return subject


    raise HTTPException(
        status_code=403,
        detail=(
            "Usuário sem permissão "
            "para acessar esta disciplina."
        )
    )


# =========================================================
# ADMINISTRAÇÃO
# TROCAR PROFESSOR RESPONSÁVEL PELA DISCIPLINA
# =========================================================

@router.patch(
    "/{subject_id}/teacher",
    response_model=SubjectResponse
)
def change_subject_teacher(

    subject_id: int,

    data: SubjectTeacherUpdate,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    # -----------------------------------------------------
    # DISCIPLINA
    # -----------------------------------------------------

    subject = (
        db.query(Subject)
        .filter(
            Subject.id
            == subject_id
        )
        .first()
    )

    if not subject:

        raise HTTPException(
            status_code=404,
            detail="Disciplina não encontrada."
        )


    # -----------------------------------------------------
    # PROFESSOR DESTINO
    # -----------------------------------------------------

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
                "receber disciplinas."
            )
        )


    # -----------------------------------------------------
    # JÁ É O PROFESSOR DA DISCIPLINA
    # -----------------------------------------------------

    if (
        subject.teacher_id
        == teacher.id
    ):

        return subject


    # =====================================================
    # PROTEÇÃO CONTRA DUPLICIDADE LEGADA
    #
    # Normalmente não deveria existir outra disciplina
    # com mesmo nome na mesma turma.
    #
    # Porém existem dados antigos no banco.
    # =====================================================

    other_subjects = (
        db.query(Subject)
        .filter(
            Subject.id != subject.id,

            Subject.classroom_id
            == subject.classroom_id,

            Subject.ativa == True
        )
        .all()
    )

    subject_name = (
        normalize_subject_name(
            subject.nome
        )
    )

    for other_subject in other_subjects:

        if (
            normalize_subject_name(
                other_subject.nome
            )
            == subject_name
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Existe outra disciplina ativa "
                    "com o mesmo nome nesta turma. "
                    "Há dados antigos duplicados "
                    "que precisam ser corrigidos "
                    "antes da troca do professor."
                )
            )


    # =====================================================
    # REGRA DO DIRETOR DE TURMA
    #
    # Se o professor atual é DT, ele precisa continuar
    # lecionando pelo menos uma disciplina naquela turma.
    # =====================================================

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id
            == subject.classroom_id
        )
        .first()
    )

    old_teacher_id = (
        subject.teacher_id
    )

    if (
        classroom
        and classroom.teacher_id
        == old_teacher_id
        and old_teacher_id
        != teacher.id
    ):

        other_subject = (
            db.query(Subject)
            .filter(
                Subject.id
                != subject.id,

                Subject.teacher_id
                == old_teacher_id,

                Subject.classroom_id
                == subject.classroom_id,

                Subject.ativa
                == True
            )
            .first()
        )

        if not other_subject:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Este professor é Diretor de Turma "
                    "e esta é sua última disciplina ativa "
                    "na turma. Troque ou remova o DT "
                    "antes de transferir a disciplina."
                )
            )


    # -----------------------------------------------------
    # TROCA PROFESSOR
    # -----------------------------------------------------

    subject.teacher_id = (
        teacher.id
    )

    db.commit()

    db.refresh(
        subject
    )

    return subject