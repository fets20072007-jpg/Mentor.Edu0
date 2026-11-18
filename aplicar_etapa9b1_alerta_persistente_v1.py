from pathlib import Path
import sys

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
FILES = HERE / "files"

MODELS = ROOT / "backend" / "app" / "database" / "models.py"
MENTOR = ROOT / "backend" / "app" / "router" / "ai" / "mentor.py"
API = ROOT / "frontend" / "js" / "api" / "study-sessions.js"
PAGE = ROOT / "frontend" / "js" / "pages" / "student" / "study-sessions.js"
CSS = ROOT / "frontend" / "css" / "pages.css"

for path in (MODELS, MENTOR, API, PAGE, CSS):
    if not path.exists():
        raise SystemExit(
            f"ERRO: arquivo necessário não encontrado: {path}"
        )

def read(path):
    return path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

def patch(name):
    path = FILES / name

    if not path.exists():
        raise SystemExit(
            f"ERRO: pacote incompleto. Faltou files/{name}"
        )

    return path.read_text(
        encoding="utf-8",
    )

models = read(MODELS)
mentor = read(MENTOR)
api = read(API)
page = read(PAGE)
css = read(CSS)

original_models = models
original_mentor = mentor
original_api = api
original_page = page
original_css = css

MODEL_BLOCK = patch("model_block.txt")
MENTOR_ENDPOINTS = patch("mentor_endpoints.txt")
API_BLOCK = patch("api_block.txt")
PAGE_HELPERS = patch("page_helpers.txt")
PAGE_MARKUP = patch("page_markup.txt")
PAGE_SYNC = patch("page_sync.txt")
CSS_BLOCK = patch("css_block.txt")

if "MENTOR_EDU_FOCUS_TIMER_V9A" not in page:
    raise SystemExit(
        "ERRO: a Etapa 9A não foi encontrada. "
        "Nenhuma alteração foi salva."
    )

if "Base" not in models:
    raise SystemExit(
        "ERRO: não encontrei Base em models.py. "
        "Nenhuma alteração foi salva."
    )

if "router = APIRouter" not in mentor:
    raise SystemExit(
        "ERRO: não encontrei o router do Mentor. "
        "Nenhuma alteração foi salva."
    )

if "MENTOR EDU V9B1 - ALERTA PERSISTENTE DE FOCO" not in models:
    models = (
        models.rstrip()
        + "\n\n"
        + MODEL_BLOCK.strip()
        + "\n"
    )

if "from app.database.models import StudyFocusAlert" not in mentor:
    anchor = "from app.schema.ai_mentor import ("
    pos = mentor.find(anchor)

    if pos == -1:
        anchor = "router = APIRouter"
        pos = mentor.find(anchor)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei ponto seguro de importação em mentor.py."
        )

    mentor = (
        mentor[:pos]
        + "from app.database.models import StudyFocusAlert\n"
        + mentor[pos:]
    )

if "MENTOR EDU V9B1 - SINCRONIZAÇÃO DE FOCO" not in mentor:
    anchor = '@router.post("/test-student-tutor")'
    pos = mentor.find(anchor)

    if pos == -1:
        pos = len(mentor)

    mentor = (
        mentor[:pos]
        + MENTOR_ENDPOINTS.strip()
        + "\n\n"
        + mentor[pos:]
    )

if "MENTOR_EDU_FOCUS_API_V9B1" not in api:
    if "api." not in api:
        api = (
            'import { api } from "./client.js";\n'
            + api
        )

    api = (
        api.rstrip()
        + "\n\n"
        + API_BLOCK.strip()
        + "\n"
    )

focus_import = (
    'import { syncStudyFocusAlert, getStudyFocusAlerts, '
    'clearStudyFocusAlert } from "../../api/study-sessions.js";'
)

if focus_import not in page:
    page = focus_import + "\n" + page

if "MENTOR_EDU_FOCUS_BACKEND_V9B1" not in page:
    anchor = "function mentorFocusTimerPanel"
    pos = page.find(anchor)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei mentorFocusTimerPanel da Etapa 9A."
        )

    page = (
        page[:pos]
        + PAGE_HELPERS.strip()
        + "\n\n"
        + page[pos:]
    )

if "data-focus-server-alerts" not in page:
    marker = (
        '            <div\n'
        '                class="mentor-focus-message"\n'
        '                data-focus-message\n'
        '            ></div>'
    )

    if marker not in page:
        raise SystemExit(
            "ERRO: não encontrei a área de mensagem do timer."
        )

    page = page.replace(
        marker,
        marker + "\n" + PAGE_MARKUP.rstrip(),
        1,
    )

if "shouldSyncBackend" not in page:
    render_pos = page.find(
        "const renderState = () => {"
    )

    marker = "        mentorFocusWriteState(state);"
    pos = page.find(marker, render_pos)

    if render_pos == -1 or pos == -1:
        raise SystemExit(
            "ERRO: não encontrei renderState para sincronizar."
        )

    page = (
        page[:pos]
        + PAGE_SYNC.rstrip()
        + "\n\n"
        + page[pos:]
    )

bind_pos = page.find("function bindFocusTimer")

if bind_pos == -1:
    raise SystemExit(
        "ERRO: não encontrei bindFocusTimer."
    )

load_call = "    mentorFocusLoadBackendAlerts(shell);"

if load_call not in page[bind_pos:]:
    marker = "    if (!shell) return;"
    pos = page.find(marker, bind_pos)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei o shell do temporizador."
        )

    insert_at = pos + len(marker)

    page = (
        page[:insert_at]
        + "\n\n"
        + load_call
        + page[insert_at:]
    )

# Limpa a cobrança persistente ao encerrar o timer.
if "closingSessionId" not in page:
    stop_pos = page.find(
        'stopButton?.addEventListener'
    )

    clear_pos = page.find(
        "mentorFocusClearState();",
        stop_pos,
    )

    if stop_pos == -1 or clear_pos == -1:
        raise SystemExit(
            "ERRO: não encontrei o encerramento do timer da Etapa 9A."
        )

    indent_start = page.rfind(
        "\n",
        0,
        clear_pos,
    ) + 1

    indent = page[
        indent_start:clear_pos
    ]

    inject = (
        f"{indent}const closingSessionId = state.sessionId;\n"
        f"{indent}mentorFocusClearBackend(closingSessionId).then(() => {{\n"
        f"{indent}    mentorFocusLoadBackendAlerts(shell);\n"
        f"{indent}}});\n\n"
    )

    page = (
        page[:clear_pos]
        + inject
        + page[clear_pos:]
    )

if "MENTOR_EDU_FOCUS_BACKEND_V9B1" not in css:
    css = (
        css.rstrip()
        + "\n\n"
        + CSS_BLOCK.strip()
        + "\n"
    )

try:
    compile(models, str(MODELS), "exec")
    compile(mentor, str(MENTOR), "exec")
except SyntaxError as exc:
    raise SystemExit(
        "ERRO: a Etapa 9B.1 geraria erro de sintaxe no backend. "
        "Nenhuma alteração foi salva.\n"
        f"Linha {exc.lineno}: {exc.msg}"
    )

checks = {
    "modelo": "class StudyFocusAlert(Base)" in models,
    "upsert": '@router.post("/student/focus-alert")' in mentor,
    "lista": '@router.get("/student/focus-alerts")' in mentor,
    "clear": '@router.post("/student/focus-alert/clear")' in mentor,
    "deduplicação": "uq_study_focus_alert_user_session" in models,
    "api": "syncStudyFocusAlert" in api and "getStudyFocusAlerts" in api,
    "sync": "shouldSyncBackend" in page,
    "painel": "data-focus-server-alerts" in page,
    "limpeza": "closingSessionId" in page,
    "css": "MENTOR_EDU_FOCUS_BACKEND_V9B1" in css,
}

failed = [
    name
    for name, ok in checks.items()
    if not ok
]

if failed:
    raise SystemExit(
        "ERRO: validação da Etapa 9B.1 falhou. "
        "Nenhuma alteração foi salva: "
        + ", ".join(failed)
    )

if (
    models == original_models
    and mentor == original_mentor
    and api == original_api
    and page == original_page
    and css == original_css
):
    print(
        "ETAPA 9B.1 já está aplicada. "
        "Nenhuma alteração necessária."
    )
    sys.exit(0)

for path, content in (
    (MODELS, original_models),
    (MENTOR, original_mentor),
    (API, original_api),
    (PAGE, original_page),
    (CSS, original_css),
):
    backup = path.with_name(
        path.name + ".backup_etapa9b1"
    )

    if not backup.exists():
        backup.write_text(
            content,
            encoding="utf-8",
        )

MODELS.write_text(models, encoding="utf-8")
MENTOR.write_text(mentor, encoding="utf-8")
API.write_text(api, encoding="utf-8")
PAGE.write_text(page, encoding="utf-8")
CSS.write_text(css, encoding="utf-8")

print()
print("========================================================")
print(" MENTOR.EDU - ETAPA 9B.1 ALERTA PERSISTENTE APLICADO")
print("========================================================")
print()
print("Backend:")
print("- tabela study_focus_alerts")
print("- 1 alerta por aluno + sessão")
print("- urgência recalculada no servidor")
print("- a cobrança é atualizada, não duplicada")
print("- ao regularizar/encerrar, ela é removida")
print()
print("Frontend:")
print("- sincronização a cada 30 s")
print("- sincronização quando muda a urgência")
print("- pendências aparecem em Sessões de estudo")
print()
print("Agora:")
print("1. Reinicie o backend")
print("2. Use Ctrl + F5")
print("3. Teste uma sessão curta")
