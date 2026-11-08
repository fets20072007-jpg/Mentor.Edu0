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
# CADASTRO DE USUÁRIOS
#
# SUPORTE:
# - Administração
# - Professor
# - Aluno
#
# ADMINISTRAÇÃO:
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
        "administração"
    ]

    if tipo_novo not in tipos_validos:

        raise HTTPException(
            status_code=400,
            detail="Tipo de usuário inválido."
        )


    # =====================================================
    # PERMISSÕES DE CADASTRO
    # =====================================================

    if tipo_atual == "suporte":

        # Suporte pode cadastrar:
        # - Administração
        # - Professor
        # - Aluno

        pass


    elif tipo_atual in [
        "administracao",
        "administração"
    ]:

        # Administração não pode cadastrar
        # outra Administração.

        if tipo_novo in [
            "administracao",
            "administração"
        ]:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Somente o Suporte pode cadastrar "
                    "integrantes da Administração."
                )
            )


    else:

        raise HTTPException(
            status_code=403,
            detail=(
                "Usuário sem permissão "
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
            detail="E-mail é obrigatório."
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
            detail="E-mail já cadastrado."
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
                detail="Turma não encontrada."
            )


        if not classroom.ativa:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Não é possível cadastrar "
                    "o aluno em uma turma inativa."
                )
            )


    # =====================================================
    # PROFESSOR
    # VALIDA CAMPOS OBRIGATÓRIOS
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
                    "CPF é obrigatório "
                    "para professores."
                )
            )


        # -------------------------------------------------
        # MATRÍCULA
        # -------------------------------------------------

        if not matricula_normalizada:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Matrícula é obrigatória "
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
                    "Especialidade é obrigatória "
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
                    "Já existe um professor "
                    "com este CPF."
                )
            )


        # -------------------------------------------------
        # MATRÍCULA DUPLICADA
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
                    "Já existe um professor "
                    "com esta matrícula."
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
                    "Já existe um professor "
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
    # TRANSAÇÃO ÚNICA
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
        # Gera o ID do usuário sem fazer commit.
        #
        # Assim podemos criar:
        #
        # Aluno:
        # User + Enrollment
        #
        # Professor:
        # User + Teacher
        #
        # na mesma transação.
        # -------------------------------------------------

        db.flush()


        # =================================================
        # ALUNO
        # CRIA MATRÍCULA AUTOMATICAMENTE
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
        # COMMIT ÚNICO
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
                "Não foi possível concluir o cadastro. "
                "Verifique se e-mail, CPF ou matrícula "
                "já estão cadastrados."
            )
        )


    # =====================================================
    # OUTROS ERROS
    # =====================================================

    except Exception:

        db.rollback()

        raise


# =========================================================
# LISTAGEM DE USUÁRIOS
# ADMINISTRAÇÃO / SUPORTE
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
# PERFIL DO USUÁRIO AUTENTICADO
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
# ATUALIZAR PRÓPRIO PERFIL
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
                detail="E-mail inválido."
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
                detail="E-mail já cadastrado."
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
# EXCLUSÃO DA PRÓPRIA CONTA
#
# OBSERVAÇÃO:
# Posteriormente será substituída por
# desativação institucional.
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

    db.delete(
        current_user
    )

    db.commit()

    return {
        "message":
            "Usuário deletado com sucesso."
    }