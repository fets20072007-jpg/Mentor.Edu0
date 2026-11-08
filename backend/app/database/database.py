from sqlalchemy import (
    create_engine
)

from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)

from app.core.config import (
    DATABASE_URL
)


# =========================================================
# ENGINE
# =========================================================

engine_options = {}


# SQLite precisa dessa opcao para funcionar
# corretamente com FastAPI.
#
# Outros bancos, como PostgreSQL,
# nao utilizam esse argumento.

if DATABASE_URL.startswith(
    "sqlite"
):

    engine_options[
        "connect_args"
    ] = {
        "check_same_thread": False
    }


engine = create_engine(

    DATABASE_URL,

    **engine_options
)


# =========================================================
# SESSAO
# =========================================================

SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine
)


# =========================================================
# BASE SQLALCHEMY
# =========================================================

Base = declarative_base()