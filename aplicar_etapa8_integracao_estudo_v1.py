from pathlib import Path
import sys

ROOT = Path.cwd()

MENTOR_PAGE = ROOT / "frontend" / "js" / "pages" / "student" / "mentor-edu.js"
PLAN_PAGE = ROOT / "frontend" / "js" / "pages" / "student" / "study-plans.js"
SESSION_PAGE = ROOT / "frontend" / "js" / "pages" / "student" / "study-sessions.js"
CSS = ROOT / "frontend" / "css" / "mentor-ai-page.css"

for path in (MENTOR_PAGE, PLAN_PAGE, SESSION_PAGE, CSS):
    if not path.exists():
        raise SystemExit(
            f"ERRO: arquivo necessário não encontrado: {path}"
        )

def read(path):
    return path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

mentor = read(MENTOR_PAGE)
plans = read(PLAN_PAGE)
sessions = read(SESSION_PAGE)
css = read(CSS)

original_mentor = mentor
original_plans = plans
original_sessions = sessions
original_css = css

MENTOR_HELPERS = '\n// MENTOR_EDU_HANDOFF_V8\nconst MENTOR_PLAN_PREFILL_KEY = "mentor_edu_plan_prefill_v1";\nconst MENTOR_SESSION_PREFILL_KEY = "mentor_edu_session_prefill_v1";\n\nfunction writeMentorHandoff(key, suggestion) {\n    const text = String(suggestion || "").trim();\n\n    if (!text) return false;\n\n    try {\n        sessionStorage.setItem(\n            key,\n            JSON.stringify({\n                suggestion: text,\n                createdAt: Date.now(),\n                source: "mentor-edu",\n            }),\n        );\n        return true;\n    } catch {\n        return false;\n    }\n}\n'
OLD_PLAN_HANDLER = '    page.querySelectorAll("[data-suggestion-plan]").forEach(button => {\n        button.addEventListener("click", () => {\n            navigate("study-plans");\n        });\n    });'
NEW_PLAN_HANDLER = '    page.querySelectorAll("[data-suggestion-plan]").forEach(button => {\n        button.addEventListener("click", () => {\n            writeMentorHandoff(\n                MENTOR_PLAN_PREFILL_KEY,\n                button.dataset.suggestionPlan,\n            );\n\n            navigate("study-plans");\n        });\n    });'
OLD_SESSION_HANDLER = '    page.querySelectorAll("[data-suggestion-session]").forEach(button => {\n        button.addEventListener("click", () => {\n            navigate("study-sessions");\n        });\n    });'
NEW_SESSION_HANDLER = '    page.querySelectorAll("[data-suggestion-session]").forEach(button => {\n        button.addEventListener("click", () => {\n            writeMentorHandoff(\n                MENTOR_SESSION_PREFILL_KEY,\n                button.dataset.suggestionSession,\n            );\n\n            navigate("study-sessions");\n        });\n    });'
PLAN_HELPER = '\n// MENTOR_EDU_PLAN_HANDOFF_V8\nconst MENTOR_PLAN_PREFILL_KEY = "mentor_edu_plan_prefill_v1";\n\nfunction readMentorPlanPrefill() {\n    try {\n        const raw = sessionStorage.getItem(\n            MENTOR_PLAN_PREFILL_KEY,\n        );\n\n        if (!raw) return null;\n\n        sessionStorage.removeItem(\n            MENTOR_PLAN_PREFILL_KEY,\n        );\n\n        const data = JSON.parse(raw);\n        const suggestion = String(\n            data?.suggestion || "",\n        ).trim();\n\n        return suggestion\n            ? { suggestion }\n            : null;\n    } catch {\n        try {\n            sessionStorage.removeItem(\n                MENTOR_PLAN_PREFILL_KEY,\n            );\n        } catch {\n            // Sem ação.\n        }\n\n        return null;\n    }\n}\n\nfunction applyMentorPlanPrefill(container) {\n    const data = readMentorPlanPrefill();\n\n    if (!data) return;\n\n    const form = container.querySelector(\n        "[data-plan-form]",\n    );\n\n    if (!form) return;\n\n    const title = form.elements?.titulo;\n    const goal = form.elements?.meta;\n    const hours = form.elements?.horas_dia;\n    const subjects = form.elements?.materias;\n\n    if (title) {\n        title.value = "Plano sugerido pelo Mentor";\n    }\n\n    if (goal) {\n        goal.value = data.suggestion;\n    }\n\n    if (hours && !hours.value) {\n        hours.value = "2";\n    }\n\n    form.hidden = false;\n\n    form.scrollIntoView({\n        behavior: "smooth",\n        block: "center",\n    });\n\n    setTimeout(() => {\n        subjects?.focus();\n    }, 250);\n\n    showToast(\n        "Sugestão do Mentor carregada. Complete as matérias e salve o plano.",\n        "success",\n    );\n}\n'
SESSION_HELPER = '\n// MENTOR_EDU_SESSION_HANDOFF_V8\nconst MENTOR_SESSION_PREFILL_KEY = "mentor_edu_session_prefill_v1";\n\nfunction readMentorSessionPrefill() {\n    try {\n        const raw = sessionStorage.getItem(\n            MENTOR_SESSION_PREFILL_KEY,\n        );\n\n        if (!raw) return null;\n\n        sessionStorage.removeItem(\n            MENTOR_SESSION_PREFILL_KEY,\n        );\n\n        const data = JSON.parse(raw);\n        const suggestion = String(\n            data?.suggestion || "",\n        ).trim();\n\n        return suggestion\n            ? { suggestion }\n            : null;\n    } catch {\n        try {\n            sessionStorage.removeItem(\n                MENTOR_SESSION_PREFILL_KEY,\n            );\n        } catch {\n            // Sem ação.\n        }\n\n        return null;\n    }\n}\n\nfunction applyMentorSessionPrefill(container) {\n    const data = readMentorSessionPrefill();\n\n    if (!data) return;\n\n    const form = container.querySelector(\n        "[data-session-form]",\n    );\n\n    if (!form) return;\n\n    const subject = form.elements?.materia;\n    const topic = form.elements?.assunto;\n    const duration = form.elements?.duracao_minutos;\n    const notes = form.elements?.observacoes;\n\n    if (topic) {\n        topic.value = data.suggestion;\n    }\n\n    if (duration && !duration.value) {\n        duration.value = "30";\n    }\n\n    if (notes) {\n        notes.value =\n            "Sessão iniciada a partir de uma sugestão do Mentor.Edu.";\n    }\n\n    form.hidden = false;\n\n    form.scrollIntoView({\n        behavior: "smooth",\n        block: "center",\n    });\n\n    setTimeout(() => {\n        subject?.focus();\n    }, 250);\n\n    showToast(\n        "Sugestão do Mentor carregada. Informe a matéria e registre a sessão.",\n        "success",\n    );\n}\n'
V8_CSS = '\n/* MENTOR_EDU_HANDOFF_V8 */\n.mentor-suggestion-action-buttons button[data-suggestion-plan],\n.mentor-suggestion-action-buttons button[data-suggestion-session] {\n    position: relative;\n}\n\n.mentor-suggestion-action-buttons button[data-suggestion-plan]::after,\n.mentor-suggestion-action-buttons button[data-suggestion-session]::after {\n    content: "→";\n    margin-left: 5px;\n    opacity: .72;\n}\n'

# 1) Confirma Etapa 7.
required = [
    "MENTOR_EDU_ACTIONS_V7",
    "data-suggestion-plan",
    "data-suggestion-session",
    "mentor-edu:study-now",
]

missing = [
    item
    for item in required
    if item not in mentor
]

if missing:
    raise SystemExit(
        "ERRO: Mentor Edu não corresponde à Etapa 7. "
        "Nenhuma alteração foi salva. Faltou: "
        + ", ".join(missing)
    )

# 2) Helpers.
if "MENTOR_EDU_HANDOFF_V8" not in mentor:
    anchor = "function suggestionsMarkup(items) {"
    pos = mentor.find(anchor)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei suggestionsMarkup."
        )

    mentor = (
        mentor[:pos]
        + MENTOR_HELPERS.strip()
        + "\n\n"
        + mentor[pos:]
    )

# 3) Faz os botões carregarem a sugestão escolhida.
if 'data-suggestion-plan="${escapeHtml(title)}"' not in mentor:
    if "data-suggestion-plan" not in mentor:
        raise SystemExit(
            "ERRO: não encontrei o botão Meu plano."
        )

    mentor = mentor.replace(
        "data-suggestion-plan",
        'data-suggestion-plan="${escapeHtml(title)}"',
        1,
    )

if 'data-suggestion-session="${escapeHtml(title)}"' not in mentor:
    if "data-suggestion-session" not in mentor:
        raise SystemExit(
            "ERRO: não encontrei o botão Sessão."
        )

    mentor = mentor.replace(
        "data-suggestion-session",
        'data-suggestion-session="${escapeHtml(title)}"',
        1,
    )

# 4) Guarda sugestão antes de navegar.
if "button.dataset.suggestionPlan" not in mentor:
    if OLD_PLAN_HANDLER not in mentor:
        raise SystemExit(
            "ERRO: não encontrei o clique de Meu plano."
        )

    mentor = mentor.replace(
        OLD_PLAN_HANDLER,
        NEW_PLAN_HANDLER,
        1,
    )

if "button.dataset.suggestionSession" not in mentor:
    if OLD_SESSION_HANDLER not in mentor:
        raise SystemExit(
            "ERRO: não encontrei o clique de Sessão."
        )

    mentor = mentor.replace(
        OLD_SESSION_HANDLER,
        NEW_SESSION_HANDLER,
        1,
    )

# 5) Plano.
if "MENTOR_EDU_PLAN_HANDOFF_V8" not in plans:
    anchor = "function planForm()"
    pos = plans.find(anchor)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei planForm em study-plans.js."
        )

    plans = (
        plans[:pos]
        + PLAN_HELPER.strip()
        + "\n\n"
        + plans[pos:]
    )

if "applyMentorPlanPrefill(container)" not in plans[
    plans.find("export async function renderStudentStudyPlans") :
]:
    old_end = "render([...plans])}"
    new_end = (
        "render([...plans]);"
        "applyMentorPlanPrefill(container)"
        "}"
    )

    if old_end not in plans:
        raise SystemExit(
            "ERRO: não encontrei o final esperado de study-plans.js."
        )

    plans = plans.replace(
        old_end,
        new_end,
        1,
    )

# 6) Sessão.
if "MENTOR_EDU_SESSION_HANDOFF_V8" not in sessions:
    anchor = "function sessionForm()"
    pos = sessions.find(anchor)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei sessionForm em study-sessions.js."
        )

    sessions = (
        sessions[:pos]
        + SESSION_HELPER.strip()
        + "\n\n"
        + sessions[pos:]
    )

if "applyMentorSessionPrefill(container);" not in sessions:
    old_line = "    render([...sessions]);"
    new_line = (
        old_line
        + "\n"
        + "    applyMentorSessionPrefill(container);"
    )

    if old_line not in sessions:
        raise SystemExit(
            "ERRO: não encontrei o render final de study-sessions.js."
        )

    sessions = sessions.replace(
        old_line,
        new_line,
        1,
    )

# 7) CSS.
if "MENTOR_EDU_HANDOFF_V8" not in css:
    css = (
        css.rstrip()
        + "\n\n"
        + V8_CSS.strip()
        + "\n"
    )

# 8) Validação.
checks = {
    "handoff": (
        "MENTOR_EDU_HANDOFF_V8" in mentor
        and "writeMentorHandoff" in mentor
    ),
    "botão plano": (
        'data-suggestion-plan="${escapeHtml(title)}"'
        in mentor
    ),
    "botão sessão": (
        'data-suggestion-session="${escapeHtml(title)}"'
        in mentor
    ),
    "plano": (
        "MENTOR_EDU_PLAN_HANDOFF_V8" in plans
        and "applyMentorPlanPrefill(container)" in plans
    ),
    "sessão": (
        "MENTOR_EDU_SESSION_HANDOFF_V8" in sessions
        and "applyMentorSessionPrefill(container);" in sessions
    ),
    "css": (
        "MENTOR_EDU_HANDOFF_V8" in css
    ),
}

failed = [
    name
    for name, ok in checks.items()
    if not ok
]

if failed:
    raise SystemExit(
        "ERRO: validação da Etapa 8 falhou. "
        "Nenhuma alteração foi salva: "
        + ", ".join(failed)
    )

if (
    mentor == original_mentor
    and plans == original_plans
    and sessions == original_sessions
    and css == original_css
):
    print(
        "ETAPA 8 já está aplicada. "
        "Nenhuma alteração necessária."
    )
    sys.exit(0)

# 9) Backups.
for path, content, suffix in (
    (MENTOR_PAGE, original_mentor, ".backup_etapa8_handoff"),
    (PLAN_PAGE, original_plans, ".backup_etapa8_handoff"),
    (SESSION_PAGE, original_sessions, ".backup_etapa8_handoff"),
    (CSS, original_css, ".backup_etapa8_handoff"),
):
    backup = path.with_name(path.name + suffix)

    if not backup.exists():
        backup.write_text(
            content,
            encoding="utf-8",
        )

MENTOR_PAGE.write_text(mentor, encoding="utf-8")
PLAN_PAGE.write_text(plans, encoding="utf-8")
SESSION_PAGE.write_text(sessions, encoding="utf-8")
CSS.write_text(css, encoding="utf-8")

print()
print("====================================================")
print(" MENTOR.EDU - ETAPA 8 INTEGRAÇÃO DE ESTUDO APLICADA")
print("====================================================")
print()
print("Fluxo conectado:")
print("- Sugestão -> Meu plano -> formulário pré-preenchido")
print("- Sugestão -> Sessão -> formulário pré-preenchido")
print()
print("Segurança:")
print("- nenhum plano é criado sem o aluno salvar")
print("- nenhuma sessão é registrada sem o aluno confirmar")
print("- matéria/matérias continuam sob controle do aluno")
print()
print("Arquivos alterados:")
print("- frontend/js/pages/student/mentor-edu.js")
print("- frontend/js/pages/student/study-plans.js")
print("- frontend/js/pages/student/study-sessions.js")
print("- frontend/css/mentor-ai-page.css")
print()
print("Use Ctrl + F5 e teste Meu plano e Sessão.")
