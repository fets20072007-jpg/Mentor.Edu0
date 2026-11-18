from pathlib import Path
import sys

ROOT = Path.cwd()

PAGE = (
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
    / "mentor-ai-page.css"
)

for path in (PAGE, CSS):
    if not path.exists():
        raise SystemExit(
            f"ERRO: arquivo necessário não encontrado: {path}"
        )

def read(path):
    return path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

page = read(PAGE)
css = read(CSS)

original_page = page
original_css = css

NEW_SUGGESTIONS = 'function suggestionsMarkup(items) {\n    const normalized = normalizeList(items);\n\n    if (!normalized.length) {\n        return `\n            <div class="mentor-empty-state">\n                <strong>Sem sugestões novas por enquanto.</strong>\n                <p>O Mentor vai criar ações assim que houver dados suficientes do seu perfil.</p>\n            </div>\n        `;\n    }\n\n    return `\n        <div class="mentor-suggestion-stack mentor-suggestion-stack--actions">\n            ${normalized.map((item, index) => {\n                const { title, detail } = itemParts(item);\n\n                return `\n                    <article class="mentor-suggestion-action-card">\n                        <div class="mentor-suggestion-action-head">\n                            <span>${String(index + 1).padStart(2, "0")}</span>\n\n                            <div>\n                                <strong>${escapeHtml(title)}</strong>\n                                ${\n                                    detail\n                                        ? `<p>${escapeHtml(detail)}</p>`\n                                        : `<p>Sugestão criada a partir do seu perfil.</p>`\n                                }\n                            </div>\n                        </div>\n\n                        <div class="mentor-suggestion-action-buttons">\n                            <button\n                                type="button"\n                                class="is-primary"\n                                data-suggestion-chat="${escapeHtml(title)}"\n                            >\n                                Estudar agora\n                            </button>\n\n                            <button\n                                type="button"\n                                data-suggestion-plan\n                            >\n                                Meu plano\n                            </button>\n\n                            <button\n                                type="button"\n                                data-suggestion-session\n                            >\n                                Sessão\n                            </button>\n                        </div>\n                    </article>\n                `;\n            }).join("")}\n        </div>\n    `;\n}'
OLD_APPLY_HANDLER = '    page.querySelectorAll("[data-real-suggestion]").forEach(button => {\n        button.addEventListener("click", () => {\n            const chat = page.querySelector("[data-mentor-chat]");\n            chat?.classList.add("is-open");\n            chat?.scrollIntoView({ behavior: "smooth", block: "center" });\n\n            const input = chat?.querySelector("input");\n            if (input) {\n                input.value = button.dataset.realSuggestion || "";\n                setTimeout(() => input.focus(), 250);\n            }\n\n            showToast(page, "Sugestão carregada no chat.");\n        });\n    });'
NEW_APPLY_HANDLER = '    // MENTOR_EDU_ACTIONS_V7\n    page.querySelectorAll("[data-suggestion-chat]").forEach(button => {\n        button.addEventListener("click", () => {\n            const suggestion =\n                button.dataset.suggestionChat ||\n                "";\n\n            page.dispatchEvent(\n                new CustomEvent(\n                    "mentor-edu:study-now",\n                    {\n                        detail: {\n                            suggestion,\n                        },\n                    },\n                ),\n            );\n        });\n    });\n\n    page.querySelectorAll("[data-suggestion-plan]").forEach(button => {\n        button.addEventListener("click", () => {\n            navigate("study-plans");\n        });\n    });\n\n    page.querySelectorAll("[data-suggestion-session]").forEach(button => {\n        button.addEventListener("click", () => {\n            navigate("study-sessions");\n        });\n    });'
STUDY_NOW_HANDLER = '\n    const onStudyNow = event => {\n        const suggestion =\n            String(\n                event?.detail?.suggestion ??\n                "",\n            ).trim();\n\n        if (!suggestion) return;\n\n        const prompt =\n            "Quero estudar agora esta recomendação do meu perfil: "\n            + suggestion\n            + ". Faça uma revisão curta e didática do ponto principal, "\n            + "depois proponha 2 exercícios progressivos para eu praticar. "\n            + "Não entregue as respostas dos exercícios antes de eu tentar.";\n\n        sendTutorMessage(prompt);\n    };\n\n    page.addEventListener(\n        "mentor-edu:study-now",\n        onStudyNow,\n    );\n'
OLD_AVERAGE_BLOCK = '    const averageRaw =\n        metrics?.media_geral ??\n        metrics?.media ??\n        metrics?.average ??\n        metrics?.nota_media ??\n        null;\n\n    const attendanceRaw =\n        metrics?.frequencia_percentual ??\n        metrics?.frequencia ??\n        metrics?.attendance ??\n        metrics?.presenca ??\n        null;'
NEW_AVERAGE_BLOCK = '    // MENTOR_EDU_PROFILE_METRICS_V7\n    const averageRaw =\n        metrics?.media_geral_percentual ??\n        metrics?.media_geral ??\n        metrics?.media ??\n        metrics?.average ??\n        metrics?.nota_media ??\n        null;\n\n    const attendanceRaw =\n        metrics?.frequencia?.taxa_presenca ??\n        metrics?.frequencia?.percentual ??\n        metrics?.frequencia_percentual ??\n        metrics?.attendance ??\n        metrics?.presenca ??\n        null;'
V7_CSS = '\n/* MENTOR_EDU_ACTIONS_V7 */\n.mentor-suggestion-stack--actions {\n    display: grid;\n    gap: 12px;\n}\n\n.mentor-suggestion-action-card {\n    border: 1px solid #e7def1;\n    border-radius: 16px;\n    background: #fff;\n    padding: 14px;\n}\n\n.mentor-suggestion-action-head {\n    display: grid;\n    grid-template-columns: 34px minmax(0, 1fr);\n    gap: 11px;\n    align-items: start;\n}\n\n.mentor-suggestion-action-head > span {\n    display: grid;\n    place-items: center;\n    width: 34px;\n    height: 34px;\n    border-radius: 11px;\n    background: #f2e9ff;\n    color: #6d28d9;\n    font-size: 10px;\n    font-weight: 900;\n}\n\n.mentor-suggestion-action-head strong {\n    display: block;\n    color: #2f2738;\n    font-size: 12px;\n    line-height: 1.35;\n}\n\n.mentor-suggestion-action-head p {\n    margin: 5px 0 0;\n    color: #746a7d;\n    font-size: 10px;\n    line-height: 1.5;\n}\n\n.mentor-suggestion-action-buttons {\n    display: flex;\n    flex-wrap: wrap;\n    gap: 8px;\n    margin-top: 12px;\n    padding-left: 45px;\n}\n\n.mentor-suggestion-action-buttons button {\n    min-height: 34px;\n    padding: 0 11px;\n    border: 1px solid #ddd3e8;\n    border-radius: 10px;\n    background: #fff;\n    color: #6d28d9;\n    cursor: pointer;\n    font: inherit;\n    font-size: 9px;\n    font-weight: 900;\n}\n\n.mentor-suggestion-action-buttons button:hover {\n    border-color: #c4b5fd;\n    background: #faf8ff;\n}\n\n.mentor-suggestion-action-buttons button.is-primary {\n    border-color: #6d28d9;\n    background: #6d28d9;\n    color: #fff;\n}\n\n.mentor-suggestion-action-buttons button.is-primary:hover {\n    background: #5b21b6;\n}\n\n@media (max-width: 620px) {\n    .mentor-suggestion-action-buttons {\n        padding-left: 0;\n    }\n}\n'

required = [
    "MENTOR_EDU_CHAT_REAL_V5",
    "function suggestionsMarkup",
    "function applyProfileData",
    "async function loadStudentProfile",
    "async function sendTutorMessage",
]

missing = [
    item
    for item in required
    if item not in page
]

if missing:
    raise SystemExit(
        "ERRO: a página Mentor Edu não corresponde à base esperada. "
        "Nada foi salvo. Faltou: "
        + ", ".join(missing)
    )

# 1. Corrige média e frequência do perfil.
if "MENTOR_EDU_PROFILE_METRICS_V7" not in page:
    if OLD_AVERAGE_BLOCK not in page:
        raise SystemExit(
            "ERRO: não encontrei o bloco de métricas do perfil. "
            "Nada foi salvo."
        )

    page = page.replace(
        OLD_AVERAGE_BLOCK,
        NEW_AVERAGE_BLOCK,
        1,
    )

# 2. Substitui o visual das sugestões por cards acionáveis.
if "mentor-suggestion-stack--actions" not in page:
    start = page.find(
        "function suggestionsMarkup(items) {"
    )

    end = page.find(
        "function loadingMarkup",
        start,
    )

    if start == -1 or end == -1:
        raise SystemExit(
            "ERRO: não encontrei suggestionsMarkup de forma segura. "
            "Nada foi salvo."
        )

    page = (
        page[:start]
        + NEW_SUGGESTIONS.strip()
        + "\n\n"
        + page[end:]
    )

# 3. applyProfileData passa a receber navigate.
page = page.replace(
    "function applyProfileData(page, data) {",
    "function applyProfileData(page, data, navigate) {",
    1,
)

# 4. Conecta as novas ações.
if "MENTOR_EDU_ACTIONS_V7" not in page:
    if OLD_APPLY_HANDLER not in page:
        raise SystemExit(
            "ERRO: não encontrei o manipulador antigo das sugestões. "
            "Nada foi salvo."
        )

    page = page.replace(
        OLD_APPLY_HANDLER,
        NEW_APPLY_HANDLER,
        1,
    )

# 5. loadStudentProfile recebe navigate e repassa.
page = page.replace(
    "async function loadStudentProfile(page, user, { force = false } = {}) {",
    "async function loadStudentProfile(page, user, navigate, { force = false } = {}) {",
    1,
)

page = page.replace(
    "applyProfileData(page, data);",
    "applyProfileData(page, data, navigate);",
    1,
)

page = page.replace(
    "loadStudentProfile(page, user, { force: true });",
    "loadStudentProfile(page, user, navigate, { force: true });",
)

page = page.replace(
    "loadStudentProfile(page, user);",
    "loadStudentProfile(page, user, navigate);",
)

# 6. Evento "Estudar agora" aciona o Tutor.
if '"mentor-edu:study-now"' not in page[
    page.find("async function sendTutorMessage") :
]:
    anchor = '    chatForm?.addEventListener("submit", event => {'

    pos = page.find(anchor)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei o ponto seguro após sendTutorMessage. "
            "Nada foi salvo."
        )

    page = (
        page[:pos]
        + STUDY_NOW_HANDLER
        + "\n"
        + page[pos:]
    )

# 7. Limpa listener quando sai da página.
observer_line = (
    '            document.removeEventListener("keydown", onKeyDown);'
)

observer_new = (
    observer_line
    + "\n"
    + '            page.removeEventListener("mentor-edu:study-now", onStudyNow);'
)

if (
    observer_line in page
    and 'page.removeEventListener("mentor-edu:study-now", onStudyNow);'
    not in page
):
    page = page.replace(
        observer_line,
        observer_new,
        1,
    )

# 8. CSS.
if "MENTOR_EDU_ACTIONS_V7" not in css:
    css = (
        css.rstrip()
        + "\n\n"
        + V7_CSS.strip()
        + "\n"
    )

checks = {
    "métrica média": (
        "media_geral_percentual"
        in page
    ),
    "métrica frequência": (
        "frequencia?.taxa_presenca"
        in page
    ),
    "ações sugestão": (
        "data-suggestion-chat"
        in page
        and "data-suggestion-plan"
        in page
        and "data-suggestion-session"
        in page
    ),
    "estudar agora": (
        "mentor-edu:study-now"
        in page
        and "sendTutorMessage(prompt)"
        in page
    ),
    "navegação plano": (
        'navigate("study-plans")'
        in page
    ),
    "navegação sessão": (
        'navigate("study-sessions")'
        in page
    ),
    "css": (
        "MENTOR_EDU_ACTIONS_V7"
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
        "ERRO: validação da Etapa 7 falhou. "
        "Nada foi salvo: "
        + ", ".join(failed)
    )

if (
    page == original_page
    and css == original_css
):
    print(
        "ETAPA 7 já parece estar aplicada. "
        "Nenhuma alteração necessária."
    )
    sys.exit(0)

page_backup = PAGE.with_name(
    PAGE.name
    + ".backup_etapa7_acoes"
)

css_backup = CSS.with_name(
    CSS.name
    + ".backup_etapa7_acoes"
)

if not page_backup.exists():
    page_backup.write_text(
        original_page,
        encoding="utf-8",
    )

if not css_backup.exists():
    css_backup.write_text(
        original_css,
        encoding="utf-8",
    )

PAGE.write_text(
    page,
    encoding="utf-8",
)

CSS.write_text(
    css,
    encoding="utf-8",
)

print()
print("====================================================")
print(" MENTOR.EDU - ETAPA 7 AÇÕES DE ESTUDO APLICADA")
print("====================================================")
print()
print("Alterados:")
print("- frontend/js/pages/student/mentor-edu.js")
print("- frontend/css/mentor-ai-page.css")
print()
print("Novo comportamento:")
print("- Sugestões do Mentor agora possuem ações reais")
print("- Estudar agora abre o Tutor e inicia uma revisão")
print("- Meu plano abre a área de plano de estudos")
print("- Sessão abre a área de sessões de estudo")
print()
print("Correção incluída:")
print("- Média geral lê media_geral_percentual")
print("- Frequência lê frequencia.taxa_presenca")
print()
print("Nenhum endpoint existente foi substituído.")
print()
print("Use Ctrl + F5 e teste Sugestões do Mentor.")
