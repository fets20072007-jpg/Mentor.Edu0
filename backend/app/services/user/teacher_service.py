from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import Teacher, User


def create_teacher(
    db: Session,
    user_id: int,
    teacher
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    if user.tipo != "Professor":
        raise HTTPException(
            status_code=403,
            detail="Apenas usuários do tipo Professor podem criar perfil de professor."
        )

    existing_teacher = (
        db.query(Teacher)
        .filter(Teacher.user_id == user_id)
        .first()
    )

    if existing_teacher:
        raise HTTPException(
            status_code=400,
            detail="Este usuário já possui perfil de professor."
        )

    novo_professor = Teacher(
        user_id=user_id,
        nome=teacher.nome,
        email=teacher.email,
        cpf=teacher.cpf,
        matricula=teacher.matricula,
        telefone=teacher.telefone,
        especialidade=teacher.especialidade,
        carga_horaria=teacher.carga_horaria,
        ativo=True
    )

    db.add(novo_professor)
    db.commit()
    db.refresh(novo_professor)

    return novo_professor

def get_teachers(db: Session):
    return db.query(Teacher).all()

def get_teacher_by_id(
    db: Session,
    teacher_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(Teacher.id == teacher_id)
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado."
        )

    return teacher

def get_teacher_classrooms(
    db: Session,
    teacher_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(Teacher.id == teacher_id)
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado."
        )

    return teacher.classrooms