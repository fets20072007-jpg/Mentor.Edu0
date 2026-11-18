from pathlib import Path

ROOT = Path('.')
DASHBOARD_JS = ROOT / 'frontend' / 'js' / 'pages' / 'student' / 'dashboard.js'
MENTOR_CSS = ROOT / 'frontend' / 'css' / 'mentor-ai-page.css'
BOT = ROOT / 'frontend' / 'assets' / 'brand' / 'mentor-ai-bot.png'

for path in (DASHBOARD_JS, MENTOR_CSS, BOT):
    if not path.exists():
        raise SystemExit(f'Arquivo necessário não encontrado: {path}\nConfirme que a Etapa 3 V1.1 foi aplicada.')

def read(path):
    return path.read_text(encoding='utf-8-sig', errors='strict')

def backup_once(path, suffix):
    backup = path.with_name(path.name + suffix)
    if not backup.exists():
        backup.write_text(read(path), encoding='utf-8')

js = read(DASHBOARD_JS)
css = read(MENTOR_CSS)

backup_once(DASHBOARD_JS, '.backup_mentor_inicio_v1')
backup_once(MENTOR_CSS, '.backup_mentor_inicio_v1')

JS_MARKER = 'MENTOR_EDU_HOME_CARD_V1'
CSS_MARKER = 'MENTOR_EDU_HOME_VISUAL_V1'

home_helper = '\n// MENTOR_EDU_HOME_CARD_V1\nfunction mentorEduHomeSection() {\n  return `\n    <section class="mentor-home-card" data-mentor-home>\n      <div class="mentor-home-bot">\n        <img src="assets/brand/mentor-ai-bot.png" alt="Mentor Edu">\n      </div>\n\n      <div class="mentor-home-copy">\n        <span>MENTOR EDU • IA PARA SEUS ESTUDOS</span>\n        <strong>Seu espaço de aprendizagem personalizada</strong>\n        <p>\n          Veja seus pontos fortes, prioridades, plano de estudos e converse\n          com o Mentor quando precisar de uma explicação passo a passo.\n        </p>\n      </div>\n\n      <button type="button" class="mentor-home-open" data-mentor-route="mentor-edu">\n        Abrir Mentor Edu\n        <b aria-hidden="true">→</b>\n      </button>\n    </section>\n\n    <button\n      type="button"\n      class="mentor-home-float"\n      data-mentor-route="mentor-edu"\n      aria-label="Abrir Mentor Edu"\n      title="Abrir Mentor Edu"\n    >\n      <img src="assets/brand/mentor-ai-bot.png" alt="">\n      <span>\n        <small>Mentor Edu</small>\n        <strong>O que vamos estudar hoje?</strong>\n      </span>\n    </button>\n  `;\n}\n\nfunction bindMentorEduHome(container, navigate) {\n  container.querySelectorAll("[data-mentor-route]").forEach(button => {\n    button.addEventListener("click", () => navigate(button.dataset.mentorRoute));\n  });\n}\n\n'
home_css = '\n\n/* MENTOR_EDU_HOME_VISUAL_V1 */\n.mentor-home-card {\n    display: grid;\n    grid-template-columns: auto minmax(0, 1fr) auto;\n    align-items: center;\n    gap: 16px;\n    margin: 16px 0 18px;\n    padding: 17px 18px;\n    border: 1px solid #e5dbf5;\n    border-radius: 18px;\n    background:\n        radial-gradient(circle at 94% 10%, rgba(124, 58, 237, .13), transparent 28%),\n        linear-gradient(135deg, #ffffff 0%, #fbf8ff 100%);\n    box-shadow: 0 9px 26px rgba(62, 34, 93, .055);\n}\n\n.mentor-home-bot {\n    overflow: hidden;\n    width: 54px;\n    height: 54px;\n    border-radius: 15px;\n    box-shadow: 0 8px 18px rgba(91, 33, 182, .18);\n}\n\n.mentor-home-bot img,\n.mentor-home-float img {\n    width: 100%;\n    height: 100%;\n    display: block;\n    object-fit: cover;\n}\n\n.mentor-home-copy {\n    min-width: 0;\n}\n\n.mentor-home-copy > span {\n    display: block;\n    margin-bottom: 3px;\n    color: #7c3aed;\n    font-size: 9px;\n    font-weight: 900;\n    letter-spacing: .08em;\n}\n\n.mentor-home-copy > strong {\n    display: block;\n    color: #111827;\n    font-size: 15px;\n}\n\n.mentor-home-copy > p {\n    max-width: 730px;\n    margin: 4px 0 0;\n    color: #6b7280;\n    font-size: 11px;\n    line-height: 1.5;\n}\n\n.mentor-home-open {\n    display: inline-flex;\n    align-items: center;\n    justify-content: center;\n    gap: 8px;\n    min-height: 40px;\n    padding: 0 14px;\n    border: 0;\n    border-radius: 12px;\n    background: linear-gradient(135deg, #7c3aed, #5b21b6);\n    color: #fff;\n    cursor: pointer;\n    font: inherit;\n    font-size: 11px;\n    font-weight: 800;\n    box-shadow: 0 7px 16px rgba(109, 40, 217, .18);\n}\n\n.mentor-home-open b {\n    font-size: 15px;\n}\n\n.mentor-home-float {\n    position: fixed;\n    z-index: 950;\n    right: 22px;\n    bottom: 22px;\n    display: flex;\n    align-items: center;\n    gap: 9px;\n    max-width: 250px;\n    padding: 8px 12px 8px 8px;\n    border: 1px solid rgba(255,255,255,.35);\n    border-radius: 16px;\n    background: linear-gradient(135deg, #5b21b6, #7c3aed);\n    color: #fff;\n    cursor: pointer;\n    box-shadow: 0 15px 36px rgba(76, 29, 149, .28);\n    text-align: left;\n    transition: transform .18s ease, box-shadow .18s ease;\n}\n\n.mentor-home-float:hover {\n    transform: translateY(-2px);\n    box-shadow: 0 18px 42px rgba(76, 29, 149, .34);\n}\n\n.mentor-home-float img {\n    flex: none;\n    width: 38px;\n    height: 38px;\n    border-radius: 11px;\n}\n\n.mentor-home-float span {\n    display: grid;\n    gap: 1px;\n    min-width: 0;\n}\n\n.mentor-home-float small {\n    color: #e9d5ff;\n    font-size: 8px;\n    font-weight: 800;\n    letter-spacing: .06em;\n    text-transform: uppercase;\n}\n\n.mentor-home-float strong {\n    overflow: hidden;\n    color: #fff;\n    font-size: 10px;\n    font-weight: 700;\n    text-overflow: ellipsis;\n    white-space: nowrap;\n}\n\n@media (max-width: 760px) {\n    .mentor-home-card {\n        grid-template-columns: auto minmax(0, 1fr);\n    }\n\n    .mentor-home-open {\n        grid-column: 1 / -1;\n        width: 100%;\n    }\n\n    .mentor-home-float {\n        right: 12px;\n        bottom: 12px;\n        max-width: 56px;\n        padding: 8px;\n        border-radius: 16px;\n    }\n\n    .mentor-home-float img {\n        width: 38px;\n        height: 38px;\n    }\n\n    .mentor-home-float span {\n        display: none;\n    }\n}\n'

if JS_MARKER not in js:
    anchor = 'export async function renderStudentDashboard(container, user, navigate) {'
    if anchor not in js:
        raise SystemExit('Não encontrei renderStudentDashboard em dashboard.js. Nenhuma alteração foi aplicada.')
    js = js.replace(anchor, home_helper + anchor, 1)

if '${mentorEduHomeSection()}' not in js:
    dynamic_anchor = '])}${shortcutsSection()}`;'
    if dynamic_anchor in js:
        js = js.replace(dynamic_anchor, '])}${mentorEduHomeSection()}${shortcutsSection()}`;', 1)
    else:
        old_anchor = '    bindDashboardShortcuts(container, navigate);'
        if old_anchor in js:
            js = js.replace(old_anchor, '    container.insertAdjacentHTML("beforeend", mentorEduHomeSection());\n' + old_anchor, 1)
        else:
            raise SystemExit('Não consegui identificar o ponto onde inserir o card do Mentor Edu no dashboard.js.')

if 'bindMentorEduHome(container, navigate);' not in js:
    anchor = "  startRotatingCard(container,'student-grades',notes);"
    if anchor in js:
        js = js.replace(anchor, '  bindMentorEduHome(container, navigate);\n' + anchor, 1)
    else:
        anchor = '    bindDashboardShortcuts(container, navigate);'
        if anchor in js:
            js = js.replace(anchor, anchor + '\n    bindMentorEduHome(container, navigate);', 1)
        else:
            raise SystemExit('Não encontrei ponto seguro para ativar os botões do Mentor Edu.')

if CSS_MARKER not in css:
    css = css.rstrip() + home_css + '\n'

checks = {
    'helper do card': JS_MARKER in js,
    'card inserido': '${mentorEduHomeSection()}' in js or 'insertAdjacentHTML("beforeend", mentorEduHomeSection())' in js,
    'binding inserido': 'bindMentorEduHome(container, navigate);' in js,
    'CSS': CSS_MARKER in css,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('Validação falhou. Nenhum arquivo foi gravado: ' + ', '.join(failed))

DASHBOARD_JS.write_text(js, encoding='utf-8')
MENTOR_CSS.write_text(css, encoding='utf-8')

print('')
print('ETAPA 3.5 — MENTOR EDU NO INÍCIO APLICADA COM SUCESSO.')
print('')
print('Alterados SOMENTE:')
print('- frontend/js/pages/student/dashboard.js')
print('- frontend/css/mentor-ai-page.css')
print('')
print('Adicionado ao Início:')
print('- card compacto Mentor Edu')
print('- botão Abrir Mentor Edu')
print('- bolha flutuante no canto inferior direito')
print('')
print('NÃO foram alterados: login, main.js, router.js, sidebar.js, backend ou IA.')
print('Use Ctrl + F5 e teste o Início.')
