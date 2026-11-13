from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.dependencies import get_db

from app.database.models import (
    User,
    Teacher,
    Classroom,
    Enrollment
)

from app.schema.users import (
    UserCreate,
    UserResponse,
    UserUpdate
)

from app.core.security import hash_password

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_admin_or_support
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================================================
# CADASTRO DE USUÃRIOS
#
# SUPORTE:
# - AdministraÃ§Ã£o
# - Professor
# - Aluno
#
# ADMINISTRAÃ‡ÃƒO:
# - Professor
# - Aluno
#
# Professor:
# - cria User
# - cria Teacher automaticamente
#
# Aluno:
# - cria User
# - cria Enrollment automaticamente
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse
)
def register_user(

    user: UserCreate,

    current_user: User = Depends(
        require_admin_or_support
    ),

    db: Session = Depends(
        get_db
    )

):

    # =====================================================
    # NORMALIZA TIPOS
    # =====================================================

    tipo_novo = (
        user.tipo
        or ""
    ).strip().lower()

    tipo_atual = (
        current_user.tipo
        or ""
    ).strip().lower()


    # =====================================================
    # TIPOS PERMITIDOS
    # =====================================================

    tipos_validos = [
        "aluno",
        "professor",
        "administracao",
        "administraÃ§Ã£o"
    ]

    if tipo_novo not in tipos_validos:

        raise HTTPException(
            status_code=400,
            detail="Tipo de usuÃ¡rio invÃ¡lido."
        )


    # =====================================================
    # PERMISSÃ•ES DE CADASTRO
    # =====================================================

    if tipo_atual == "suporte":

        # Suporte pode cadastrar:
        # - AdministraÃ§Ã£o
        # - Professor
        # - Aluno

        pass


    elif tipo_atual in [
        "administracao",
        "administraÃ§Ã£o"
    ]:

        # AdministraÃ§Ã£o nÃ£o pode cadastrar
        # outra AdministraÃ§Ã£o.

        if tipo_novo in [
            "administracao",
            "administraÃ§Ã£o"
        ]:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Somente o Suporte pode cadastrar "
                    "integrantes da AdministraÃ§Ã£o."
                )
            )


    else:

        raise HTTPException(
            status_code=403,
            detail=(
                "UsuÃ¡rio sem permissÃ£o "
                "para realizar cadastros."
            )
        )


    # =====================================================
    # NORMALIZA E-MAIL
    # =====================================================

    email_normalizado = (
        user.email
        or ""
    ).strip().lower()

    if not email_normalizado:

        raise HTTPException(
            status_code=400,
            detail="E-mail Ã© obrigatÃ³rio."
        )


    # =====================================================
    # VERIFICA E-MAIL DUPLICADO
    # =====================================================

    usuario_existente = (
        db.query(User)
        .filter(
            User.email == email_normalizado
        )
        .first()
    )

    if usuario_existente:

        raise HTTPException(
            status_code=400,
            detail="E-mail jÃ¡ cadastrado."
        )


    # =====================================================
    # PADRONIZA TIPO SALVO
    # =====================================================

    if tipo_novo == "aluno":

        tipo_salvo = "Aluno"


    elif tipo_novo == "professor":

        tipo_salvo = "Professor"


    else:

        tipo_salvo = "Administracao"


    # =====================================================
    # ALUNO
    # VALIDA TURMA
    # =====================================================

    classroom = None

    if tipo_novo == "aluno":

        if user.classroom_id is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Aluno deve estar "
                    "vinculado a uma turma."
                )
            )


        classroom = (
            db.query(Classroom)
            .filter(
                Classroom.id
                == user.classroom_id
            )
            .first()
        )


        if not classroom:

            raise HTTPException(
                status_code=404,
                detail="Turma nÃ£o encontrada."
            )


        if not classroom.ativa:

            raise HTTPException(
                status_code=400,
                detail=(
                    "NÃ£o Ã© possÃ­vel cadastrar "
                    "o aluno em uma turma inativa."
                )
            )


    # =====================================================
    # PROFESSOR
    # VALIDA CAMPOS OBRIGATÃ“RIOS
    # =====================================================

    cpf_normalizado = None
    matricula_normalizada = None
    especialidade_normalizada = None


    if tipo_novo == "professor":

        cpf_normalizado = (
            user.cpf
            or ""
        ).strip()


        matricula_normalizada = (
            user.matricula
            or ""
        ).strip()


        especialidade_normalizada = (
            user.especialidade
            or ""
        ).strip()


        # -------------------------------------------------
        # CPF
        # -------------------------------------------------

        if not cpf_normalizado:

            raise HTTPException(
                status_code=400,
                detail=(
                    "CPF Ã© obrigatÃ³rio "
                    "para professores."
                )
            )


        # -------------------------------------------------
        # MATRÃCULA
        # -------------------------------------------------

        if not matricula_normalizada:

            raise HTTPException(
                status_code=400,
                detail=(
                    "MatrÃ­cula Ã© obrigatÃ³ria "
                    "para professores."
                )
            )


        # -------------------------------------------------
        # ESPECIALIDADE
        # -------------------------------------------------

        if not especialidade_normalizada:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Especialidade Ã© obrigatÃ³ria "
                    "para professores."
                )
            )


        # -------------------------------------------------
        # CPF DUPLICADO
        # -------------------------------------------------

        professor_cpf = (
            db.query(Teacher)
            .filter(
                Teacher.cpf
                == cpf_normalizado
            )
            .first()
        )

        if professor_cpf:

            raise HTTPException(
                status_code=400,
                detail=(
                    "JÃ¡ existe um professor "
                    "com este CPF."
                )
            )


        # -------------------------------------------------
        # MATRÃCULA DUPLICADA
        # -------------------------------------------------

        professor_matricula = (
            db.query(Teacher)
            .filter(
                Teacher.matricula
                == matricula_normalizada
            )
            .first()
        )

        if professor_matricula:

            raise HTTPException(
                status_code=400,
                detail=(
                    "JÃ¡ existe um professor "
                    "com esta matrÃ­cula."
                )
            )


        # -------------------------------------------------
        # E-MAIL DUPLICADO EM TEACHERS
        # -------------------------------------------------

        professor_email = (
            db.query(Teacher)
            .filter(
                Teacher.email
                == email_normalizado
            )
            .first()
        )

        if professor_email:

            raise HTTPException(
                status_code=400,
                detail=(
                    "JÃ¡ existe um professor "
                    "com este e-mail."
                )
            )


    # =====================================================
    # SENHA
    # =====================================================

    hashed_password = hash_password(
        user.senha
    )


    # =====================================================
    # CRIA OBJETO USER
    # =====================================================

    novo_usuario = User(

        nome=user.nome,

        email=email_normalizado,

        senha=hashed_password,

        tipo=tipo_salvo,

        bio=user.bio,

        escola=user.escola,

        serie=user.serie,

        idade=user.idade,

        objetivo=user.objetivo,

        materias_favoritas=(
            user.materias_favoritas
        ),

        dificuldades=(
            user.dificuldades
        ),

        horas_estudo=(
            user.horas_estudo
        ),

        classroom_id=(
            classroom.id
            if tipo_novo == "aluno"
            else None
        )
    )


    # =====================================================
    # TRANSAÃ‡ÃƒO ÃšNICA
    # =====================================================

    try:

        # -------------------------------------------------
        # CRIA USER
        # -------------------------------------------------

        db.add(
            novo_usuario
        )


        # -------------------------------------------------
        # FLUSH
        #
        # Gera o ID do usuÃ¡rio sem fazer commit.
        #
        # Assim podemos criar:
        #
        # Aluno:
        # User + Enrollment
        #
        # Professor:
        # User + Teacher
        #
        # na mesma transaÃ§Ã£o.
        # -------------------------------------------------

        db.flush()


        # =================================================
        # ALUNO
        # CRIA MATRÃCULA AUTOMATICAMENTE
        # =================================================

        if tipo_novo == "aluno":

            nova_matricula = Enrollment(

                user_id=(
                    novo_usuario.id
                ),

                classroom_id=(
                    classroom.id
                ),

                ativo=True
            )

            db.add(
                nova_matricula
            )


        # =================================================
        # PROFESSOR
        # CRIA TEACHER AUTOMATICAMENTE
        # =================================================

        if tipo_novo == "professor":

            novo_professor = Teacher(

                user_id=(
                    novo_usuario.id
                ),

                nome=(
                    novo_usuario.nome
                ),

                email=(
                    novo_usuario.email
                ),

                cpf=(
                    cpf_normalizado
                ),

                matricula=(
                    matricula_normalizada
                ),

                telefone=(
                    user.telefone.strip()
                    if user.telefone
                    else None
                ),

                especialidade=(
                    especialidade_normalizada
                ),

                carga_horaria=(
                    user.carga_horaria
                    if user.carga_horaria
                    is not None
                    else 40
                ),

                ativo=True
            )

            db.add(
                novo_professor
            )


        # =================================================
        # COMMIT ÃšNICO
        # =================================================

        db.commit()

        db.refresh(
            novo_usuario
        )

        return novo_usuario


    # =====================================================
    # ERRO DE INTEGRIDADE
    # =====================================================

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=(
                "NÃ£o foi possÃ­vel concluir o cadastro. "
                "Verifique se e-mail, CPF ou matrÃ­cula "
                "jÃ¡ estÃ£o cadastrados."
            )
        )


    # =====================================================
    # OUTROS ERROS
    # =====================================================

    except Exception:

        db.rollback()

        raise


# =========================================================
# LISTAGEM DE USUÃRIOS
# ADMINISTRAÃ‡ÃƒO / SUPORTE
# =========================================================

@router.get(
    "/",
    response_model=list[
        UserResponse
    ]
)
def list_users(

    current_user: User = Depends(
        require_admin_or_support
    ),

    db: Session = Depends(
        get_db
    )

):

    return (
        db.query(User)
        .all()
    )


# =========================================================
# PERFIL DO USUÃRIO AUTENTICADO
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(

    current_user: User = Depends(
        get_current_user
    )

):

    return current_user


# =========================================================
# ATUALIZAR PRÃ“PRIO PERFIL
# =========================================================

@router.put(
    "/me",
    response_model=UserResponse
)
def update_me(

    user_update: UserUpdate,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    update_data = (
        user_update.model_dump(
            exclude_unset=True
        )
    )


    # =====================================================
    # CAMPOS PROTEGIDOS
    # =====================================================

    campos_protegidos = {
        "tipo",
        "id",
        "classroom_id",
        "cargo_administrativo"
    }


    for campo in campos_protegidos:

        update_data.pop(
            campo,
            None
        )


    # =====================================================
    # E-MAIL
    # =====================================================

    if "email" in update_data:

        novo_email = (
            update_data["email"]
            or ""
        ).strip().lower()


        if not novo_email:

            raise HTTPException(
                status_code=400,
                detail="E-mail invÃ¡lido."
            )


        usuario_existente = (
            db.query(User)
            .filter(
                User.email
                == novo_email,

                User.id
                != current_user.id
            )
            .first()
        )


        if usuario_existente:

            raise HTTPException(
                status_code=400,
                detail="E-mail jÃ¡ cadastrado."
            )


        update_data[
            "email"
        ] = novo_email


    # =====================================================
    # ATUALIZA CAMPOS
    # =====================================================

    for key, value in (
        update_data.items()
    ):

        setattr(
            current_user,
            key,
            value
        )


    db.commit()

    db.refresh(
        current_user
    )

    return current_user


# =========================================================
# EXCLUSÃƒO DA PRÃ“PRIA CONTA
#
# OBSERVAÃ‡ÃƒO:
# Posteriormente serÃ¡ substituÃ­da por
# desativaÃ§Ã£o institucional.
# =========================================================

@router.delete(
    "/me"
)
def delete_me(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    if current_user.ativo is False:

        return {
            "message":
                "Conta j? est? desativada."
        }


    current_user.ativo = False

    db.commit()

    db.refresh(
        current_user
    )


    return {
        "message":
            "Conta desativada com sucesso."
    }

