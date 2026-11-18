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

# 1) Garante arquivos visuais
PAGE.parent.mkdir(parents=True, exist_ok=True)
CSS.parent.mkdir(parents=True, exist_ok=True)
BOT.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(FILES / 'mentor-edu.js', PAGE)
shutil.copy2(FILES / 'mentor-ai-page.css', CSS)
shutil.copy2(FILES / 'mentor-ai-bot.png', BOT)

# 2) main.js: garante rota dinâmica, sem duplicar
main = read(MAIN)
backup_once(MAIN, '.backup_etapa3_v1_1')
marker = '// MENTOR_EDU_DYNAMIC_ETAPA3'
if marker not in main:
    block = (
        '        // MENTOR_EDU_DYNAMIC_ETAPA3\n'
        '        if (route === "mentor-edu" && role === ROLES.STUDENT) {\n'
        '            const module = await import("./pages/student/mentor-edu.js");\n'
        '            return await module.renderStudentMentorEdu(container, user, navigate);\n'
        '        }\n\n'
    )
    anchors = [
        '        if (route === "notifications") return await renderNotifications(container);\n',
        '        if (route === "overview") {\n',
    ]
    anchor = next((a for a in anchors if a in main), None)
    if not anchor:
        raise SystemExit('Não encontrei ponto seguro para inserir a rota dinâmica no main.js.')
    main = main.replace(anchor, block + anchor, 1)
MAIN.write_text(main, encoding='utf-8')

# 3) dashboard.html: injeta CSS antes de </head>, sem depender de pages.css
dash = read(DASH)
backup_once(DASH, '.backup_etapa3_v1_1')
if 'css/mentor-ai-page.css' not in dash:
    tag = '    <link rel="stylesheet" href="css/mentor-ai-page.css">\n'
    lower = dash.lower()
    idx = lower.find('</head>')
    if idx == -1:
        raise SystemExit('Não encontrei </head> em frontend/dashboard.html.')
    dash = dash[:idx] + tag + dash[idx:]
DASH.write_text(dash, encoding='utf-8')

# 4) sidebar.js: torna Mentor Edu clicável e usa o robô
sidebar = read(SIDEBAR)
backup_once(SIDEBAR, '.backup_etapa3_v1_1')

# Aceita tanto o estado da Etapa 1 quanto um estado já parcialmente corrigido.
if '{ route: "mentor-edu", label: "Mentor Edu", icon: "mentor-ai", children: [' not in sidebar:
    sidebar = sidebar.replace(
        '{ label: "Mentor Edu", icon: "message", children: [',
        '{ route: "mentor-edu", label: "Mentor Edu", icon: "mentor-ai", children: [',
        1,
    )

if 'function sidebarIcon(item)' not in sidebar:
    item_anchor = 'function itemMarkup(item, unread) {\n'
    if item_anchor not in sidebar:
        raise SystemExit('Não encontrei function itemMarkup em sidebar.js.')
    helper = (
        'function sidebarIcon(item) {\n'
        '    if (item.icon === "mentor-ai") {\n'
        '        return `<span class="mentor-menu-icon" aria-hidden="true"><img src="assets/brand/mentor-ai-bot.png" alt=""></span>`;\n'
        '    }\n'
        '    return icon(item.icon);\n'
        '}\n\n'
    )
    sidebar = sidebar.replace(item_anchor, helper + item_anchor, 1)

item_start = sidebar.find('function itemMarkup(item, unread) {')
item_end = sidebar.find('export function renderSidebar', item_start)
if item_start == -1 or item_end == -1:
    raise SystemExit('Não consegui delimitar itemMarkup em sidebar.js.')

before = sidebar[:item_start]
item_block = sidebar[item_start:item_end]
after = sidebar[item_end:]

item_block = item_block.replace('${icon(item.icon)}', '${sidebarIcon(item)}')

plain_group = '<button class="nav-group-toggle" type="button" aria-expanded="false">${sidebarIcon(item)}'
route_group = '<button class="nav-group-toggle" type="button"${item.route ? ` data-route="${item.route}"` : ""} aria-expanded="false">${sidebarIcon(item)}'
if plain_group in item_block:
    item_block = item_block.replace(plain_group, route_group, 1)

sidebar = before + item_block + after

old_selector = 'document.querySelectorAll(".nav-item[data-route]").forEach(item => {'
new_selector = 'document.querySelectorAll(".nav-item[data-route], .nav-group-toggle[data-route]").forEach(item => {'
if old_selector in sidebar:
    sidebar = sidebar.replace(old_selector, new_selector, 1)

SIDEBAR.write_text(sidebar, encoding='utf-8')

# 5) Validações finais simples
checks = {
    'main.js rota dinâmica': marker in read(MAIN),
    'dashboard CSS': 'css/mentor-ai-page.css' in read(DASH),
    'sidebar Mentor Edu': 'route: "mentor-edu", label: "Mentor Edu"' in read(SIDEBAR),
    'sidebar robô': 'sidebarIcon(item)' in read(SIDEBAR),
    'página Mentor Edu': PAGE.exists(),
    'CSS Mentor Edu': CSS.exists(),
    'imagem do robô': BOT.exists(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('Falha na validação final: ' + ', '.join(failed))

print('')
print('ETAPA 3 V1.1 — REPARO APLICADO COM SUCESSO.')
print('')
print('Corrigido:')
print('- dashboard.html não depende mais de css/pages.css')
print('- CSS do Mentor Edu foi inserido antes de </head>')
print('- rota dinâmica foi preservada/garantida')
print('- menu Mentor Edu ficou clicável')
print('- ícone do robô foi aplicado')
print('- nenhum item foi duplicado')
print('')
print('Agora use Ctrl + F5 e abra #/mentor-edu.')
