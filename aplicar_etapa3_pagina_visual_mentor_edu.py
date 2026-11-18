from pathlib import Path
import shutil

ROOT = Path('.')
FRONT = ROOT / 'frontend'
HERE = Path(__file__).resolve().parent
FILES = HERE / 'files'

MAIN = FRONT / 'js' / 'main.js'
DASH = FRONT / 'dashboard.html'
SIDEBAR = FRONT / 'js' / 'components' / 'sidebar.js'
PAGE = FRONT / 'js' / 'pages' / 'student' / 'mentor-edu.js'
CSS = FRONT / 'css' / 'mentor-ai-page.css'
BOT = FRONT / 'assets' / 'brand' / 'mentor-ai-bot.png'

for path in (MAIN, DASH, SIDEBAR):
    if not path.exists():
        raise SystemExit(f'Arquivo necessário não encontrado: {path}')

def read(path):
    return path.read_text(encoding='utf-8-sig', errors='strict')

def backup_once(path, suffix):
    backup = path.with_name(path.name + suffix)
    if not backup.exists():
        backup.write_text(read(path), encoding='utf-8')

# Novos arquivos isolados
PAGE.parent.mkdir(parents=True, exist_ok=True)
CSS.parent.mkdir(parents=True, exist_ok=True)
BOT.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(FILES / 'mentor-edu.js', PAGE)
shutil.copy2(FILES / 'mentor-ai-page.css', CSS)
shutil.copy2(FILES / 'mentor-ai-bot.png', BOT)

# ----------------------------------------------------------
# main.js: SOMENTE import dinâmico da rota mentor-edu.
# ----------------------------------------------------------
main = read(MAIN)
backup_once(MAIN, '.backup_etapa3')
dynamic_marker = '// MENTOR_EDU_DYNAMIC_ETAPA3'
dynamic_block = (
    '        // MENTOR_EDU_DYNAMIC_ETAPA3\n'
    '        if (route === "mentor-edu" && role === ROLES.STUDENT) {\n'
    '            const module = await import("./pages/student/mentor-edu.js");\n'
    '            return await module.renderStudentMentorEdu(container, user, navigate);\n'
    '        }\n\n'
)
if dynamic_marker not in main:
    anchor = '        if (route === "notifications") return await renderNotifications(container);\n'
    if anchor not in main:
        raise SystemExit('Não encontrei um ponto seguro para a rota mentor-edu em main.js. Nada foi aplicado ao main.js.')
    main = main.replace(anchor, dynamic_block + anchor, 1)
MAIN.write_text(main, encoding='utf-8')

# ----------------------------------------------------------
# dashboard.html: carrega APENAS o CSS da página.
# ----------------------------------------------------------
dash = read(DASH)
backup_once(DASH, '.backup_etapa3')
if 'css/mentor-ai-page.css' not in dash:
    anchor = '    <link rel="stylesheet" href="css/pages.css">\n'
    tag = '    <link rel="stylesheet" href="css/mentor-ai-page.css">\n'
    if anchor not in dash:
        raise SystemExit('Não encontrei css/pages.css em dashboard.html.')
    dash = dash.replace(anchor, anchor + tag, 1)
DASH.write_text(dash, encoding='utf-8')

# ----------------------------------------------------------
# sidebar.js: ícone real + título Mentor Edu clicável.
# ----------------------------------------------------------
sidebar = read(SIDEBAR)
backup_once(SIDEBAR, '.backup_etapa3')

# O grupo criado na Etapa 1 passa a ter rota e ícone próprios.
sidebar = sidebar.replace(
    '{ label: "Mentor Edu", icon: "message", children: [',
    '{ route: "mentor-edu", label: "Mentor Edu", icon: "mentor-ai", children: [',
    1,
)

# Helper de ícone: só afeta icon=mentor-ai; demais ícones ficam iguais.
if 'function sidebarIcon(item)' not in sidebar:
    old_fn = 'function itemMarkup(item, unread) {\n'
    helper = (
        'function sidebarIcon(item) {\n'
        '    if (item.icon === "mentor-ai") {\n'
        '        return `<span class="mentor-menu-icon" aria-hidden="true"><img src="assets/brand/mentor-ai-bot.png" alt=""></span>`;\n'
        '    }\n'
        '    return icon(item.icon);\n'
        '}\n\n'
    )
    if old_fn not in sidebar:
        raise SystemExit('Não encontrei itemMarkup em sidebar.js.')
    sidebar = sidebar.replace(old_fn, helper + old_fn, 1)

# Troca os dois usos de icon(item.icon) dentro de itemMarkup.
item_start = sidebar.find('function itemMarkup(item, unread) {')
item_end = sidebar.find('export function renderSidebar', item_start)
if item_start == -1 or item_end == -1:
    raise SystemExit('Não consegui delimitar itemMarkup em sidebar.js.')
before = sidebar[:item_start]
item_block = sidebar[item_start:item_end]
after = sidebar[item_end:]
item_block = item_block.replace('${icon(item.icon)}', '${sidebarIcon(item)}')

# Grupo com route recebe data-route no botão principal.
old_group = '<button class="nav-group-toggle" type="button" aria-expanded="false">${sidebarIcon(item)}'
new_group = '<button class="nav-group-toggle" type="button"${item.route ? ` data-route="${item.route}"` : ""} aria-expanded="false">${sidebarIcon(item)}'
item_block = item_block.replace(old_group, new_group)
sidebar = before + item_block + after

# Active state também reconhece o botão principal Mentor Edu.
sidebar = sidebar.replace(
    'document.querySelectorAll(".nav-item[data-route]").forEach(item => {',
    'document.querySelectorAll(".nav-item[data-route], .nav-group-toggle[data-route]").forEach(item => {',
    1,
)

SIDEBAR.write_text(sidebar, encoding='utf-8')

print('')
print('ETAPA 3 — PÁGINA VISUAL MENTOR EDU APLICADA COM SUCESSO.')
print('')
print('Criado:')
print('- frontend/js/pages/student/mentor-edu.js')
print('- frontend/css/mentor-ai-page.css')
print('- frontend/assets/brand/mentor-ai-bot.png')
print('')
print('Alterações pequenas e controladas em:')
print('- frontend/js/main.js -> apenas rota com import dinâmico')
print('- frontend/dashboard.html -> apenas link do CSS')
print('- frontend/js/components/sidebar.js -> ícone + título Mentor Edu clicável')
print('')
print('IMPORTANTE: nenhuma chamada à IA foi adicionada nesta etapa.')
print('Use Ctrl + F5 e teste a página Mentor Edu.')
print('')
print('Se precisar desfazer SOMENTE a Etapa 3:')
print('git restore frontend/js/main.js frontend/dashboard.html frontend/js/components/sidebar.js')
print('Remove-Item frontend/js/pages/student/mentor-edu.js, frontend/css/mentor-ai-page.css, frontend/assets/brand/mentor-ai-bot.png -Force')
