from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import (
    CORS_ORIGINS,
    ENVIRONMENT
)

from fastapi.staticfiles import StaticFiles
from sqlalchemy import text, inspect
from app.database.database import engine, Base
from app.database import models as database_models  # registra todos os modelos no metadata
from app.database.seed import seed_test_users
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.openapi.docs import get_swagger_ui_html

from app.router.user.users import router as users_router
from app.router.user.password import router as password_router
from app.router.auth.auth import router as auth_router

from app.router.academic.attendance import router as attendance_router
from app.router.academic.assessment import router as assessment_router
from app.router.academic.grade import router as grade_router
from app.router.academic.classroom import router as classroom_router
from app.router.academic.enrollment import router as enrollment_router
from app.router.academic.subject import router as subject_router
from app.router.academic.academic_record import router as academic_record_router

from app.router.analytics.performance import router as performance_router
from app.router.analytics.analytics import router as analytics_router
from app.router.analytics.dashboard import router as dashboard_router
from app.router.analytics.recommendations import router as recommendations_router

from app.router.ai.chat import router as chat_router
from app.router.ai.smart_recomendations import router as smart_router
from app.router.ai.study_plan import router as study_plan_router
from app.router.ai.study_sessions import router as study_sessions_router
from app.router.education.books import router as books_router
from app.router.education.chapters import router as chapters_router
from app.router.education.exercises import router as exercises_router
from app.router.education.answers import router as answers_router

# LEGADO - NÃƒO USAR
# from app.router.education.questions import router as questions_router

from app.router.education.library import router as library_router

from app.router.education.library_questions import (
    router as library_questions_router
)

from app.router.education.pdf import router as pdf_router
from app.router.education.learning_history import router as history_router
from app.router.education.practical_examples import router as practical_examples_router
from app.router.education.videos import router as videos_router
from app.router.user.teacher import router as teacher_router

# LEGADO:
# questÃµes da biblioteca agora usam LibraryQuestion / question-bank
#from app.router.education.library_questions import (router as library_questions_router)


from app.router.academic.admin import (
    router as admin_router
)

from app.router.system.ticket import (
    router as ticket_router
)

from app.router.system.uploads import router as uploads_router

from app.router.system.notification import (
    router as notification_router
)

from app.router.education.class_schedule import (
    router as class_schedule_router
)

from app.router.academic.assessment_access import (
    router as assessment_access_router
)

from app.router.academic.attendance_edit import (
    router as attendance_edit_router
)

IS_PRODUCTION = (
    ENVIRONMENT == "production"
)


app = FastAPI(
    title="Mentor.Edu API",

    description="""
    API do Mentor.Edu.

    Plataforma educacional para acompanhamento de alunos,
    professores, avalia??es, desempenho e ensino personalizado.
    """,

    version="1.0.0",

    docs_url=None,

    redoc_url=None,

    openapi_url=(
        None
        if IS_PRODUCTION
        else "/openapi.json"
    )
)
# =========================================================
# DESATIVA CACHE DO FRONTEND DURANTE O DESENVOLVIMENTO
# =========================================================
@app.middleware("http")
async def disable_frontend_cache(request, call_next):
    response = await call_next(request)
    path = request.url.path.lower()

    if (
        path == "/"
        or path.endswith(".html")
        or path.endswith(".js")
        or path.endswith(".css")
    ):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


# =========================================================
# ARQUIVOS ESTÃTICOS
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# =========================================================
# SWAGGER PERSONALIZADO - MENTOR.EDU
# =========================================================

if not IS_PRODUCTION:

    @app.get(
        "/docs",
        include_in_schema=False
    )
    def custom_swagger_ui():

        return get_swagger_ui_html(
            openapi_url=app.openapi_url,

            title="Mentor.Edu - DocumentaÃ§Ã£o da API",

            swagger_css_url=(
                "/static/swagger-custom.css"
            ),

            swagger_ui_parameters={
                "defaultModelsExpandDepth": -1,

                "displayRequestDuration": True,

                "filter": True,

                "persistAuthorization": True,

                "docExpansion": "none"
            }
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

@app.get("/", include_in_schema=False)
def frontend_index():
    return FileResponse(FRONTEND_DIR / "index.html")


app.include_router(users_router)
app.include_router(password_router)
app.include_router(auth_router)
app.include_router(study_plan_router)
app.include_router(study_sessions_router)
app.include_router(recommendations_router)
app.include_router(library_router)
app.include_router(chapters_router)
app.include_router(exercises_router)
app.include_router(videos_router)
app.include_router(pdf_router)
app.include_router(practical_examples_router)
# LEGADO:
# app.include_router(questions_router)
app.include_router(answers_router)
app.include_router(performance_router)
app.include_router(smart_router)
app.include_router(dashboard_router)
app.include_router(teacher_router)
app.include_router(classroom_router)
app.include_router(subject_router)
app.include_router(enrollment_router)
app.include_router(attendance_router)
app.include_router(assessment_router)
app.include_router(grade_router)
app.include_router(academic_record_router)
app.include_router(analytics_router)
app.include_router(history_router)
app.include_router(admin_router)
#app.include_router(lesson_plan_router)
app.include_router(library_questions_router)
app.include_router(ticket_router)
app.include_router(uploads_router)
app.include_router(notification_router)
app.include_router(class_schedule_router)
app.include_router(assessment_access_router)
app.include_router(attendance_edit_router)

# InicializaÃ§Ã£o do banco + migraÃ§Ãµes leves.
# Em ambientes novos (ex.: Render), o SQLite comeÃ§a vazio.
# Por isso as tabelas precisam existir antes de qualquer PRAGMA/ALTER TABLE.
@app.on_event("startup")
def initialize_database():
    Base.metadata.create_all(bind=engine)

    migrations = {
        "subjects": [("categoria", "VARCHAR DEFAULT 'Outras' NOT NULL")],
        "assessments": [("arquivo", "VARCHAR"), ("arquivo_nome", "VARCHAR")],
        "study_plans": [("material_url", "VARCHAR"), ("arquivo", "VARCHAR")],
        "tickets": [
            ("destinatario_perfil", "VARCHAR DEFAULT 'Suporte' NOT NULL"),
            ("destinatario_user_id", "INTEGER"),
            ("destinatario_nome", "VARCHAR")
        ],
        "attendance": [
            ("justificativa_status", "VARCHAR"),
            ("justificativa_enviada_em", "DATETIME"),
            ("justificativa_analisada_em", "DATETIME"),
            ("justificativa_analisada_por", "INTEGER")
        ],
    }
    with engine.begin() as conn:
        inspector = inspect(conn)
        for table, columns in migrations.items():
            existing = {
                column["name"]
                for column in inspector.get_columns(table)
            }
            for name, ddl in columns:
                if name not in existing:
                    # PostgreSQL usa TIMESTAMP no lugar de DATETIME.
                    safe_ddl = (
                        ddl.replace("DATETIME", "TIMESTAMP")
                        if engine.dialect.name == "postgresql"
                        else ddl
                    )
                    conn.execute(
                        text(
                            f"ALTER TABLE {table} "
                            f"ADD COLUMN {name} {safe_ddl}"
                        )
                    )

    # Cria somente as contas de teste que ainda nao existem.
    seed_test_users()

UPLOADS_DIR = PROJECT_ROOT / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Frontend estÃ¡tico servido pelo mesmo FastAPI.
# Deve ficar por Ãºltimo para nÃ£o capturar as rotas da API.
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")




