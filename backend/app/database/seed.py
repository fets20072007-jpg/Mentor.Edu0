from sqlalchemy import func

from app.core.security import hash_password
from app.database.database import SessionLocal
from app.database.models import User


TEST_USERS = (
    {
        "nome": "Aluno Teste A",
        "email": "aluno.a@mentor.test",
        "password": "Teste123!",
        "tipo": "Aluno",
    },
    {
        "nome": "Professor Teste A",
        "email": "professor.a@mentor.test",
        "password": "Teste123!",
        "tipo": "Professor",
    },
    {
        "nome": "Administrador Teste",
        "email": "admin@mentor.test",
        "password": "Teste123!",
        "tipo": "Administracao",
    },
    {
        "nome": "Suporte Mentor",
        "email": "suporte@mentor.test",
        "password": "Teste123!",
        "tipo": "Suporte",
    },
)


def seed_test_users() -> None:
    """Cria as contas de teste ausentes sem duplicar usuários existentes."""
    db = SessionLocal()
    try:
        created = 0

        for data in TEST_USERS:
            email = data["email"].strip().lower()
            existing = (
                db.query(User)
                .filter(func.lower(User.email) == email)
                .first()
            )

            if existing:
                continue

            db.add(
                User(
                    nome=data["nome"],
                    email=email,
                    senha=hash_password(data["password"]),
                    tipo=data["tipo"],
                    ativo=True,
                )
            )
            created += 1

        if created:
            db.commit()
            print(f"[seed] {created} usuario(s) de teste criado(s).")
        else:
            print("[seed] Usuarios de teste ja existem; nenhuma alteracao necessaria.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
