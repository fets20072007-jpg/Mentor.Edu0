from app.router.user.users import router as users_router
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
from app.router.education.questions import router as questions_router
from app.router.education.library import router as library_router
from app.router.education.pdf import router as pdf_router
from app.router.education.learning_history import router as history_router
#from app.router.education.lesson_plan import router as lesson_plan_router
from app.router.education.practical_examples import router as practical_examples_router
from app.router.education.videos import router as videos_router
from app.router.user.teacher import router as teacher_router
from fastapi import FastAPI

app = FastAPI(
    title="Mentor Edu API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "Mentor Edu backend rodando com sucesso!"}


app.include_router(users_router)
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
app.include_router(questions_router)
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
#app.include_router(lesson_plan_router)