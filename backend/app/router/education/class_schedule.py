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

from app.schema.class_schedule import (
    ClassScheduleCreate,
    ClassScheduleUpdate,
    ClassScheduleResponse
)

from app.security.auth import (
    get_current_user
)

from app.core.permissions import (
    require_admin
)

from app.services.education.class_schedule_service import (
    create_schedule,
    get_all_schedules,
    get_classroom_schedules,
    get_my_schedules,
    update_schedule,
    deactivate_schedule
)


router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"]
)


# =========================================================
# ADMINISTRACAO
# CRIAR HORARIO
# =========================================================

@router.post(
    "",
    response_model=ClassScheduleResponse
)
def register_schedule(

    data: ClassScheduleCreate,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return create_schedule(
        db=db,
        data=data
    )


# =========================================================
# ADMINISTRACAO
# LISTAR TODOS
# =========================================================

@router.get(
    "",
    response_model=list[
        ClassScheduleResponse
    ]
)
def list_schedules(

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_all_schedules(
        db
    )


# =========================================================
# USUARIO
# MEUS HORARIOS
# =========================================================

@router.get(
    "/me",
    response_model=list[
        ClassScheduleResponse
    ]
)
def my_schedules(

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_my_schedules(

        db=db,

        current_user=current_user
    )


# =========================================================
# ADMINISTRACAO
# HORARIOS DE UMA TURMA
# =========================================================

@router.get(
    "/classroom/{classroom_id}",
    response_model=list[
        ClassScheduleResponse
    ]
)
def classroom_schedules(

    classroom_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return get_classroom_schedules(

        db=db,

        classroom_id=classroom_id
    )


# =========================================================
# ADMINISTRACAO
# ATUALIZAR
# =========================================================

@router.patch(
    "/{schedule_id}",
    response_model=ClassScheduleResponse
)
def edit_schedule(

    schedule_id: int,

    data: ClassScheduleUpdate,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return update_schedule(

        db=db,

        schedule_id=schedule_id,

        data=data
    )


# =========================================================
# ADMINISTRACAO
# DESATIVAR
# =========================================================

@router.delete(
    "/{schedule_id}"
)
def delete_schedule(

    schedule_id: int,

    current_user: User = Depends(
        require_admin
    ),

    db: Session = Depends(
        get_db
    )

):

    return deactivate_schedule(

        db=db,

        schedule_id=schedule_id
    )