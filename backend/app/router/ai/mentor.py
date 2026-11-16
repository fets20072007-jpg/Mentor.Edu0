from fastapi import Request
import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.core.config import AI_TEST_TOKEN

from app.core.permissions import (
    require_student,
    require_teacher,
)
from app.database.dependencies import get_db
from app.database.models import (
    User,
    Teacher,
    Classroom,
    Subject,
    Enrollment,
)
from app.schema.ai_mentor import (
    AIChatRequest,
    AIQuestionRequest,
    AILessonPlanRequest,
)
from app.services.ai.mentor_client import (
    MentorAIUnavailable,
    ask_text,
    ask_json,
)
from app.services.ai.context_builder import (
    build_student_metrics,
    classify_profile,
)


router = APIRouter(
    prefix="/mentor-ai",
    tags=["Mentor Edu AI"],
)


def _raise_ai_error(error):
    print(
        f"[MENTOR AI ERROR] "
        f"{type(error).__name__}: {error}",
        flush=True,
    )

    if isinstance(
        error,
        MentorAIUnavailable,
    ):
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    raise HTTPException(
        status_code=502,
        detail="Não foi possível obter resposta do serviço de IA.",
    ) from error

@router.get("/health")
def ai_health():
    return {
        "status": "ok",
        "service": "Mentor Edu AI",
    }


@router.get("/student/profile")
def student_profile(
    current_user: User = Depends(
        require_student
    ),
    db: Session = Depends(get_db),
):
    metrics = build_student_metrics(
        db,
        current_user,
    )

    profile = classify_profile(metrics)

    instructions = """
Você é o analista pedagógico do Mentor.Edu.

Analise SOMENTE os dados fornecidos.
O perfil calculado por regras do sistema é a base.
Não faça diagnóstico psicológico, médico ou clínico.
Não invente notas, faltas ou dificuldades.
Quando houver poucos dados, deixe isso explícito.

Retorne JSON no formato:
{
  "resumo": "texto curto",
  "pontos_fortes": ["..."],
  "pontos_atencao": ["..."],
  "acoes_aluno": ["..."],
  "sugestoes_professor": ["..."],
  "confianca": "baixa|media|alta"
}
"""

    try:
        result = ask_json(
            instructions=instructions,
            user_input=json.dumps(
                {
                    "perfil_calculado": profile,
                    "metricas": metrics,
                },
                ensure_ascii=False,
            ),
            smart=True,
        )
    except Exception as error:
        _raise_ai_error(error)

    return {
        "perfil": profile,
        "metricas": metrics,
        "analise": result["data"],
        "model": result["model"],
        "response_id": result["response_id"],
    }


@router.post("/student/chat")
def student_chat(
    payload: AIChatRequest,
    current_user: User = Depends(
        require_student
    ),
    db: Session = Depends(get_db),
):
    metrics = build_student_metrics(
        db,
        current_user,
    )

    instructions = """
Você é o Tutor Mentor.Edu.
Fale em português brasileiro.

Seu objetivo é ENSINAR.

- adapte a explicação ao contexto pedagógico;
- explique exercícios passo a passo;
- não faça diagnóstico médico ou psicológico;
- não revele IDs nem dados internos;
- nunca cite dados de outro aluno;
- se faltar contexto, diga o que precisa;
- evite dar somente a resposta final.
"""

    try:
        result = ask_text(
            instructions=instructions,
            user_input=(
                "CONTEXTO PEDAGÓGICO:\n"
                + json.dumps(
                    metrics,
                    ensure_ascii=False,
                )
                + "\n\nPERGUNTA DO ALUNO:\n"
                + payload.mensagem
            ),
            smart=False,
        )
    except Exception as error:
        _raise_ai_error(error)

    return {
        "resposta": result["text"],
        "model": result["model"],
        "response_id": result["response_id"],
    }


@router.post("/teacher/questions")
def teacher_questions(
    payload: AIQuestionRequest,
    current_user: User = Depends(
        require_teacher
    ),
):
    instructions = """
Você é o gerador pedagógico de questões do Mentor.Edu.

- gere exatamente a quantidade solicitada;
- cada questão objetiva tem UMA resposta correta;
- distratores devem ser plausíveis;
- não copie literalmente questões protegidas;
- quando houver curso técnico, contextualize algumas
  questões em situações profissionais;
- explicação é exclusiva do professor;
- se alternativas=4, use A-D e alternativa_e=null.

Retorne JSON:
{
  "titulo": "...",
  "questoes": [
    {
      "enunciado": "...",
      "alternativa_a": "...",
      "alternativa_b": "...",
      "alternativa_c": "...",
      "alternativa_d": "...",
      "alternativa_e": "... ou null",
      "resposta_correta": "A|B|C|D|E",
      "explicacao": "...",
      "dificuldade": "Fácil|Médio|Difícil",
      "categoria": "..."
    }
  ]
}
"""

    try:
        result = ask_json(
            instructions=instructions,
            user_input=json.dumps(
                payload.model_dump(),
                ensure_ascii=False,
            ),
            smart=True,
        )
    except Exception as error:
        _raise_ai_error(error)

    data = result["data"]

    if (
        not isinstance(data, dict)
        or not isinstance(
            data.get("questoes"),
            list,
        )
    ):
        raise HTTPException(
            status_code=502,
            detail="Formato de questões inválido.",
        )

    return {
        **data,
        "model": result["model"],
        "response_id": result["response_id"],
    }


@router.post("/teacher/lesson-plan")
def teacher_lesson_plan(
    payload: AILessonPlanRequest,
    current_user: User = Depends(
        require_teacher
    ),
):
    instructions = """
Você é o planejador pedagógico do Mentor.Edu.

Crie um plano REALISTA e aplicável.

Inclua:
- objetivos;
- competências/habilidades;
- divisão do tempo;
- metodologia;
- atividade prática;
- avaliação da aprendizagem;
- adaptações para diferentes ritmos.

Se houver curso técnico, conecte a disciplina
com situações profissionais e práticas do curso.

Não invente códigos oficiais de currículo
se eles não forem fornecidos.

Retorne JSON:
{
  "titulo": "...",
  "objetivos": ["..."],
  "competencias": ["..."],
  "etapas": [
    {
      "nome": "...",
      "minutos": 10,
      "descricao": "..."
    }
  ],
  "atividade_pratica": "...",
  "avaliacao_aprendizagem": "...",
  "adaptacoes": ["..."],
  "integracao_curso_tecnico": "..."
}
"""

    try:
        result = ask_json(
            instructions=instructions,
            user_input=json.dumps(
                payload.model_dump(),
                ensure_ascii=False,
            ),
            smart=True,
        )
    except Exception as error:
        _raise_ai_error(error)

    return {
        "plano": result["data"],
        "model": result["model"],
        "response_id": result["response_id"],
    }


@router.get(
    "/teacher/classrooms/{classroom_id}/alerts"
)
def classroom_alerts(
    classroom_id: int,
    current_user: User = Depends(
        require_teacher
    ),
    db: Session = Depends(get_db),
):
    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == current_user.id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor não encontrado.",
        )

    classroom = (
        db.query(Classroom)
        .filter(
            Classroom.id == classroom_id
        )
        .first()
    )

    if not classroom:
        raise HTTPException(
            status_code=404,
            detail="Turma não encontrada.",
        )

    teaches_class = (
        db.query(Subject)
        .filter(
            Subject.teacher_id == teacher.id,
            Subject.classroom_id == classroom_id,
            Subject.ativa == True,
        )
        .first()
    )

    is_dt = (
        classroom.teacher_id == teacher.id
    )

    if not teaches_class and not is_dt:
        raise HTTPException(
            status_code=403,
            detail="Você não possui vínculo com esta turma.",
        )

    enrollments = (
        db.query(Enrollment)
        .filter(
            Enrollment.classroom_id == classroom_id,
            Enrollment.ativo == True,
        )
        .all()
    )

    alerts = []

    for enrollment in enrollments:
        student = enrollment.user
        if not student:
            continue

        metrics = build_student_metrics(
            db,
            student,
        )

        grade = metrics.get(
            "media_geral_percentual"
        )

        attendance = (
            metrics.get("frequencia", {})
            .get("taxa_presenca")
        )

        level = None
        signal = None

        if (
            grade is not None
            and attendance is not None
            and grade < 50
            and attendance < 75
        ):
            level = "critico"
            signal = (
                "Baixo desempenho associado "
                "a frequência reduzida."
            )

        elif (
            (grade is not None and grade < 60)
            or (
                attendance is not None
                and attendance < 80
            )
        ):
            level = "atencao"
            signal = (
                "Há indicadores que merecem "
                "acompanhamento pedagógico."
            )

        elif (
            grade is not None
            and attendance is not None
            and grade >= 85
            and attendance >= 90
        ):
            level = "positivo"
            signal = (
                "Desempenho e frequência "
                "consistentemente positivos."
            )

        if level:
            alerts.append({
                "student_id": student.id,
                "nome": student.nome,
                "nivel": level,
                "sinal": signal,
                "media_percentual": grade,
                "taxa_presenca": attendance,
            })

    aggregate = {
        "turma": classroom.nome,
        "alunos_ativos": len(enrollments),
        "alertas_criticos": sum(
            1
            for item in alerts
            if item["nivel"] == "critico"
        ),
        "alertas_atencao": sum(
            1
            for item in alerts
            if item["nivel"] == "atencao"
        ),
        "sinais_positivos": sum(
            1
            for item in alerts
            if item["nivel"] == "positivo"
        ),
    }

    try:
        result = ask_text(
            instructions=(
                "Você é o analista de turma do Mentor.Edu. "
                "Receberá somente dados agregados. "
                "Faça uma síntese curta de prioridades e "
                "pontos positivos. Não invente fatos."
            ),
            user_input=json.dumps(
                aggregate,
                ensure_ascii=False,
            ),
            smart=False,
        )

        summary = result["text"]
        model = result["model"]
        response_id = result["response_id"]

    except Exception:
        summary = (
            "Resumo de IA indisponível; "
            "os alertas por regras continuam válidos."
        )
        model = None
        response_id = None

    return {
        "resumo": summary,
        "indicadores": aggregate,
        "alertas": alerts,
        "model": model,
        "response_id": response_id,
    }


@router.post("/test-openai")
def test_openai(request: Request):
    """Teste técnico protegido da conexão Mentor.Edu -> OpenAI."""

    if not AI_TEST_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="AI_TEST_TOKEN não configurado no servidor.",
        )

    supplied = request.headers.get("X-Mentor-AI-Test")

    if supplied != AI_TEST_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Token de teste inválido.",
        )

    try:
        result = ask_text(
            instructions=(
                "Você está realizando um teste técnico do Mentor.Edu. "
                "Responda em português brasileiro, em uma única frase curta."
            ),
            user_input=(
                "Confirme que a conexão com a IA está funcionando. "
                "Comece exatamente com: Mentor.Edu IA online"
            ),
            smart=False,
        )
    except Exception as error:
        _raise_ai_error(error)

    return {
        "status": "ok",
        "service": "Mentor Edu AI",
        "model": result["model"],
        "response_id": result["response_id"],
        "resposta": result["text"],
    }
