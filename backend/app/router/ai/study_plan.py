from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.database.models import StudyPlan, User

from app.schema.study_plan import (
    StudyPlanCreate,
    StudyPlanResponse,
    StudyPlanUpdate
)

from app.security.auth import get_current_user


router = APIRouter(
    prefix="/study-plans",
    tags=["Study Plans"]
)


@router.post(
    "/",
    response_model=StudyPlanResponse
)
def create_study_plan(
    plan: StudyPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    novo_plano = StudyPlan(
        titulo=plan.titulo,
        meta=plan.meta,
        horas_dia=plan.horas_dia,
        materias=plan.materias,
        dificuldade=plan.dificuldade,
        user_id=current_user.id
    )

    db.add(novo_plano)
    db.commit()
    db.refresh(novo_plano)

    return novo_plano


@router.get(
    "/me",
    response_model=list[StudyPlanResponse]
)
def get_my_study_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    planos = db.query(StudyPlan).filter(
        StudyPlan.user_id == current_user.id
    ).all()

    return planos


@router.put(
    "/{plan_id}",
    response_model=StudyPlanResponse
)
def update_study_plan(
    plan_id: int,
    plan_update: StudyPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plano = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()

    if not plano:
        raise HTTPException(
            status_code=404,
            detail="Plano de estudo não encontrado"
        )

    update_data = plan_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(plano, key, value)

    db.commit()
    db.refresh(plano)

    return plano


@router.delete("/{plan_id}")
def delete_study_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    plano = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()

    if not plano:
        raise HTTPException(
            status_code=404,
            detail="Plano de estudo não encontrado"
        )

    db.delete(plano)
    db.commit()

    return {
        "message": "Plano de estudo deletado com sucesso"
    }