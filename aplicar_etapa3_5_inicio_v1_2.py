from pathlib import Path
import re

ROOT = Path(".")
DASHBOARD_JS = ROOT / "frontend" / "js" / "pages" / "student" / "dashboard.js"
MENTOR_CSS = ROOT / "frontend" / "css" / "mentor-ai-page.css"
BOT = ROOT / "frontend" / "assets" / "brand" / "mentor-ai-bot.png"

for path in (DASHBOARD_JS, MENTOR_CSS, BOT):
    if not path.exists():
        raise SystemExit(f"Arquivo necessário não encontrado: {path}")

def read(path):
    return path.read_text(encoding="utf-8-sig", errors="strict")

original_js = read(DASHBOARD_JS)
original_css = read(MENTOR_CSS)
js = original_js
css = original_css

JS_MARKER = "MENTOR_EDU_HOME_CARD_V1_2"
CSS_MARKER = "MENTOR_EDU_HOME_VISUAL_V1_2"

home_helper = '\n// MENTOR_EDU_HOME_CARD_V1_2\nfunction mentorEduHomeSection() {\n  return `\n    <section class="mentor-home-card" data-mentor-home>\n      <div class="mentor-home-bot">\n        <img src="assets/brand/mentor-ai-bot.png" alt="Mentor Edu">\n      </div>\n\n      <div class="mentor-home-copy">\n        <span>MENTOR EDU • IA PARA SEUS ESTUDOS</span>\n        <strong>Seu espaço de aprendizagem personalizada</strong>\n        <p>\n          Veja seus pontos fortes, prioridades, plano de estudos e converse\n          com o Mentor quando precisar de uma explicação passo a passo.\n        </p>\n      </div>\n\n      <button type="button" class="mentor-home-open" data-mentor-route="mentor-edu">\n        Abrir Mentor Edu\n        <b aria-hidden="true">→</b>\n      </button>\n    </section>\n\n    <button\n      type="button"\n      class="mentor-home-float"\n      data-mentor-route="mentor-edu"\n      aria-label="Abrir Mentor Edu"\n      title="Abrir Mentor Edu"\n    >\n      <img src="assets/brand/mentor-ai-bot.png" alt="">\n      <span>\n        <small>Mentor Edu</small>\n        <strong>O que vamos estudar hoje?</strong>\n      </span>\n    </button>\n  `;\n}\n\nfunction bindMentorEduHome(container, navigate) {\n  container.querySelectorAll("[data-mentor-route]").forEach(button => {\n    button.addEventListener("click", () => navigate(button.dataset.mentorRoute));\n  });\n}\n\n'
home_css = '\n\n/* MENTOR_EDU_HOME_VISUAL_V1_2 */\n.mentor-home-card {\n    display: grid;\n    grid-template-columns: auto minmax(0, 1fr) auto;\n    align-items: center;\n    gap: 16px;\n    margin: 16px 0 18px;\n    padding: 17px 18px;\n    border: 1px solid #e5dbf5;\n    border-radius: 18px;\n    background:\n        radial-gradient(circle at 94% 10%, rgba(124, 58, 237, .13), transparent 28%),\n        linear-gradient(135deg, #ffffff 0%, #fbf8ff 100%);\n    box-shadow: 0 9px 26px rgba(62, 34, 93, .055);\n}\n\n.mentor-home-bot {\n    overflow: hidden;\n    width: 54px;\n    height: 54px;\n    border-radius: 15px;\n    box-shadow: 0 8px 18px rgba(91, 33, 182, .18);\n}\n\n.mentor-home-bot img,\n.mentor-home-float img {\n    width: 100%;\n    height: 100%;\n    display: block;\n    object-fit: cover;\n}\n\n.mentor-home-copy {\n    min-width: 0;\n}\n\n.mentor-home-copy > span {\n    display: block;\n    margin-bottom: 3px;\n    color: #7c3aed;\n    font-size: 9px;\n    font-weight: 900;\n    letter-spacing: .08em;\n}\n\n.mentor-home-copy > strong {\n    display: block;\n    color: #111827;\n    font-size: 15px;\n}\n\n.mentor-home-copy > p {\n    max-width: 730px;\n    margin: 4px 0 0;\n    color: #6b7280;\n    font-size: 11px;\n    line-height: 1.5;\n}\n\n.mentor-home-open {\n    display: inline-flex;\n    align-items: center;\n    justify-content: center;\n    gap: 8px;\n    min-height: 40px;\n    padding: 0 14px;\n    border: 0;\n    border-radius: 12px;\n    background: linear-gradient(135deg, #7c3aed, #5b21b6);\n    color: #fff;\n    cursor: pointer;\n    font: inherit;\n    font-size: 11px;\n    font-weight: 800;\n    box-shadow: 0 7px 16px rgba(109, 40, 217, .18);\n}\n\n.mentor-home-open b {\n    font-size: 15px;\n}\n\n.mentor-home-float {\n    position: fixed;\n    z-index: 950;\n    right: 22px;\n    bottom: 22px;\n    display: flex;\n    align-items: center;\n    gap: 9px;\n    max-width: 250px;\n    padding: 8px 12px 8px 8px;\n    border: 1px solid rgba(255,255,255,.35);\n    border-radius: 16px;\n    background: linear-gradient(135deg, #5b21b6, #7c3aed);\n    color: #fff;\n    cursor: pointer;\n    box-shadow: 0 15px 36px rgba(76, 29, 149, .28);\n    text-align: left;\n    transition: transform .18s ease, box-shadow .18s ease;\n}\n\n.mentor-home-float:hover {\n    transform: translateY(-2px);\n    box-shadow: 0 18px 42px rgba(76, 29, 149, .34);\n}\n\n.mentor-home-float img {\n    flex: none;\n    width: 38px;\n    height: 38px;\n    border-radius: 11px;\n}\n\n.mentor-home-float span {\n    display: grid;\n    gap: 1px;\n    min-width: 0;\n}\n\n.mentor-home-float small {\n    color: #e9d5ff;\n    font-size: 8px;\n    font-weight: 800;\n    letter-spacing: .06em;\n    text-transform: uppercase;\n}\n\n.mentor-home-float strong {\n    overflow: hidden;\n    color: #fff;\n    font-size: 10px;\n    font-weight: 700;\n    text-overflow: ellipsis;\n    white-space: nowrap;\n}\n\n@media (max-width: 760px) {\n    .mentor-home-card {\n        grid-template-columns: auto minmax(0, 1fr);\n    }\n\n    .mentor-home-open {\n        grid-column: 1 / -1;\n        width: 100%;\n    }\n\n    .mentor-home-float {\n        right: 12px;\n        bottom: 12px;\n        max-width: 56px;\n        padding: 8px;\n        border-radius: 16px;\n    }\n\n    .mentor-home-float span {\n        display: none;\n    }\n}\n'

# 1) O dashboard atual tem shortcutsSection() e renderStudentDashboard.
if "function shortcutsSection()" not in js:
    raise SystemExit(
        "Não encontrei function shortcutsSection() no dashboard.js. "
        "Nenhuma alteração foi gravada."
    )

if "export async function renderStudentDashboard" not in js:
    raise SystemExit(
        "Não encontrei renderStudentDashboard no dashboard.js. "
        "Nenhuma alteração foi gravada."
    )

# 2) Helper antes do export.
if JS_MARKER not in js:
    anchor = "export async function renderStudentDashboard"
    pos = js.find(anchor)
    if pos < 0:
        raise SystemExit("Não encontrei o ponto de inserção do helper.")
    js = js[:pos] + home_helper + js[pos:]

# 3) Card: imediatamente ANTES de shortcutsSection().
if "${mentorEduHomeSection()}" not in js:
    target = "${shortcutsSection()}"
    if target not in js:
        raise SystemExit(
            "Não encontrei ${shortcutsSection()} no template do dashboard. "
            "Nenhuma alteração foi gravada."
        )
    js = js.replace(
        target,
        "${mentorEduHomeSection()}${shortcutsSection()}",
        1,
    )

# 4) Binding: regex tolerante a espaços e CRLF/LF.
binding_call = "bindMentorEduHome(container, navigate);"
if binding_call not in js:
    pattern = r"(\s*bindShortcutRoutes\s*\(\s*container\s*,\s*navigate\s*\)\s*;)"
    match = re.search(pattern, js)
    if not match:
        raise SystemExit(
            "Não encontrei bindShortcutRoutes(container,navigate) no dashboard.js. "
            "Nenhuma alteração foi gravada."
        )

    indent_match = re.match(r"\s*", match.group(1))
    indent = indent_match.group(0) if indent_match else "\n  "
    replacement = match.group(1) + indent + binding_call
    js = js[:match.start()] + replacement + js[match.end():]

# 5) CSS.
if CSS_MARKER not in css:
    css = css.rstrip() + home_css + "\n"

# 6) Validação ANTES de gravar.
checks = {
    "helper": JS_MARKER in js,
    "card": "${mentorEduHomeSection()}${shortcutsSection()}" in js,
    "binding": binding_call in js,
    "css": CSS_MARKER in css,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit(
        "Falha na validação final. Nenhum arquivo foi gravado: "
        + ", ".join(failed)
    )

# 7) Backup + gravação só depois das validações.
backup_js = DASHBOARD_JS.with_name(DASHBOARD_JS.name + ".backup_mentor_inicio_v1_2")
backup_css = MENTOR_CSS.with_name(MENTOR_CSS.name + ".backup_mentor_inicio_v1_2")
if not backup_js.exists():
    backup_js.write_text(original_js, encoding="utf-8")
if not backup_css.exists():
    backup_css.write_text(original_css, encoding="utf-8")

DASHBOARD_JS.write_text(js, encoding="utf-8")
MENTOR_CSS.write_text(css, encoding="utf-8")

print("")
print("ETAPA 3.5 V1.2 — MENTOR EDU NO INÍCIO APLICADO COM SUCESSO.")
print("")
print("Alterados somente:")
print("- frontend/js/pages/student/dashboard.js")
print("- frontend/css/mentor-ai-page.css")
print("")
print("No Início agora deve existir:")
print("- 3 cards dinâmicos existentes")
print("- card compacto Mentor Edu")
print("- Atalhos rápidos existentes")
print("- bolha flutuante Mentor Edu")
print("")
print("Card e bolha abrem #/mentor-edu.")
print("Use Ctrl + F5.")
