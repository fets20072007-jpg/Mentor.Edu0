from pathlib import Path
import sys

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
FILES = HERE / "files"

MODELS = ROOT / "backend" / "app" / "database" / "models.py"
MENTOR = ROOT / "backend" / "app" / "router" / "ai" / "mentor.py"
MAIN = ROOT / "backend" / "app" / "main.py"
REQUIREMENTS = ROOT / "backend" / "requirements.txt"
API = ROOT / "frontend" / "js" / "api" / "study-sessions.js"
PAGE = ROOT / "frontend" / "js" / "pages" / "student" / "study-sessions.js"
MAIN_JS = ROOT / "frontend" / "js" / "main.js"
SW = ROOT / "frontend" / "sw.js"

for path in (MODELS, MENTOR, MAIN, REQUIREMENTS, API, PAGE, MAIN_JS):
    if not path.exists():
        raise SystemExit(f"ERRO: arquivo necessário não encontrado: {path}")


def read(path):
    return path.read_text(encoding="utf-8-sig", errors="strict")


def patch(name):
    path = FILES / name
    if not path.exists():
        raise SystemExit(f"ERRO: pacote incompleto. Faltou files/{name}")
    return path.read_text(encoding="utf-8")

models = read(MODELS)
mentor = read(MENTOR)
main = read(MAIN)
requirements = read(REQUIREMENTS)
api = read(API)
page = read(PAGE)
main_js = read(MAIN_JS)
sw = read(SW) if SW.exists() else ""

originals = {
    MODELS: models,
    MENTOR: mentor,
    MAIN: main,
    REQUIREMENTS: requirements,
    API: api,
    PAGE: page,
    MAIN_JS: main_js,
    SW: sw,
}

if "MENTOR EDU V9B1 - ALERTA PERSISTENTE DE FOCO" not in models:
    raise SystemExit("ERRO: Etapa 9B.1 não encontrada em models.py.")
if "MENTOR EDU V9B1 - SINCRONIZAÇÃO DE FOCO" not in mentor:
    raise SystemExit("ERRO: Etapa 9B.1 não encontrada em mentor.py.")
if "MENTOR_EDU_FOCUS_TIMER_V9A" not in page:
    raise SystemExit("ERRO: Etapa 9A não encontrada em study-sessions.js.")
if "app" not in main:
    raise SystemExit("ERRO: aplicação FastAPI não encontrada em main.py.")

if "MENTOR EDU V9B2 - WEB PUSH" not in models:
    models = models.rstrip() + "\n\n" + patch("models_push.txt").strip() + "\n"

if "MENTOR EDU V9B2 - IMPORTS WEB PUSH" not in mentor:
    mentor = patch("mentor_imports.txt").strip() + "\n\n" + mentor

model_import = (
    "from app.database.models import StudyPushSubscription, StudyFocusPushState"
)
if model_import not in mentor:
    anchor = "from app.database.models import StudyFocusAlert"
    pos = mentor.find(anchor)
    if pos == -1:
        raise SystemExit("ERRO: import de StudyFocusAlert não encontrado.")
    line_end = mentor.find("\n", pos)
    mentor = mentor[:line_end + 1] + model_import + "\n" + mentor[line_end + 1:]

if "MENTOR EDU V9B2 - SERVIÇO WEB PUSH" not in mentor:
    mentor = mentor.rstrip() + "\n\n" + patch("mentor_push_service.txt").strip() + "\n"

if "MENTOR EDU V9B2 - STARTUP WEB PUSH" not in main:
    main = main.rstrip() + "\n\n" + patch("main_startup.txt").strip() + "\n"

if not any(line.strip().lower().startswith("pywebpush") for line in requirements.splitlines()):
    requirements = requirements.rstrip() + "\npywebpush==2.5.0\n"

if "MENTOR_EDU_WEB_PUSH_API_V9B2" not in api:
    api = api.rstrip() + "\n\n" + patch("api_push.txt").strip() + "\n"

push_import = (
    'import { getStudyPushConfig, saveStudyPushSubscription, '
    'removeStudyPushSubscription } from "../../api/study-sessions.js";'
)
if push_import not in page:
    page = push_import + "\n" + page

if "MENTOR_EDU_WEB_PUSH_V9B2" not in page:
    anchor = "function mentorFocusTimerPanel"
    pos = page.find(anchor)
    if pos == -1:
        raise SystemExit("ERRO: mentorFocusTimerPanel não encontrado.")
    page = page[:pos] + patch("page_push_helpers.txt").strip() + "\n\n" + page[pos:]

if "data-focus-push" not in page:
    token = "data-focus-notifications"
    pos = page.find(token)
    if pos == -1:
        raise SystemExit("ERRO: botão de notificações da Etapa 9A não encontrado.")
    close = page.find("</button>", pos)
    if close == -1:
        raise SystemExit("ERRO: fechamento do botão de notificações não encontrado.")
    close += len("</button>")
    page = page[:close] + "\n\n" + patch("page_push_button.txt").rstrip() + page[close:]

bind_pos = page.find("function bindFocusTimer")
if bind_pos == -1:
    raise SystemExit("ERRO: bindFocusTimer não encontrado.")

if "mentorPushRefreshButton(" not in page[bind_pos:]:
    token = "data-focus-notifications"
    pos = page.find(token, bind_pos)
    if pos == -1:
        raise SystemExit("ERRO: referência de notificationButton não encontrada.")
    # Insere após o fechamento da declaração que contém o seletor.
    end = page.find(");", pos)
    if end == -1:
        raise SystemExit("ERRO: declaração de notificationButton inválida.")
    end += 2
    page = page[:end] + "\n\n" + patch("page_push_bind.txt").rstrip() + page[end:]

sw_patch = patch("service_worker.txt")
if "MENTOR_EDU_SERVICE_WORKER_V9B2" not in sw:
    sw = sw.rstrip() + ("\n\n" if sw.strip() else "") + sw_patch.strip() + "\n"

if "MENTOR_EDU_REGISTER_SW_V9B2" not in main_js:
    main_js = main_js.rstrip() + "\n\n" + patch("main_js_sw.txt").strip() + "\n"

try:
    compile(models, str(MODELS), "exec")
    compile(mentor, str(MENTOR), "exec")
    compile(main, str(MAIN), "exec")
except SyntaxError as exc:
    raise SystemExit(
        "ERRO: a Etapa 9B.2 geraria erro de sintaxe no backend. "
        "Nenhuma alteração foi salva.\n"
        f"Linha {exc.lineno}: {exc.msg}"
    )

checks = {
    "subscription model": "class StudyPushSubscription(Base)" in models,
    "push state": "class StudyFocusPushState(Base)" in models,
    "config endpoint": '@router.get("/student/push/config")' in mentor,
    "subscribe endpoint": '@router.post("/student/push/subscribe")' in mentor,
    "cron endpoint": '@router.post("/system/focus-push/run")' in mentor,
    "background": "mentor_focus_push_background_loop" in mentor and "MENTOR EDU V9B2 - STARTUP WEB PUSH" in main,
    "requirement": "pywebpush==2.5.0" in requirements,
    "frontend api": "getStudyPushConfig" in api,
    "push button": "data-focus-push" in page,
    "service worker": "MENTOR_EDU_SERVICE_WORKER_V9B2" in sw,
    "sw register": "MENTOR_EDU_REGISTER_SW_V9B2" in main_js,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("ERRO: validação 9B.2 falhou. Nada foi salvo: " + ", ".join(failed))

for path, content in originals.items():
    if path == SW and not path.exists():
        continue
    if path.exists():
        backup = path.with_name(path.name + ".backup_etapa9b2")
        if not backup.exists():
            backup.write_text(content, encoding="utf-8")

MODELS.write_text(models, encoding="utf-8")
MENTOR.write_text(mentor, encoding="utf-8")
MAIN.write_text(main, encoding="utf-8")
REQUIREMENTS.write_text(requirements, encoding="utf-8")
API.write_text(api, encoding="utf-8")
PAGE.write_text(page, encoding="utf-8")
MAIN_JS.write_text(main_js, encoding="utf-8")
SW.write_text(sw, encoding="utf-8")

print("\n====================================================")
print(" MENTOR.EDU - ETAPA 9B.2 WEB PUSH APLICADA")
print("====================================================\n")
print("Incluído:")
print("- Service Worker")
print("- assinatura Push por dispositivo")
print("- VAPID")
print("- deduplicação por sessão e nível")
print("- escalonamento em segundo plano")
print("- loop do backend")
print("- endpoint protegido para cron externo\n")
print("Agora rode:")
print("1. pip install -r backend/requirements.txt")
print("2. python configurar_webpush_9b2.py")
print("3. reinicie o backend")
print("4. Ctrl + F5")
print("5. ative Push em segundo plano em Sessões")
