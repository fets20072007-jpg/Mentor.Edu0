import os
from pathlib import Path

from dotenv import load_dotenv


# =========================================================
# CAMINHOS
# =========================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

ENV_FILE = (
    PROJECT_ROOT
    / ".env"
)


# =========================================================
# CARREGA .ENV
# =========================================================

load_dotenv(
    dotenv_path=ENV_FILE
)


# =========================================================
# AMBIENTE
# =========================================================

ENVIRONMENT = (
    os.getenv(
        "ENVIRONMENT",
        "development"
    )
    .strip()
    .lower()
)


# =========================================================
# SEGURANCA / JWT
# =========================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY"
)


if not SECRET_KEY:

    raise RuntimeError(
        "SECRET_KEY nao definida. "
        "Configure a variavel no arquivo .env."
    )


ALGORITHM = (
    os.getenv(
        "ALGORITHM",
        "HS256"
    )
    .strip()
)


try:

    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "60"
        )
    )

except ValueError as error:

    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES "
        "deve ser um numero inteiro."
    ) from error


# =========================================================
# BANCO DE DADOS
# =========================================================

DEFAULT_DB_PATH = (
    PROJECT_ROOT
    / "app"
    / "database"
    / "mentor.db"
)


DEFAULT_DATABASE_URL = (
    "sqlite:///"
    + DEFAULT_DB_PATH.as_posix()
)


_env_database_url = (
    os.getenv(
        "DATABASE_URL",
        ""
    )
    .strip()
)


DATABASE_URL = (
    _env_database_url
    or DEFAULT_DATABASE_URL
)


# =========================================================
# CORS
# =========================================================

DEFAULT_CORS_ORIGINS = (
    "http://127.0.0.1:5500,"
    "http://localhost:5500"
)


CORS_ORIGINS_RAW = os.getenv(
    "CORS_ORIGINS",
    DEFAULT_CORS_ORIGINS
)


CORS_ORIGINS = [

    origin.strip()

    for origin in (
        CORS_ORIGINS_RAW.split(",")
    )

    if origin.strip()
]