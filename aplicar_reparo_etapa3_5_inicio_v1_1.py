from pathlib import Path

ROOT = Path('.')
DASHBOARD_JS = ROOT / 'frontend' / 'js' / 'pages' / 'student' / 'dashboard.js'
MENTOR_CSS = ROOT / 'frontend' / 'css' / 'mentor-ai-page.css'
BOT = ROOT / 'frontend' / 'assets' / 'brand' / 'mentor-ai-bot.png'

for path in (DASHBOARD_JS, MENTOR_CSS, BOT):
    if not path.exists():
        raise SystemExit(f'Arquivo necessário não encontrado: {path}')

def read(path):
    return path.read_text(encoding='utf-8-sig', errors='strict')

original_js = read(DASHBOARD_JS)
original_css = read(MENTOR_CSS)
js = original_js
css = original_css

JS_MARKER = 'MENTOR_EDU_HOME_CARD_V1_1'
CSS_MARKER = 'MENTOR_EDU_HOME_VISUAL_V1_1'
home_helper = '\n// MENTOR_EDU_HOME_CARD_V1_1\nfunction mentorEduHomeSection() {\n  return `\n    <section class="mentor-home-card" data-mentor-home>\n      <div class="mentor-home-bot">\n        <img src="assets/brand/mentor-ai-bot.png" alt="Mentor Edu">\n      </div>\n\n      <div class="mentor-home-copy">\n        <span>MENTOR EDU • IA PARA SEUS ESTUDOS</span>\n        <strong>Seu espaço de aprendizagem personalizada</strong>\n        <p>\n          Veja seus pontos fortes, prioridades, plano de estudos e converse\n          com o Mentor quando precisar de uma explicação passo a passo.\n        </p>\n      </div>\n\n      <button type="button" class="mentor-home-open" data-mentor-route="mentor-edu">\n        Abrir Mentor Edu\n        <b aria-hidden="true">→</b>\n      </button>\n    </section>\n\n    <button\n      type="button"\n      class="mentor-home-float"\n      data-mentor-route="mentor-edu"\n      aria-label="Abrir Mentor Edu"\n      title="Abrir Mentor Edu"\n    >\n      <img src="assets/brand/mentor-ai-bot.png" alt="">\n      <span>\n        <small>Mentor Edu</small>\n        <strong>O que vamos estudar hoje?</strong>\n      </span>\n    </button>\n  `;\n}\n\nfunction bindMentorEduHome(container, navigate) {\n  container.querySelectorAll("[data-mentor-route]").forEach(button => {\n    button.addEventListener("click", () => navigate(button.dataset.mentorRoute));\n  });\n}\n\n'
home_css = '\n\n/* MENTOR_EDU_HOME_VISUAL_V1_1 */\n.mentor-home-card {\n    display: grid;\n    grid-template-columns: auto minmax(0, 1fr) auto;\n    align-items: center;\n    gap: 16px;\n    margin: 16px 0 18px;\n    padding: 17px 18px;\n    border: 1px solid #e5dbf5;\n    border-radius: 18px;\n    background:\n        radial-gradient(circle at 94% 10%, rgba(124, 58, 237, .13), transparent 28%),\n        linear-gradient(135deg, #ffffff 0%, #fbf8ff 100%);\n    box-shadow: 0 9px 26px rgba(62, 34, 93, .055);\n}\n\n.mentor-home-bot {\n    overflow: hidden;\n    width: 54px;\n    height: 54px;\n    border-radius: 15px;\n    box-shadow: 0 8px 18px rgba(91, 33, 182, .18);\n}\n\n.mentor-home-bot img,\n.mentor-home-float img {\n    width: 100%;\n    height: 100%;\n    display: block;\n    object-fit: cover;\n}\n\n.mentor-home-copy {\n    min-width: 0;\n}\n\n.mentor-home-copy > span {\n    display: block;\n    margin-bottom: 3px;\n    color: #7c3aed;\n    font-size: 9px;\n    font-weight: 900;\n    letter-spacing: .08em;\n}\n\n.mentor-home-copy > strong {\n    display: block;\n    color: #111827;\n    font-size: 15px;\n}\n\n.mentor-home-copy > p {\n    max-width: 730px;\n    margin: 4px 0 0;\n    color: #6b7280;\n    font-size: 11px;\n    line-height: 1.5;\n}\n\n.mentor-home-open {\n    display: inline-flex;\n    align-items: center;\n    justify-content: center;\n    gap: 8px;\n    min-height: 40px;\n    padding: 0 14px;\n    border: 0;\n    border-radius: 12px;\n    background: linear-gradient(135deg, #7c3aed, #5b21b6);\n    color: #fff;\n    cursor: pointer;\n    font: inherit;\n    font-size: 11px;\n    font-weight: 800;\n    box-shadow: 0 7px 16px rgba(109, 40, 217, .18);\n}\n\n.mentor-home-open b {\n    font-size: 15px;\n}\n\n.mentor-home-float {\n    position: fixed;\n    z-index: 950;\n    right: 22px;\n    bottom: 22px;\n    display: flex;\n    align-items: center;\n    gap: 9px;\n    max-width: 250px;\n    padding: 8px 12px 8px 8px;\n    border: 1px solid rgba(255,255,255,.35);\n    border-radius: 16px;\n    background: linear-gradient(135deg, #5b21b6, #7c3aed);\n    color: #fff;\n    cursor: pointer;\n    box-shadow: 0 15px 36px rgba(76, 29, 149, .28);\n    text-align: left;\n    transition: transform .18s ease, box-shadow .18s ease;\n}\n\n.mentor-home-float:hover {\n    transform: translateY(-2px);\n    box-shadow: 0 18px 42px rgba(76, 29, 149, .34);\n}\n\n.mentor-home-float img {\n    flex: none;\n    width: 38px;\n    height: 38px;\n    border-radius: 11px;\n}\n\n.mentor-home-float span {\n    display: grid;\n    gap: 1px;\n    min-width: 0;\n}\n\n.mentor-home-float small {\n    color: #e9d5ff;\n    font-size: 8px;\n    font-weight: 800;\n    letter-spacing: .06em;\n    text-transform: uppercase;\n}\n\n.mentor-home-float strong {\n    overflow: hidden;\n    color: #fff;\n    font-size: 10px;\n    font-weight: 700;\n    text-overflow: ellipsis;\n    white-space: nowrap;\n}\n\n@media (max-width: 760px) {\n    .mentor-home-card {\n        grid-template-columns: auto minmax(0, 1fr);\n    }\n\n    .mentor-home-open {\n        grid-column: 1 / -1;\n        width: 100%;\n    }\n\n    .mentor-home-float {\n        right: 12px;\n        bottom: 12px;\n        max-width: 56px;\n        padding: 8px;\n        border-radius: 16px;\n    }\n\n    .mentor-home-float span {\n        display: none;\n    }\n}\n'

# 1) Adiciona helper antes da área de render, sem depender da assinatura exata.
if JS_MARKER not in js:
    candidates = [
        js.find('export async function '),
        js.find('export function '),
        js.find('export const '),
        js.find('export let '),
    ]
    candidates = [p for p in candidates if p >= 0]
    if not candidates:
        raise SystemExit('Não encontrei nenhuma função exportada em dashboard.js. Nenhuma alteração foi gravada.')
    insert_at = min(candidates)
    js = js[:insert_at] + home_helper + js[insert_at:]

# 2) Coloca o card imediatamente antes de Atalhos rápidos.
markup_inserted = ('${mentorEduHomeSection()}' in js)
if not markup_inserted:
    if '${shortcutsSection()}' in js:
        js = js.replace('${shortcutsSection()}', '${mentorEduHomeSection()}${shortcutsSection()}', 1)
        markup_inserted = True

# Fallback: se o HTML não usa shortcutsSection() no template, injeta pelo DOM antes da seção.
dom_injection = (
    '  const mentorShortcuts = container.querySelector(".dashboard-shortcuts-section");\n'
    '  if (mentorShortcuts) {\n'
    '    mentorShortcuts.insertAdjacentHTML("beforebegin", mentorEduHomeSection());\n'
    '  } else {\n'
    '    container.insertAdjacentHTML("beforeend", mentorEduHomeSection());\n'
    '  }\n'
)
if not markup_inserted and 'mentorShortcuts.insertAdjacentHTML' not in js:
    bind_candidates = [
        '  bindShortcutRoutes(container,navigate);\n',
        '  bindShortcutRoutes(container, navigate);\n',
        '    bindDashboardShortcuts(container, navigate);\n',
        '  bindDashboardShortcuts(container, navigate);\n',
    ]
    bind_anchor = next((a for a in bind_candidates if a in js), None)
    if bind_anchor:
        js = js.replace(bind_anchor, dom_injection + bind_anchor, 1)
        markup_inserted = True

if not markup_inserted:
    raise SystemExit(
        'Não reconheci onde ficam os Atalhos rápidos no dashboard.js. '
        'Nenhuma alteração foi gravada.\n\n'
        'Para diagnóstico rode:\n'
        'Get-Content .\\frontend\\js\\pages\\student\\dashboard.js -TotalCount 160'
    )

# 3) Ativa navegação dos botões Mentor Edu.
if 'bindMentorEduHome(container, navigate);' not in js:
    bind_candidates = [
        '  bindShortcutRoutes(container,navigate);\n',
        '  bindShortcutRoutes(container, navigate);\n',
        '    bindDashboardShortcuts(container, navigate);\n',
        '  bindDashboardShortcuts(container, navigate);\n',
    ]
    bind_anchor = next((a for a in bind_candidates if a in js), None)
    if bind_anchor:
        js = js.replace(bind_anchor, bind_anchor + '  bindMentorEduHome(container, navigate);\n', 1)
    else:
        rotate = '  startRotatingCard(container,'
        pos = js.find(rotate)
        if pos >= 0:
            js = js[:pos] + '  bindMentorEduHome(container, navigate);\n' + js[pos:]
        else:
            raise SystemExit('Não encontrei ponto seguro para ligar os botões. Nenhuma alteração foi gravada.')

# 4) CSS.
if CSS_MARKER not in css:
    css = css.rstrip() + home_css + '\n'

# 5) Valida tudo ANTES de escrever.
checks = {
    'helper': JS_MARKER in js,
    'markup': '${mentorEduHomeSection()}' in js or 'mentorShortcuts.insertAdjacentHTML' in js,
    'binding': 'bindMentorEduHome(container, navigate);' in js,
    'css': CSS_MARKER in css,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('Validação falhou; nada foi gravado: ' + ', '.join(failed))

# 6) Só agora cria backups e grava.
backup_js = DASHBOARD_JS.with_name(DASHBOARD_JS.name + '.backup_mentor_inicio_v1_1')
backup_css = MENTOR_CSS.with_name(MENTOR_CSS.name + '.backup_mentor_inicio_v1_1')
if not backup_js.exists():
    backup_js.write_text(original_js, encoding='utf-8')
if not backup_css.exists():
    backup_css.write_text(original_css, encoding='utf-8')

DASHBOARD_JS.write_text(js, encoding='utf-8')
MENTOR_CSS.write_text(css, encoding='utf-8')

print('')
print('ETAPA 3.5 V1.1 — MENTOR EDU NO INÍCIO APLICADO COM SUCESSO.')
print('')
print('Alterados apenas:')
print('- frontend/js/pages/student/dashboard.js')
print('- frontend/css/mentor-ai-page.css')
print('')
print('Adicionado:')
print('- card compacto Mentor Edu antes de Atalhos rápidos')
print('- bolha flutuante no canto inferior direito')
print('- ambos abrem #/mentor-edu')
print('')
print('Use Ctrl + F5 e teste a tela Início.')
