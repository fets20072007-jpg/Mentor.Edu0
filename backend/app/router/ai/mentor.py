# === MENTOR EDU V9B2 - IMPORTS WEB PUSH ===
import asyncio as _me_asyncio
import os as _me_os
import secrets as _me_secrets
from datetime import datetime as _me_datetime, timezone as _me_timezone

try:
    from pywebpush import webpush as _me_webpush, WebPushException as _MEWebPushException
except Exception:
    _me_webpush = None
    _MEWebPushException = Exception

from fastapi import Request
import json

import re
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
from app.database.models import StudyFocusAlert
from app.database.models import StudyPushSubscription, StudyFocusPushState
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



@router.post("/test-ai")
def test_ai_provider(request: Request):
    if not AI_TEST_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="AI_TEST_TOKEN não configurado.",
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
                "Responda em português brasileiro em uma única frase curta."
            ),
            user_input=(
                "Confirme que a IA do Mentor.Edu está funcionando. "
                "Comece exatamente com: Mentor.Edu IA online"
            ),
            smart=False,
        )
    except Exception as error:
        _raise_ai_error(error)

    return {
    "status": "ok",
    "service": "Mentor Edu AI",
    "provider": result.get("provider"),
    "model_route": "fast",
    "model": result["model"],
    "response_id": result["response_id"],
    "resposta": result["text"],
}

# === TUTOR ALUNO V1 ===

def _tutor_focus(metrics: dict) -> list[dict]:
    subjects = metrics.get("desempenho_por_disciplina") or []

    valid = [
        item
        for item in subjects
        if item.get("media_percentual") is not None
    ]

    valid.sort(
        key=lambda item: item["media_percentual"]
    )

    return valid[:3]


def _tutor_instructions() -> str:
    return """
# MENTOR_EDU_TUTOR_NATURAL_V1_4
Você é o Tutor IA do Mentor.Edu.

IDENTIDADE
Você conversa como um tutor humano próximo, paciente e objetivo.
Não escreva como um chatbot corporativo, relatório ou manual.
Não diga que é "uma IA", "um modelo de linguagem" ou frases parecidas,
a menos que o estudante pergunte diretamente sobre isso.

OBJETIVO
Ensine o estudante a entender e resolver, não apenas entregue a resposta.
Responda exatamente ao que foi perguntado e avance aos poucos.

JEITO DE FALAR
- responda em português brasileiro natural;
- use linguagem simples e apropriada ao nível do estudante;
- comece direto pela dúvida, sem introduções genéricas;
- não repita o enunciado inteiro se isso não for necessário;
- evite frases como "Claro!", "Certamente!", "Vamos explorar", "É importante destacar"
  e outras aberturas artificiais quando não acrescentarem nada;
- não termine toda resposta com ofertas genéricas como
  "Se quiser, posso ajudar com mais alguma coisa";
- não use excesso de títulos, listas, emojis, negrito ou separadores;
- por padrão, prefira 2 a 4 blocos curtos;
- se a dúvida for simples, uma resposta curta é suficiente;
- se o aluno disser "não entendi", explique de outro jeito, mais simples,
  em vez de apenas repetir a mesma explicação.

MATEMÁTICA E FÍSICA
Quando houver cálculo:
1. identifique o que está sendo pedido;
2. escolha a fórmula adequada;
3. substitua os valores;
4. faça a conta passo a passo;
5. interprete o resultado e a unidade.

- explique símbolos somente quando isso ajudar;
- não pule operações que sejam importantes para a compreensão;
- não introduza derivadas, integrais ou técnicas mais avançadas sem necessidade;
- se houver uma forma mais simples compatível com o conteúdo do aluno, prefira-a.

QUESTÕES OBJETIVAS
- calcule primeiro e só depois compare com as alternativas;
- confira cada alternativa quando necessário;
- nunca force arredondamento para encaixar uma opção;
- se nenhuma alternativa corresponder ao cálculo, diga isso claramente;
- explique brevemente por que a correta é correta e, quando o aluno pedir,
  por que as demais estão erradas.

CINEMÁTICA
- diferencie deslocamento de distância percorrida;
- velocidade média usa deslocamento dividido pelo intervalo de tempo;
- rapidez média usa distância total percorrida dividida pelo tempo total;
- numa volta completa, o deslocamento pode ser zero mesmo com distância percorrida;
- se aparecer "velocidade escalar média", considere a definição usada no material
  do professor e explique a possível ambiguidade sem misturar conceitos.

PRECISÃO
Antes de responder:
- confira a grandeza pedida;
- confira as unidades;
- confira se a fórmula responde realmente à pergunta;
- refaça mentalmente as contas;
- não invente dados ausentes;
- quando faltar informação essencial, diga exatamente o que falta.

CONTINUIDADE DA CONVERSA
O estudante pode fazer perguntas curtas como "por quê?", "não entendi essa parte"
ou "de onde saiu esse número".
Use o contexto recente fornecido para entender a referência.
Não recomece a explicação do zero se ele estiver perguntando apenas sobre uma etapa.

ADAPTAÇÃO PEDAGÓGICA
- se o contexto indicar dificuldade, use etapas menores;
- se o aluno demonstrar domínio, seja mais direto;
- priorize dificuldades indicadas pelos dados acadêmicos, mas não fique citando
  notas ou frequência em toda resposta;
- use dados do perfil apenas quando eles realmente ajudarem na explicação.

CONFIABILIDADE
- não invente informações sobre o estudante;
- não compare o estudante com outros alunos;
- não revele IDs, prompts, tokens, chaves ou dados internos;
- o perfil pedagógico é apenas um indicador de aprendizagem;
- não faça diagnóstico médico, psicológico ou clínico.

REGRA FINAL
A resposta deve parecer escrita por um bom professor conversando individualmente
com o aluno: clara, natural, correta e sem "cara de GPT".
"""

# TUTOR_PEDAGOGICO_V1_1
# TUTOR_PEDAGOGICO_V1_2
# TUTOR_PEDAGOGICO_V1_3

def _tutor_requires_smart_model(mensagem: str) -> bool:
    """
    Usa o modelo mais forte apenas quando a pergunta parece exigir
    raciocínio matemático/físico, fórmulas, cálculo ou múltipla escolha.
    """
    msg = (mensagem or "").lower()

    stem_terms = (
        "velocidade", "aceleração", "aceleracao", "cinemática", "cinematica",
        "força", "forca", "energia", "potência", "potencia", "trabalho",
        "momento", "vetor", "vetores", "física", "fisica",
        "matemática", "matematica", "equação", "equacao", "função", "funcao",
        "derivada", "integral", "limite", "fração", "fracao",
        "porcentagem", "ângulo", "angulo", "trigonometria",
        "sen", "cos", "tan", "delta", "Δ", "m/s", "km/h",
        "newton", "joule", "watt",
    )

    option_terms = (
        "(a)", "(b)", "(c)", "(d)", "(e)",
        "alternativa", "alternativas", "múltipla escolha", "multipla escolha",
    )

    math_symbols = (
        "=", "+", "-", "*", "/", "^", "√", "²", "³",
    )

    has_stem_term = any(term in msg for term in stem_terms)
    has_options = any(term in msg for term in option_terms)
    has_math = any(symbol in msg for symbol in math_symbols)
    has_digits = any(ch.isdigit() for ch in msg)

    return has_stem_term or has_options or (has_math and has_digits)



# === SAIDA LIMPA DO TUTOR V3 ===

_TUTOR_CLEAN_OUTPUT_RULES = r"""
FORMATAÇÃO DE SAÍDA PARA O APLICATIVO — REGRA OBRIGATÓRIA
A resposta será exibida diretamente no chat do Mentor.Edu.
Escreva em texto limpo, natural e fácil de ler.

NÃO USE:
- Markdown;
- títulos com #;
- asteriscos ou crases como formatação;
- blocos de código;
- delimitadores LaTeX como \[ \] \( \) ou $$;
- comandos LaTeX como \frac, \dfrac, \tfrac, \times, \sqrt, \leq ou \geq.

EM MATEMÁTICA E FÍSICA:
- escreva fórmulas diretamente com símbolos legíveis;
- use × para multiplicação e ÷ quando necessário;
- use ² e ³ para potências simples;
- use Δ, √, ≤, ≥ e outros símbolos já prontos;
- sempre deixe espaço entre número e unidade: 3 m/s², 4 s, 24 m.

Exemplo correto:
s = s₀ + v₀ × t + (a × t²) / 2

Exemplo incorreto:
s = s_0 + v_0 t + \dfrac{a t^2}{2}

Substituição correta:
s = 0 + 0 × 4 + (3 × 4²) / 2

Nunca exponha caracteres de formatação que o estudante precise interpretar.
"""


def _clean_tutor_output(value: str) -> str:
    """Normaliza a saída da IA para leitura direta no Mentor.Edu."""
    if value is None:
        return ""

    text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Markdown comum.
    text = re.sub(r"```[A-Za-z0-9_-]*\s*", "", text)
    text = text.replace("```", "")
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_\n]+)__", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"(?m)^\s*[-*+]\s+", "• ", text)

    # Delimitadores e comandos de espaçamento LaTeX.
    text = text.replace(r"\[", "").replace(r"\]", "")
    text = text.replace(r"\(", "").replace(r"\)", "")
    text = text.replace("$$", "").replace("$", "")
    text = text.replace(r"\,", " ")
    text = text.replace(r"\;", " ")
    text = text.replace(r"\:", " ")
    text = text.replace(r"\!", "")
    text = text.replace("\\ ", " ")

    # Remove apenas comandos de dimensionamento.
    text = text.replace(r"\left", "").replace(r"\right", "")

    # Frações: \frac, \dfrac e \tfrac.
    frac = re.compile(
        r"\\(?:dfrac|tfrac|frac)\s*\{([^{}]+)\}\s*\{([^{}]+)\}"
    )

    def _fraction_repl(match):
        numerator = match.group(1).strip()
        denominator = match.group(2).strip()

        simple_num = bool(re.fullmatch(r"[A-Za-z0-9À-ÿ_.+-]+", numerator))
        simple_den = bool(re.fullmatch(r"[A-Za-z0-9À-ÿ_.+-]+", denominator))

        if simple_num and simple_den:
            return f"{numerator}/{denominator}"

        if simple_den:
            return f"({numerator}) / {denominator}"

        return f"({numerator}) / ({denominator})"

    for _ in range(6):
        new_text = frac.sub(_fraction_repl, text)
        if new_text == text:
            break
        text = new_text

    # Raiz quadrada simples.
    text = re.sub(
        r"\\sqrt\s*\{([^{}]+)\}",
        lambda m: f"√({m.group(1).strip()})",
        text,
    )

    replacements = {
        r"\times": "×",
        r"\cdot": "·",
        r"\div": "÷",
        r"\leq": "≤",
        r"\le": "≤",
        r"\geq": "≥",
        r"\ge": "≥",
        r"\neq": "≠",
        r"\approx": "≈",
        r"\pm": "±",
        r"\Delta": "Δ",
        r"\delta": "δ",
        r"\pi": "π",
        r"\theta": "θ",
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\omega": "ω",
        r"\mu": "μ",
        r"\infty": "∞",
        r"\%": "%",
        r"\_": "_",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Comandos que só envolvem texto.
    for _ in range(4):
        text = re.sub(
            r"\\(?:text|mathrm|mathbf|mathit|operatorname)\s*\{([^{}]*)\}",
            r"\1",
            text,
        )

    # Expoentes simples.
    text = re.sub(r"\^\s*\{?\s*2\s*\}?", "²", text)
    text = re.sub(r"\^\s*\{?\s*3\s*\}?", "³", text)

    # Subscritos numéricos.
    sub_map = str.maketrans(
        "0123456789+-=()",
        "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎",
    )

    def _sub_repl(match):
        raw = match.group(1) or match.group(2) or ""
        return raw.translate(sub_map)

    text = re.sub(
        r"_\{([0-9+\-=()]+)\}|_([0-9])",
        _sub_repl,
        text,
    )

    # Ambientes LaTeX.
    text = re.sub(r"\\begin\{[^}]+\}", "", text)
    text = re.sub(r"\\end\{[^}]+\}", "", text)
    text = text.replace(r"\\", "\n")

    # Chaves residuais de formatação.
    text = re.sub(r"\{([^{}\n]+)\}", r"\1", text)

    # Se sobrar algum comando desconhecido, remove só a barra.
    text = re.sub(r"\\([A-Za-z]+)", r"\1", text)

    # Corrige alguns casos seguros de unidade sem espaço.
    # Ex.: 3m/s² -> 3 m/s²
    text = re.sub(
        r"(?<![A-Za-z0-9_])(\d+(?:[.,]\d+)?)(m/s(?:²|³)?)\b",
        r"\1 \2",
        text,
    )

    # Em final de frase, corrige medidas comuns como 24m. -> 24 m.
    text = re.sub(
        r"(\d+(?:[.,]\d+)?)(m|s|kg|cm|mm|km)(?=[.,;:!?)]|$)",
        r"\1 \2",
        text,
    )

    # Limpeza final.
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)

    return text.strip()

def _run_student_tutor(
    *,
    mensagem: str,
    metrics: dict,
) -> dict:
    profile = classify_profile(metrics)
    focus = _tutor_focus(metrics)

    context = {
        "perfil_pedagogico": profile,
        "media_geral_percentual": (
            metrics.get("media_geral_percentual")
        ),
        "frequencia": metrics.get("frequencia"),
        "foco_prioritario": focus,
        "objetivo_declarado": (
            metrics.get("objetivo_declarado")
        ),
        "dificuldades_declaradas": (
            metrics.get("dificuldades_declaradas")
        ),
        "horas_estudo_dia": (
            metrics.get("horas_estudo_dia")
        ),
            "adaptacao_sessoes": metrics.get(
            "mentor10c_adaptive"
        ),
}

    use_smart_model = _tutor_requires_smart_model(mensagem)

    result = ask_text(
        instructions=_tutor_instructions() + _TUTOR_CLEAN_OUTPUT_RULES,
        user_input=(
            "CONTEXTO PEDAGÓGICO DO ESTUDANTE "
            "(use apenas para adaptar a didática; não trate como fonte "
            "de conteúdo da disciplina):\n"
            + json.dumps(
                context,
                ensure_ascii=False,
            )
            + "\n\nPERGUNTA DO ESTUDANTE:\n"
            + mensagem
        ),
        smart=use_smart_model,
    )

    return {
        "tutor_version": "1.4.4-clean",
        "resposta": _clean_tutor_output(result["text"]),
        "perfil": profile,
        "foco_prioritario": focus,
        "provider": result.get("provider"),
        "model_route": "smart" if use_smart_model else "fast",
        "smart_requested": use_smart_model,
        "model": result["model"],
        "response_id": result["response_id"],
    }


@router.post("/student/tutor")
def student_tutor_v1(
    payload: AIChatRequest,
    current_user: User = Depends(
        require_student
    ),
    db: Session = Depends(get_db),
):
    """
    Tutor IA personalizado do aluno.
    Usa somente contexto pedagógico do usuário autenticado.
    """
    metrics = build_student_metrics(
        db,
        current_user,
    )

    metrics["mentor10c_adaptive"] = (
        _me10c_adaptive_context(
            db,
            current_user.id,
        )
    )

    try:
        return _run_student_tutor(
            mensagem=payload.mensagem,
            metrics=metrics,
        )
    except Exception as error:
        _raise_ai_error(error)


# === MENTOR EDU ETAPA 6 - ALERTAS INTELIGENTES DO ALUNO ===

def _mentor_alert_number(value):
    try:
        if value is None or value == "":
            return None
        number = float(value)
        if number != number:
            return None
        return number
    except (TypeError, ValueError):
        return None


def _mentor_student_subjects(metrics: dict) -> list[dict]:
    raw = metrics.get("desempenho_por_disciplina") or []

    if isinstance(raw, dict):
        result = []
        for name, value in raw.items():
            if isinstance(value, dict):
                candidate = (
                    value.get("media_percentual")
                    if value.get("media_percentual") is not None
                    else value.get("percentual")
                    if value.get("percentual") is not None
                    else value.get("media")
                )
            else:
                candidate = value

            score = _mentor_alert_number(candidate)
            if score is not None:
                result.append({
                    "disciplina": str(name),
                    "media_percentual": score,
                })
        return result

    if not isinstance(raw, list):
        return []

    result = []

    for item in raw:
        if not isinstance(item, dict):
            continue

        name = (
            item.get("disciplina")
            or item.get("nome")
            or item.get("subject")
            or item.get("name")
        )

        candidate = (
            item.get("media_percentual")
            if item.get("media_percentual") is not None
            else item.get("percentual")
            if item.get("percentual") is not None
            else item.get("media")
        )

        score = _mentor_alert_number(candidate)

        if name and score is not None:
            result.append({
                "disciplina": str(name),
                "media_percentual": score,
            })

    return result


def _mentor_student_alerts(metrics: dict) -> list[dict]:
    """
    Alertas pedagógicos do próprio aluno.
    Reutiliza os indicadores acadêmicos existentes e não cria nova chamada de IA.
    """
    alerts = []

    average = _mentor_alert_number(
        metrics.get("media_geral_percentual")
    )

    attendance_data = metrics.get("frequencia") or {}
    attendance = None

    if isinstance(attendance_data, dict):
        attendance = _mentor_alert_number(
            attendance_data.get("taxa_presenca")
            if attendance_data.get("taxa_presenca") is not None
            else attendance_data.get("percentual")
        )

    subjects = _mentor_student_subjects(metrics)
    subjects.sort(
        key=lambda item: item["media_percentual"]
    )

    # Usa os mesmos cortes já usados no módulo de alertas do professor.
    if average is not None:
        if average < 50:
            alerts.append({
                "nivel": "critico",
                "titulo": "Desempenho geral precisa de atenção",
                "mensagem": (
                    f"Sua média geral atual é {average:.1f}%. "
                    "Vale revisar as avaliações recentes e priorizar "
                    "os conteúdos com maior dificuldade."
                ),
                "acao": "Ver minhas notas",
                "route": "grades",
                "prioridade": 100,
            })
        elif average < 60:
            alerts.append({
                "nivel": "atencao",
                "titulo": "Há espaço para recuperar desempenho",
                "mensagem": (
                    f"Sua média geral atual é {average:.1f}%. "
                    "Uma revisão focada nas disciplinas com menor "
                    "resultado pode ajudar."
                ),
                "acao": "Ver minhas notas",
                "route": "grades",
                "prioridade": 80,
            })
        elif average >= 85:
            alerts.append({
                "nivel": "positivo",
                "titulo": "Desempenho geral consistente",
                "mensagem": (
                    f"Sua média geral atual é {average:.1f}%. "
                    "Mantenha a rotina e use o Mentor para consolidar "
                    "os conteúdos."
                ),
                "acao": "Ver disciplinas",
                "route": "subjects",
                "prioridade": 25,
            })

    if attendance is not None:
        if attendance < 75:
            alerts.append({
                "nivel": "critico",
                "titulo": "Frequência merece atenção imediata",
                "mensagem": (
                    f"Sua taxa de presença registrada é {attendance:.1f}%. "
                    "Consulte o resumo de frequência e confira os registros."
                ),
                "acao": "Ver frequência",
                "route": "attendance",
                "prioridade": 110,
            })
        elif attendance < 80:
            alerts.append({
                "nivel": "atencao",
                "titulo": "Acompanhe sua frequência",
                "mensagem": (
                    f"Sua taxa de presença registrada é {attendance:.1f}%. "
                    "Vale acompanhar as próximas aulas e possíveis pendências."
                ),
                "acao": "Ver frequência",
                "route": "attendance",
                "prioridade": 90,
            })
        elif attendance >= 90:
            alerts.append({
                "nivel": "positivo",
                "titulo": "Boa regularidade nas aulas",
                "mensagem": (
                    f"Sua taxa de presença registrada é {attendance:.1f}%. "
                    "A regularidade está contribuindo para a continuidade "
                    "dos estudos."
                ),
                "acao": "Ver frequência",
                "route": "attendance",
                "prioridade": 20,
            })

    if subjects:
        weakest = subjects[0]
        score = weakest["media_percentual"]
        name = weakest["disciplina"]

        if score < 60:
            alerts.append({
                "nivel": "critico" if score < 50 else "atencao",
                "titulo": f"Prioridade atual: {name}",
                "mensagem": (
                    f"O indicador disponível para {name} está em {score:.1f}%. "
                    "Abra a disciplina ou converse com o Mentor para revisar "
                    "os pontos mais difíceis."
                ),
                "acao": "Ver disciplinas",
                "route": "subjects",
                "prioridade": 95 if score < 50 else 75,
            })

    if not alerts:
        alerts.append({
            "nivel": "informativo",
            "titulo": "Sem alerta acadêmico relevante agora",
            "mensagem": (
                "Os dados disponíveis não indicam uma prioridade urgente "
                "neste momento. Continue acompanhando notas, frequência "
                "e recomendações."
            ),
            "acao": "Conversar com o Mentor",
            "route": "mentor-edu",
            "prioridade": 10,
        })

    alerts.sort(
        key=lambda item: item.get("prioridade", 0),
        reverse=True,
    )

    result = []
    seen = set()

    for item in alerts:
        title = item.get("titulo")

        if not title or title in seen:
            continue

        seen.add(title)
        clean = dict(item)
        clean.pop("prioridade", None)
        result.append(clean)

        if len(result) >= 3:
            break

    return result


@router.get("/student/alerts")
def student_alerts_v1(
    current_user: User = Depends(
        require_student
    ),
    db: Session = Depends(get_db),
):
    metrics = build_student_metrics(
        db,
        current_user,
    )

    alerts = _mentor_student_alerts(metrics)

    return {
        "alerts_version": "1.0",
        "alertas": alerts,
        "quantidade": len(alerts),
        "gerado_por": "regras_pedagogicas_v1",
    }

# === MENTOR EDU V9B1 - SINCRONIZAÇÃO DE FOCO ===

def _focus_alert_table(db: Session):
    StudyFocusAlert.__table__.create(
        bind=db.get_bind(),
        checkfirst=True,
    )


def _focus_alert_level(
    remaining_minutes: int,
    late_minutes: int,
) -> str:
    remaining = max(0, int(remaining_minutes or 0))
    late = max(0, int(late_minutes or 0))

    if remaining <= 0:
        return "concluido"

    if late <= 0:
        return "em-dia"

    score = max(remaining, late)

    if score > 30:
        return "critico"
    if score > 15:
        return "alto"
    if score > 5:
        return "medio"
    return "baixo"


def _focus_alert_message(
    title: str,
    remaining_minutes: int,
    late_minutes: int,
) -> str:
    safe_title = (
        str(title or "Sessão de estudo").strip()
        or "Sessão de estudo"
    )

    return (
        f"{safe_title}: ainda faltam {remaining_minutes} min de foco. "
        f"O horário previsto terminou há {late_minutes} min."
    )


def _focus_alert_dict(item: StudyFocusAlert) -> dict:
    return {
        "id": item.id,
        "session_id": item.session_id,
        "title": item.title,
        "planned_minutes": item.planned_minutes,
        "active_ms": item.active_ms,
        "away_ms": item.away_ms,
        "remaining_minutes": item.remaining_minutes,
        "late_minutes": item.late_minutes,
        "level": item.level,
        "message": item.message,
        "updated_at": (
            item.updated_at.isoformat()
            if item.updated_at
            else None
        ),
    }


@router.post("/student/focus-alert")
def student_focus_alert_upsert(
    payload: dict,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    _focus_alert_table(db)

    try:
        session_id = int(payload.get("session_id"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=422,
            detail="session_id inválido.",
        )

    if session_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="session_id inválido.",
        )

    def safe_int(name: str) -> int:
        try:
            return max(
                0,
                int(float(payload.get(name, 0) or 0)),
            )
        except (TypeError, ValueError):
            return 0

    title = (
        str(payload.get("title") or "Sessão de estudo")
        .strip()[:255]
        or "Sessão de estudo"
    )

    planned_minutes = safe_int("planned_minutes")
    active_ms = safe_int("active_ms")
    away_ms = safe_int("away_ms")
    remaining_minutes = safe_int("remaining_minutes")
    late_minutes = safe_int("late_minutes")

    existing = (
        db.query(StudyFocusAlert)
        .filter(
            StudyFocusAlert.user_id == current_user.id,
            StudyFocusAlert.session_id == session_id,
        )
        .first()
    )

    # Sem atraso ou sem tempo pendente = sem cobrança.
    if remaining_minutes <= 0 or late_minutes <= 0:
        if existing:
            db.delete(existing)
            db.commit()

        return {
            "status": "clear",
            "session_id": session_id,
        }

    level = _focus_alert_level(
        remaining_minutes,
        late_minutes,
    )

    if existing is None:
        existing = StudyFocusAlert(
            user_id=current_user.id,
            session_id=session_id,
        )
        db.add(existing)

    existing.title = title
    existing.planned_minutes = planned_minutes
    existing.active_ms = active_ms
    existing.away_ms = away_ms
    existing.remaining_minutes = remaining_minutes
    existing.late_minutes = late_minutes
    existing.level = level
    existing.message = _focus_alert_message(
        title,
        remaining_minutes,
        late_minutes,
    )

    db.commit()
    db.refresh(existing)

    return {
        "status": "active",
        "alert": _focus_alert_dict(existing),
    }


@router.get("/student/focus-alerts")
def student_focus_alerts(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    _focus_alert_table(db)

    items = (
        db.query(StudyFocusAlert)
        .filter(
            StudyFocusAlert.user_id == current_user.id,
        )
        .order_by(StudyFocusAlert.updated_at.desc())
        .all()
    )

    return {
        "alerts_version": "9B.1",
        "alertas": [
            _focus_alert_dict(item)
            for item in items
        ],
        "quantidade": len(items),
    }


@router.post("/student/focus-alert/clear")
def student_focus_alert_clear(
    payload: dict,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    _focus_alert_table(db)

    try:
        session_id = int(payload.get("session_id"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=422,
            detail="session_id inválido.",
        )

    existing = (
        db.query(StudyFocusAlert)
        .filter(
            StudyFocusAlert.user_id == current_user.id,
            StudyFocusAlert.session_id == session_id,
        )
        .first()
    )

    if existing:
        db.delete(existing)
        db.commit()

    return {
        "status": "ok",
        "session_id": session_id,
    }

@router.post("/test-student-tutor")
def test_student_tutor_v1(
    request: Request,
):
    """
    Teste protegido com dados FICTÍCIOS.
    Não acessa banco nem dados reais de alunos.
    """
    if not AI_TEST_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="AI_TEST_TOKEN não configurado.",
        )

    supplied = request.headers.get(
        "X-Mentor-AI-Test"
    )

    if supplied != AI_TEST_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Token de teste inválido.",
        )

    fake_metrics = {
        "media_geral_percentual": 62.0,
        "desempenho_por_disciplina": [
            {
                "disciplina": "Física",
                "media_percentual": 48.0,
                "avaliacoes": 3,
            },
            {
                "disciplina": "Matemática",
                "media_percentual": 58.0,
                "avaliacoes": 4,
            },
            {
                "disciplina": "Português",
                "media_percentual": 80.0,
                "avaliacoes": 3,
            },
        ],
        "frequencia": {
            "registros": 40,
            "presentes": 35,
            "faltas": 5,
            "atrasos": 0,
            "taxa_presenca": 87.5,
        },
        "objetivo_declarado": (
            "Melhorar o desempenho em Física."
        ),
        "dificuldades_declaradas": (
            "Cinemática e interpretação de fórmulas."
        ),
        "horas_estudo_dia": 1.5,
        "respostas_avaliadas": {
            "quantidade": 10,
            "media_percentual": 60.0,
        },
    }

    try:
        result = _run_student_tutor(
            mensagem=(
                "Um objeto se move 10 m para a direita e depois 3 m para "
                "a esquerda em 5 s. Qual é a velocidade média? "
                "Alternativas: (A) 1 m/s, (B) 13 m/s, (C) 3 m/s. "
                "Mostre o cálculo e diga se alguma alternativa corresponde "
                "exatamente ao resultado."
            ),
            metrics=fake_metrics,
        )
    except Exception as error:
        _raise_ai_error(error)

    return {
        "status": "ok",
        "modo": "demonstracao",
        **result,
    }

# === MENTOR EDU V9B2 - SERVIÇO WEB PUSH ===

_ME_VAPID_PUBLIC_KEY = _me_os.getenv("VAPID_PUBLIC_KEY", "").strip()
_ME_VAPID_PRIVATE_KEY = _me_os.getenv("VAPID_PRIVATE_KEY", "").strip()
_ME_VAPID_SUBJECT = _me_os.getenv(
    "VAPID_SUBJECT",
    "mailto:contato@mentor.edu",
).strip()
_ME_PUSH_CRON_TOKEN = _me_os.getenv("FOCUS_PUSH_CRON_TOKEN", "").strip()

try:
    _ME_PUSH_INTERVAL_SECONDS = max(
        30,
        int(_me_os.getenv("FOCUS_PUSH_INTERVAL_SECONDS", "60")),
    )
except (TypeError, ValueError):
    _ME_PUSH_INTERVAL_SECONDS = 60


def _focus_push_tables(db: Session):
    StudyPushSubscription.__table__.create(bind=db.get_bind(), checkfirst=True)
    StudyFocusPushState.__table__.create(bind=db.get_bind(), checkfirst=True)


def _focus_push_enabled() -> bool:
    return bool(
        _ME_VAPID_PUBLIC_KEY
        and _ME_VAPID_PRIVATE_KEY
        and _me_webpush is not None
    )


def _focus_push_level_rank(level: str) -> int:
    return {
        "baixo": 1,
        "medio": 2,
        "alto": 3,
        "critico": 4,
    }.get(str(level or "").strip(), 0)


def _focus_push_level_label(level: str) -> str:
    return {
        "baixo": "Lembrete",
        "medio": "Urgência média",
        "alto": "Urgência alta",
        "critico": "Urgência crítica",
    }.get(str(level or "").strip(), "Lembrete")


def _focus_push_now():
    return _me_datetime.now(_me_timezone.utc)


def _focus_push_aware(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=_me_timezone.utc)
    return value.astimezone(_me_timezone.utc)


def _focus_push_effective_late(alert: StudyFocusAlert) -> int:
    base = max(0, int(alert.late_minutes or 0))
    updated = _focus_push_aware(alert.updated_at)
    if updated is None:
        return base
    elapsed = max(
        0,
        int((_focus_push_now() - updated).total_seconds() // 60),
    )
    return base + elapsed


def _focus_push_payload(alert: StudyFocusAlert, level: str, effective_late: int) -> dict:
    remaining = max(0, int(alert.remaining_minutes or 0))
    title = str(alert.title or "Sessão de estudo").strip() or "Sessão de estudo"
    return {
        "title": f"Mentor.Edu • {_focus_push_level_label(level)}",
        "body": (
            f"{title}: ainda faltam {remaining} min de foco. "
            f"O horário previsto terminou há {effective_late} min."
        ),
        "tag": f"mentor-study-session-{alert.session_id}",
        "requireInteraction": level == "critico",
        "data": {
            "url": "/dashboard.html",
            "session_id": alert.session_id,
            "level": level,
        },
    }


def _focus_push_send_one(subscription: StudyPushSubscription, payload: dict):
    if not _focus_push_enabled():
        return False, False

    import json as _me_json

    try:
        _me_webpush(
            subscription_info={
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth,
                },
            },
            data=_me_json.dumps(payload, ensure_ascii=False),
            vapid_private_key=_ME_VAPID_PRIVATE_KEY,
            vapid_claims={"sub": _ME_VAPID_SUBJECT},
            ttl=3600,
            timeout=12,
        )
        return True, False
    except _MEWebPushException as exc:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None) if response is not None else None
        if status in (404, 410):
            return False, True
        print(f"[MENTOR PUSH ERROR] {type(exc).__name__}: {exc}", flush=True)
        return False, False
    except Exception as exc:
        print(f"[MENTOR PUSH ERROR] {type(exc).__name__}: {exc}", flush=True)
        return False, False


def _focus_push_process_due(db: Session) -> dict:
    _focus_alert_table(db)
    _focus_push_tables(db)

    alerts = db.query(StudyFocusAlert).all()
    active_pairs = {(int(x.user_id), int(x.session_id)) for x in alerts}

    for state in db.query(StudyFocusPushState).all():
        pair = (int(state.user_id), int(state.session_id))
        if pair not in active_pairs:
            db.delete(state)

    sent = 0
    expired = 0
    evaluated = 0

    for alert in alerts:
        remaining = max(0, int(alert.remaining_minutes or 0))
        if remaining <= 0:
            continue

        effective_late = _focus_push_effective_late(alert)
        if effective_late <= 0:
            continue

        level = _focus_alert_level(remaining, effective_late)
        if level not in ("baixo", "medio", "alto", "critico"):
            continue

        evaluated += 1
        alert.late_minutes = effective_late
        alert.level = level
        alert.message = _focus_alert_message(
            alert.title,
            remaining,
            effective_late,
        )

        state = (
            db.query(StudyFocusPushState)
            .filter(
                StudyFocusPushState.user_id == alert.user_id,
                StudyFocusPushState.session_id == alert.session_id,
            )
            .first()
        )

        if state is None:
            state = StudyFocusPushState(
                user_id=alert.user_id,
                session_id=alert.session_id,
                last_level="",
            )
            db.add(state)
            db.flush()

        if _focus_push_level_rank(level) <= _focus_push_level_rank(state.last_level):
            continue

        subscriptions = (
            db.query(StudyPushSubscription)
            .filter(StudyPushSubscription.user_id == alert.user_id)
            .all()
        )
        if not subscriptions:
            continue

        payload = _focus_push_payload(alert, level, effective_late)
        delivered = False

        for subscription in list(subscriptions):
            ok, is_expired = _focus_push_send_one(subscription, payload)
            if ok:
                sent += 1
                delivered = True
            if is_expired:
                expired += 1
                db.delete(subscription)

        if delivered:
            state.last_level = level
            state.last_sent_at = _focus_push_now()

    db.commit()
    return {
        "status": "ok",
        "enabled": _focus_push_enabled(),
        "avaliados": evaluated,
        "enviados": sent,
        "assinaturas_expiradas": expired,
    }


def _focus_push_process_from_dependency():
    generator = get_db()
    try:
        db = next(generator)
    except StopIteration:
        return {"status": "no-db"}
    try:
        return _focus_push_process_due(db)
    finally:
        try:
            next(generator)
        except StopIteration:
            pass


async def mentor_focus_push_background_loop():
    while True:
        try:
            await _me_asyncio.to_thread(_focus_push_process_from_dependency)
        except Exception as exc:
            print(
                f"[MENTOR PUSH LOOP ERROR] {type(exc).__name__}: {exc}",
                flush=True,
            )
        await _me_asyncio.sleep(_ME_PUSH_INTERVAL_SECONDS)


@router.get("/student/push/config")
def student_push_config(
    current_user: User = Depends(require_student),
):
    return {
        "enabled": _focus_push_enabled(),
        "public_key": _ME_VAPID_PUBLIC_KEY if _focus_push_enabled() else None,
    }


@router.post("/student/push/subscribe")
def student_push_subscribe(
    payload: dict,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    _focus_push_tables(db)

    endpoint = str(payload.get("endpoint") or "").strip()
    keys = payload.get("keys") or {}
    p256dh = str(keys.get("p256dh") or "").strip()
    auth = str(keys.get("auth") or "").strip()
    device_label = str(payload.get("device_label") or "").strip()[:180]

    if not endpoint or not p256dh or not auth:
        raise HTTPException(status_code=422, detail="Assinatura push incompleta.")

    existing = (
        db.query(StudyPushSubscription)
        .filter(StudyPushSubscription.endpoint == endpoint)
        .first()
    )
    if existing is None:
        existing = StudyPushSubscription(user_id=current_user.id, endpoint=endpoint)
        db.add(existing)

    existing.user_id = current_user.id
    existing.p256dh = p256dh
    existing.auth = auth
    existing.device_label = device_label
    db.commit()
    db.refresh(existing)

    return {"status": "subscribed", "id": existing.id}


@router.post("/student/push/unsubscribe")
def student_push_unsubscribe(
    payload: dict,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
):
    _focus_push_tables(db)
    endpoint = str(payload.get("endpoint") or "").strip()
    if not endpoint:
        return {"status": "ok"}

    existing = (
        db.query(StudyPushSubscription)
        .filter(
            StudyPushSubscription.user_id == current_user.id,
            StudyPushSubscription.endpoint == endpoint,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        db.commit()

    return {"status": "ok"}


@router.post("/system/focus-push/run")
def system_focus_push_run(
    request: Request,
    db: Session = Depends(get_db),
):
    supplied = request.headers.get("X-Mentor-Push-Cron", "")

    if not _ME_PUSH_CRON_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="FOCUS_PUSH_CRON_TOKEN não configurado.",
        )

    if not _me_secrets.compare_digest(supplied, _ME_PUSH_CRON_TOKEN):
        raise HTTPException(status_code=403, detail="Token de cron inválido.")

    return _focus_push_process_due(db)

# === MENTOR EDU ETAPA 10A V2 - API REFLEXAO DA SESSAO ===
from datetime import datetime as _ME10ApiDatetime
from fastapi import HTTPException as _ME10HTTPException
from app.database.models import (
    StudySessionReflection as _ME10StudySessionReflection,
)


def _me10_reflection_table(db):
    _ME10StudySessionReflection.__table__.create(
        bind=db.get_bind(),
        checkfirst=True,
    )


def _me10_int(payload, key, minimum=None, maximum=None):
    value = payload.get(key)

    if value in (None, ""):
        return None

    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return None

    if minimum is not None:
        number = max(minimum, number)

    if maximum is not None:
        number = min(maximum, number)

    return number


def _me10_reflection_json(item):
    return {
        "id": item.id,
        "session_id": item.session_id,
        "materia": item.materia,
        "assunto": item.assunto,
        "dificuldade_inicial": item.dificuldade_inicial,
        "dificuldade_final": item.dificuldade_final,
        "compreensao_final": item.compreensao_final,
        "objetivo_status": item.objetivo_status,
        "dificuldade_restante": item.dificuldade_restante,
        "duracao_planejada": item.duracao_planejada,
        "foco_minutos": item.foco_minutos,
        "tempo_fora_minutos": item.tempo_fora_minutos,
        "updated_at": (
            item.updated_at.isoformat()
            if item.updated_at
            else None
        ),
    }


@router.post("/student/session-reflection-v10a")
def student_session_reflection_v10a(
    payload: dict,
    current_user=Depends(require_student),
    db=Depends(get_db),
):
    _me10_reflection_table(db)

    try:
        session_id = int(payload.get("session_id"))
    except (TypeError, ValueError):
        raise _ME10HTTPException(
            status_code=422,
            detail="session_id invalido.",
        )

    if session_id <= 0:
        raise _ME10HTTPException(
            status_code=422,
            detail="session_id invalido.",
        )

    objective = str(
        payload.get("objetivo_status")
        or "parcial"
    ).strip().lower()

    if objective not in {
        "cumprido",
        "parcial",
        "nao_cumprido",
    }:
        objective = "parcial"

    item = (
        db.query(_ME10StudySessionReflection)
        .filter(
            _ME10StudySessionReflection.user_id
            == current_user.id,
            _ME10StudySessionReflection.session_id
            == session_id,
        )
        .first()
    )

    if item is None:
        item = _ME10StudySessionReflection(
            user_id=current_user.id,
            session_id=session_id,
        )
        db.add(item)

    item.materia = (
        str(payload.get("materia") or "").strip()[:180]
        or None
    )

    item.assunto = (
        str(payload.get("assunto") or "").strip()[:255]
        or None
    )

    item.dificuldade_inicial = _me10_int(
        payload,
        "dificuldade_inicial",
        1,
        5,
    )

    item.dificuldade_final = _me10_int(
        payload,
        "dificuldade_final",
        1,
        5,
    )

    item.compreensao_final = _me10_int(
        payload,
        "compreensao_final",
        1,
        5,
    )

    item.objetivo_status = objective

    item.dificuldade_restante = (
        str(
            payload.get("dificuldade_restante")
            or ""
        ).strip()[:1500]
        or None
    )

    item.duracao_planejada = _me10_int(
        payload,
        "duracao_planejada",
        0,
        1440,
    )

    item.foco_minutos = _me10_int(
        payload,
        "foco_minutos",
        0,
        1440,
    )

    item.tempo_fora_minutos = _me10_int(
        payload,
        "tempo_fora_minutos",
        0,
        1440,
    )

    item.updated_at = _ME10ApiDatetime.utcnow()

    db.commit()
    db.refresh(item)

    return {
        "status": "saved",
        "reflection": _me10_reflection_json(item),
    }


@router.get("/student/session-reflections-v10a")
def student_session_reflections_v10a(
    current_user=Depends(require_student),
    db=Depends(get_db),
):
    _me10_reflection_table(db)

    items = (
        db.query(_ME10StudySessionReflection)
        .filter(
            _ME10StudySessionReflection.user_id
            == current_user.id,
        )
        .order_by(
            _ME10StudySessionReflection.updated_at.desc()
        )
        .all()
    )

    return {
        "reflection_version": "10A-V2",
        "quantidade": len(items),
        "reflexoes": [
            _me10_reflection_json(item)
            for item in items
        ],
    }

# === MENTOR EDU ETAPA 10B - API VERIFICACAO RAPIDA ===
import json as _m10b_json
import re as _m10b_re
from datetime import datetime as _M10BNow
from fastapi import HTTPException as _M10BHTTPException
from app.database.models import StudySessionCheck as _M10BStudySessionCheck

def _m10b_table(db):
    _M10BStudySessionCheck.__table__.create(bind=db.get_bind(), checkfirst=True)

def _m10b_questions(raw):
    text = str(raw or "").strip()
    text = _m10b_re.sub(r"^```(?:json)?\s*", "", text, flags=_m10b_re.I)
    text = _m10b_re.sub(r"\s*```$", "", text)
    a, b = text.find("["), text.rfind("]")
    if a >= 0 and b > a:
        text = text[a:b + 1]
    try:
        data = _m10b_json.loads(text)
    except Exception as exc:
        raise _M10BHTTPException(status_code=502, detail="O Mentor não conseguiu montar a verificação agora.") from exc
    out = []
    if not isinstance(data, list):
        data = []
    for idx, item in enumerate(data[:2], 1):
        if not isinstance(item, dict):
            continue
        q = str(item.get("enunciado") or item.get("pergunta") or "").strip()
        opts = item.get("alternativas") or {}
        if isinstance(opts, list):
            opts = {k: str(v).strip() for k, v in zip(("A", "B", "C", "D"), opts[:4])}
        if not isinstance(opts, dict):
            continue
        clean = {}
        for k in ("A", "B", "C", "D"):
            v = str(opts.get(k) or opts.get(k.lower()) or "").strip()
            if v:
                clean[k] = v
        correct = str(item.get("correta") or item.get("resposta") or "").strip().upper()[:1]
        exp = str(item.get("explicacao") or item.get("feedback") or "").strip()[:800]
        if q and len(clean) == 4 and correct in clean:
            out.append({"id": idx, "enunciado": q[:600], "alternativas": clean, "correta": correct, "explicacao": exp})
    if len(out) != 2:
        raise _M10BHTTPException(status_code=502, detail="O Mentor não conseguiu gerar duas questões válidas. Tente novamente.")
    return out

def _m10b_public(items):
    return [{"id": x["id"], "enunciado": x["enunciado"], "alternativas": x["alternativas"]} for x in items]

@router.post("/student/session-check-v10b/start")
def student_session_check_start_v10b(payload: dict, current_user=Depends(require_student), db=Depends(get_db)):
    _m10b_table(db)
    try:
        session_id = int(payload.get("session_id"))
    except (TypeError, ValueError):
        raise _M10BHTTPException(status_code=422, detail="session_id inválido.")
    materia = str(payload.get("materia") or "Conteúdo").strip()[:180]
    assunto = str(payload.get("assunto") or "Conteúdo estudado").strip()[:255]
    dificuldade = str(payload.get("dificuldade_final") or payload.get("dificuldade_inicial") or "não informada").strip()[:30]
    instructions = (
        "Você é o Mentor.Edu. Gere EXATAMENTE 2 questões objetivas curtas para verificar a compreensão de uma sessão de estudo. "
        "Cada questão deve ter quatro alternativas A, B, C e D e somente uma correta. Não repita a mesma ideia. "
        "Retorne SOMENTE JSON válido, sem Markdown, como um array de 2 objetos com as chaves: enunciado, alternativas, correta e explicacao."
    )
    user_input = f"Disciplina: {materia}\nConteúdo: {assunto}\nDificuldade: {dificuldade}/5\nCrie uma checagem curta e adequada."
    try:
        result = ask_text(instructions=instructions, user_input=user_input, smart=False)
    except Exception as exc:
        raise _M10BHTTPException(status_code=502, detail="A IA não conseguiu gerar a verificação agora. A sessão continua concluída.") from exc
    questions = _m10b_questions(result.get("text") if isinstance(result, dict) else result)
    item = db.query(_M10BStudySessionCheck).filter(
        _M10BStudySessionCheck.user_id == current_user.id,
        _M10BStudySessionCheck.session_id == session_id,
    ).first()
    if item is None:
        item = _M10BStudySessionCheck(user_id=current_user.id, session_id=session_id, questions_json="[]")
        db.add(item)
    item.materia = materia
    item.assunto = assunto
    item.questions_json = _m10b_json.dumps(questions, ensure_ascii=False)
    item.answers_json = None
    item.score = None
    item.total = 2
    item.feedback = None
    item.updated_at = _M10BNow.utcnow()
    db.commit()
    db.refresh(item)
    return {"check_version": "10B", "session_id": session_id, "questions": _m10b_public(questions)}

@router.post("/student/session-check-v10b/submit")
def student_session_check_submit_v10b(payload: dict, current_user=Depends(require_student), db=Depends(get_db)):
    _m10b_table(db)
    try:
        session_id = int(payload.get("session_id"))
    except (TypeError, ValueError):
        raise _M10BHTTPException(status_code=422, detail="session_id inválido.")
    item = db.query(_M10BStudySessionCheck).filter(
        _M10BStudySessionCheck.user_id == current_user.id,
        _M10BStudySessionCheck.session_id == session_id,
    ).first()
    if item is None:
        raise _M10BHTTPException(status_code=404, detail="Verificação não encontrada.")
    questions = _m10b_json.loads(item.questions_json)
    answers = payload.get("answers") or {}
    if not isinstance(answers, dict):
        raise _M10BHTTPException(status_code=422, detail="Respostas inválidas.")
    score = 0
    details = []
    saved = {}
    for q in questions:
        key = str(q["id"])
        ans = str(answers.get(key) or "").strip().upper()[:1]
        saved[key] = ans
        ok = ans == q["correta"]
        if ok:
            score += 1
        details.append({"id": q["id"], "correta": ok, "resposta_aluno": ans, "resposta_correta": q["correta"], "explicacao": q.get("explicacao") or ""})
    if score == 2:
        feedback = "Ótimo resultado: você acertou as duas questões."
    elif score == 1:
        feedback = "Bom começo: você acertou uma de duas questões. Vale revisar o ponto pendente."
    else:
        feedback = "Este conteúdo ainda precisa de revisão antes de avançar."
    item.answers_json = _m10b_json.dumps(saved, ensure_ascii=False)
    item.score = score
    item.total = 2
    item.feedback = feedback
    item.updated_at = _M10BNow.utcnow()
    db.commit()
    db.refresh(item)
    return {"check_version": "10B", "session_id": session_id, "score": score, "total": 2, "feedback": feedback, "details": details}

@router.get("/student/session-check-v10b/{session_id}")
def student_session_check_get_v10b(session_id: int, current_user=Depends(require_student), db=Depends(get_db)):
    _m10b_table(db)
    item = db.query(_M10BStudySessionCheck).filter(
        _M10BStudySessionCheck.user_id == current_user.id,
        _M10BStudySessionCheck.session_id == session_id,
    ).first()
    if item is None:
        return {"check_version": "10B", "session_id": session_id, "exists": False}
    return {"check_version": "10B", "session_id": session_id, "exists": True, "score": item.score, "total": item.total, "feedback": item.feedback, "answered": item.score is not None}

# === MENTOR EDU ETAPA 10C V2 - ADAPTACAO POS-SESSAO ===
from app.database.models import (
    StudySessionReflection as _ME10CReflection,
    StudySessionCheck as _ME10CCheck,
)


def _me10c_priority_for(reflection, check):
    initial = (
        int(reflection.dificuldade_inicial)
        if reflection.dificuldade_inicial is not None
        else None
    )

    final = (
        int(reflection.dificuldade_final)
        if reflection.dificuldade_final is not None
        else None
    )

    comprehension = (
        int(reflection.compreensao_final)
        if reflection.compreensao_final is not None
        else None
    )

    objective = str(
        reflection.objetivo_status
        or "parcial"
    )

    score_check = (
        int(check.score)
        if check is not None
        and check.score is not None
        else None
    )

    total_check = (
        int(check.total or 2)
        if check is not None
        else None
    )

    planned = int(
        reflection.duracao_planejada
        or 0
    )

    focus = int(
        reflection.foco_minutos
        or 0
    )

    weight = 0
    reasons = []

    if final is not None:
        if final >= 4:
            weight += 3
            reasons.append("dificuldade final alta")
        elif final == 3:
            weight += 2
            reasons.append("dificuldade final moderada")
        elif final <= 2:
            weight -= 1

    if comprehension is not None:
        if comprehension <= 2:
            weight += 2
            reasons.append("compreensão declarada baixa")
        elif comprehension == 3:
            weight += 1
        elif comprehension >= 4:
            weight -= 1

    if objective == "nao_cumprido":
        weight += 2
        reasons.append("objetivo da sessão não cumprido")
    elif objective == "parcial":
        weight += 1

    if score_check is not None:
        if score_check == 0:
            weight += 3
            reasons.append("verificação 0/2")
        elif score_check == 1:
            weight += 1
            reasons.append("verificação 1/2")
        elif score_check >= 2:
            weight -= 2

    if (
        planned > 0
        and focus >= 0
        and focus < planned * 0.6
    ):
        weight += 1
        reasons.append(
            "tempo de foco abaixo do planejado"
        )

    if (
        initial is not None
        and final is not None
    ):
        improvement = initial - final

        if improvement >= 2:
            weight -= 1
        elif improvement < 0:
            weight += 1
            reasons.append(
                "dificuldade aumentou após a sessão"
            )

    consolidated = (
        score_check == 2
        and final is not None
        and final <= 2
        and comprehension is not None
        and comprehension >= 4
    )

    if consolidated:
        level = "consolidado"
        label = "Conteúdo consolidado"
        priority = 0
    elif weight >= 6:
        level = "alta"
        label = "Prioridade alta"
        priority = 3
    elif weight >= 3:
        level = "media"
        label = "Prioridade média"
        priority = 2
    else:
        level = "baixa"
        label = "Prioridade baixa"
        priority = 1

    subject = (
        reflection.materia
        or (
            check.materia
            if check is not None
            else None
        )
        or "Conteúdo"
    )

    topic = (
        reflection.assunto
        or (
            check.assunto
            if check is not None
            else None
        )
        or "conteúdo estudado"
    )

    if level == "consolidado":
        recommendation = (
            f"{topic} apresentou bom domínio. "
            "Avance para um conteúdo relacionado e "
            "mantenha apenas uma revisão curta depois."
        )
    elif level == "alta":
        recommendation = (
            f"Não avance ainda em {topic}. "
            "Faça outra sessão curta de 10 a 15 minutos, "
            "com explicação guiada e exercícios básicos."
        )
    elif level == "media":
        recommendation = (
            f"Reforce {topic} em uma nova sessão curta, "
            "priorizando exercícios e correção dos pontos "
            "que ainda geraram dúvida."
        )
    else:
        recommendation = (
            f"Faça uma revisão breve de {topic} antes de avançar. "
            "Se a próxima checagem for boa, reduza a prioridade."
        )

    return {
        "session_id": reflection.session_id,
        "materia": subject,
        "assunto": topic,
        "nivel": level,
        "rotulo": label,
        "prioridade": priority,
        "peso": weight,
        "recomendacao": recommendation,
        "motivos": reasons[:4],
        "dados": {
            "dificuldade_inicial": initial,
            "dificuldade_final": final,
            "compreensao_final": comprehension,
            "objetivo_status": objective,
            "foco_minutos": focus,
            "duracao_planejada": planned,
            "score": score_check,
            "total": total_check,
        },
    }


def _me10c_adaptive_context(db, user_id):
    reflections = (
        db.query(_ME10CReflection)
        .filter(
            _ME10CReflection.user_id
            == user_id,
        )
        .order_by(
            _ME10CReflection.updated_at.desc()
        )
        .limit(12)
        .all()
    )

    if not reflections:
        return {
            "version": "10C-V2",
            "has_data": False,
            "items": [],
            "next_action": None,
        }

    session_ids = [
        item.session_id
        for item in reflections
    ]

    checks = (
        db.query(_ME10CCheck)
        .filter(
            _ME10CCheck.user_id
            == user_id,
            _ME10CCheck.session_id.in_(
                session_ids
            ),
        )
        .all()
    )

    checks_by_session = {
        item.session_id: item
        for item in checks
    }

    items = [
        _me10c_priority_for(
            reflection,
            checks_by_session.get(
                reflection.session_id
            ),
        )
        for reflection in reflections
    ]

    ordered = sorted(
        items,
        key=lambda item: (
            -int(item["prioridade"]),
            -int(item["peso"]),
        ),
    )

    return {
        "version": "10C-V2",
        "has_data": bool(items),
        "items": items[:8],
        "next_action": (
            ordered[0]
            if ordered
            else None
        ),
    }


@router.get("/student/adaptive-study-v10c")
def student_adaptive_study_v10c(
    current_user=Depends(require_student),
    db=Depends(get_db),
):
    return _me10c_adaptive_context(
        db,
        current_user.id,
    )
