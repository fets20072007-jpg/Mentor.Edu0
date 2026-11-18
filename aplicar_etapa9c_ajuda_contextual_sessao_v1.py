from pathlib import Path
import sys

ROOT = Path.cwd()
HERE = Path(__file__).resolve().parent
FILES = HERE / "files"

SESSIONS = (
    ROOT
    / "frontend"
    / "js"
    / "pages"
    / "student"
    / "study-sessions.js"
)

MENTOR = (
    ROOT
    / "frontend"
    / "js"
    / "pages"
    / "student"
    / "mentor-edu.js"
)

CSS = (
    ROOT
    / "frontend"
    / "css"
    / "pages.css"
)

for path in (
    SESSIONS,
    MENTOR,
    CSS,
):
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


sessions = read(SESSIONS)
mentor = read(MENTOR)
css = read(CSS)

original_sessions = sessions
original_mentor = mentor
original_css = css

SESSION_HELPERS = patch(
    "session_helpers.txt"
)

MENTOR_HELPERS = patch(
    "mentor_helpers.txt"
)

CSS_BLOCK = patch(
    "css_block.txt"
)

# -------------------------------------------------
# 1) Pré-requisitos
# -------------------------------------------------
if (
    "MENTOR_EDU_FOCUS_TIMER_V9A"
    not in sessions
):
    raise SystemExit(
        "ERRO: a Etapa 9A não foi encontrada em study-sessions.js. "
        "Nada foi salvo."
    )

if (
    "async function sendTutorMessage"
    not in mentor
):
    raise SystemExit(
        "ERRO: não encontrei o chat real do Mentor Edu. "
        "Nada foi salvo."
    )

if (
    'loadStudentProfile(page, user, navigate);'
    not in mentor
):
    raise SystemExit(
        "ERRO: não encontrei o carregamento final da página Mentor Edu. "
        "Nada foi salvo."
    )

# -------------------------------------------------
# 2) Helpers na tela de sessões
# -------------------------------------------------
if (
    "MENTOR_EDU_SESSION_MENTOR_HELP_V9C"
    not in sessions
):
    anchor = (
        "function mentorFocusTimerPanel"
    )

    pos = sessions.find(
        anchor
    )

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei mentorFocusTimerPanel. "
            "Nada foi salvo."
        )

    sessions = (
        sessions[:pos]
        + SESSION_HELPERS.strip()
        + "\n\n"
        + sessions[pos:]
    )

# -------------------------------------------------
# 3) Liga o CTA ao ciclo de render da página
# -------------------------------------------------
bind_call = (
    "        bindMentorSessionHelp("
    "container, current"
    ");"
)

if bind_call not in sessions:
    existing = (
        "        bindFocusTimer("
        "container, current"
        ");"
    )

    if existing not in sessions:
        raise SystemExit(
            "ERRO: não encontrei o bind da Etapa 9A. "
            "Nada foi salvo."
        )

    sessions = sessions.replace(
        existing,
        existing
        + "\n"
        + bind_call,
        1,
    )

# -------------------------------------------------
# 4) Helpers no Mentor
# -------------------------------------------------
if (
    "MENTOR_EDU_SESSION_CONTEXT_V9C"
    not in mentor
):
    anchor = (
        "async function "
        "sendTutorMessage"
    )

    pos = mentor.find(
        anchor
    )

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei sendTutorMessage. "
            "Nada foi salvo."
        )

    mentor = (
        mentor[:pos]
        + MENTOR_HELPERS.strip()
        + "\n\n"
        + mentor[pos:]
    )

# -------------------------------------------------
# 5) Consome o contexto uma única vez ao abrir Mentor
# -------------------------------------------------
consume_call = (
    "    mentorConsumeSessionContext("
    "sendTutorMessage"
    ");"
)

if consume_call not in mentor:
    anchor = (
        "    loadStudentProfile("
        "page, user, navigate"
        ");"
    )

    pos = mentor.rfind(
        anchor
    )

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei a carga final do Mentor Edu. "
            "Nada foi salvo."
        )

    insert_at = (
        pos
        + len(anchor)
    )

    mentor = (
        mentor[:insert_at]
        + "\n"
        + consume_call
        + mentor[insert_at:]
    )

# -------------------------------------------------
# 6) CSS
# -------------------------------------------------
if (
    "MENTOR_EDU_SESSION_MENTOR_HELP_V9C"
    not in css
):
    css = (
        css.rstrip()
        + "\n\n"
        + CSS_BLOCK.strip()
        + "\n"
    )

# -------------------------------------------------
# 7) Validação
# -------------------------------------------------
checks = {
    "helper sessão": (
        "MENTOR_EDU_SESSION_MENTOR_HELP_V9C"
        in sessions
    ),
    "cta": (
        "data-mentor-session-help"
        in sessions
    ),
    "bind sessão": (
        "bindMentorSessionHelp(container, current)"
        in sessions
    ),
    "contexto mentor": (
        "MENTOR_EDU_SESSION_CONTEXT_V9C"
        in mentor
    ),
    "prompt contextual": (
        "Atue como um orientador de estudo para ESTA sessão."
        in mentor
    ),
    "consumo único": (
        "mentorConsumeSessionContext(sendTutorMessage)"
        in mentor
    ),
    "css": (
        "MENTOR_EDU_SESSION_MENTOR_HELP_V9C"
        in css
    ),
}

failed = [
    name
    for name, ok in checks.items()
    if not ok
]

if failed:
    raise SystemExit(
        "ERRO: validação da Etapa 9C falhou. "
        "Nada foi salvo: "
        + ", ".join(failed)
    )

if (
    sessions == original_sessions
    and mentor == original_mentor
    and css == original_css
):
    print(
        "ETAPA 9C já parece estar aplicada. "
        "Nenhuma alteração necessária."
    )
    sys.exit(0)

# -------------------------------------------------
# 8) Backups
# -------------------------------------------------
for path, content in (
    (
        SESSIONS,
        original_sessions,
    ),
    (
        MENTOR,
        original_mentor,
    ),
    (
        CSS,
        original_css,
    ),
):
    backup = path.with_name(
        path.name
        + ".backup_etapa9c"
    )

    if not backup.exists():
        backup.write_text(
            content,
            encoding="utf-8",
        )

# -------------------------------------------------
# 9) Grava
# -------------------------------------------------
SESSIONS.write_text(
    sessions,
    encoding="utf-8",
)

MENTOR.write_text(
    mentor,
    encoding="utf-8",
)

CSS.write_text(
    css,
    encoding="utf-8",
)

print()
print("====================================================")
print(" MENTOR.EDU - ETAPA 9C AJUDA CONTEXTUAL APLICADA")
print("====================================================")
print()
print("Sessões de estudo:")
print("- botão centralizado de ajuda do Mentor")
print("- usa a sessão selecionada ou a sessão em foco")
print("- leva disciplina, conteúdo, dificuldade e duração")
print("- leva observações e dados do temporizador")
print()
print("Mentor Edu:")
print("- recebe o contexto automaticamente")
print("- escolhe método adequado à sessão")
print("- organiza o tempo restante")
print("- começa pelo primeiro passo")
print("- propõe prática curta e espera o aluno responder")
print()
print("Nenhum dado acadêmico é alterado.")
print("Não precisa reiniciar o backend.")
print()
print("Agora use Ctrl + F5 e teste o botão.")
