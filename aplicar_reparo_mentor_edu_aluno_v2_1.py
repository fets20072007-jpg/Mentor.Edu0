from pathlib import Path
import shutil

ROOT = Path('.')
FRONT = ROOT / 'frontend'
HERE = Path(__file__).resolve().parent
FILES = HERE / 'files'

if not FRONT.exists():
    raise SystemExit('Não encontrei a pasta frontend. Rode este script na raiz do Mentor.Edu.')

def read(path):
    return path.read_text(encoding='utf-8-sig', errors='strict')

def backup(path):
    target = path.with_name(path.name + '.backup_mentor_v2_1')
    if not target.exists():
        target.write_text(read(path), encoding='utf-8')

changed = []

# 1) Copia página, CSS e ícone
target_page = FRONT / 'js' / 'pages' / 'student' / 'mentor-edu.js'
target_css = FRONT / 'css' / 'mentor-ai-page.css'
target_bot = FRONT / 'assets' / 'brand' / 'mentor-ai-bot.png'
for path in (target_page.parent, target_css.parent, target_bot.parent):
    path.mkdir(parents=True, exist_ok=True)
shutil.copy2(FILES / 'mentor-edu.js', target_page)
shutil.copy2(FILES / 'mentor-ai-page.css', target_css)
shutil.copy2(FILES / 'mentor-ai-bot.png', target_bot)
changed += [str(target_page), str(target_css), str(target_bot)]

# 2) Sidebar oficial
sidebar_path = FRONT / 'js' / 'components' / 'sidebar.js'
if not sidebar_path.exists():
    raise SystemExit(f'Arquivo não encontrado: {sidebar_path}')
sidebar = read(sidebar_path)
backup(sidebar_path)
start = sidebar.find('    aluno: [')
end = sidebar.find('    professor: [', start)
if start == -1 or end == -1:
    raise SystemExit('Não consegui localizar o bloco do menu do aluno em sidebar.js.')
student_menu = '    aluno: [\n        { route: "overview", label: "Início", icon: "home" },\n        { label: "Disciplinas", icon: "book", children: [\n            { route: "subjects", label: "Minhas disciplinas" },\n            { route: "library", label: "Conteúdos" },\n        ]},\n        { route: "mentor-edu", label: "Mentor Edu", icon: "mentor-ai", children: [\n            { route: "mentor-edu", label: "Conversar com Mentor.Edu" },\n            { route: "study-plans", label: "Meu plano" },\n            { route: "recommendations", label: "Plano indicado" },\n            { route: "study-sessions", label: "Sessões de estudo" },\n        ]},\n        { label: "Avaliações", icon: "clipboard", children: [\n            { route: "assessments", label: "Disponíveis" },\n            { route: "assessment-history", label: "Histórico" },\n            { route: "assessment-results", label: "Resultados" },\n        ]},\n        { route: "grades", label: "Notas", icon: "chart" },\n        { label: "Frequência", icon: "calendar", children: [\n            { route: "attendance", label: "Resumo" },\n            { route: "attendance-justifications", label: "Justificativas" },\n        ]},\n        { route: "record", label: "Histórico acadêmico", icon: "school" },\n        { label: "Biblioteca", icon: "book", children: [\n            { route: "library", label: "Explorar biblioteca" },\n        ]},\n        { route: "schedules", label: "Horários", icon: "calendar" },\n        { route: "notifications", label: "Notificações", icon: "bell", badge: "notifications" },\n        { route: "tickets", label: "Chamados", icon: "message" },\n        { route: "profile", label: "Perfil", icon: "user" },\n    ],\n'
sidebar = sidebar[:start] + student_menu + sidebar[end:]

new_item_markup = 'function navIconMarkup(item) {\n    if (item.icon === "mentor-ai") {\n        return `<span class="mentor-ai-menu-icon" aria-hidden="true"><img src="assets/brand/mentor-ai-bot.png" alt=""></span>`;\n    }\n    return icon(item.icon);\n}\n\nfunction itemMarkup(item, unread) {\n    const badge = item.badge === "notifications" && unread > 0 ? `<span class="nav-badge">${Math.min(unread, 99)}</span>` : "";\n    const leading = navIconMarkup(item);\n\n    if (item.children) {\n        const routeAttr = item.route ? ` data-route="${item.route}"` : "";\n        return `<div class="nav-group" data-nav-group><button class="nav-group-toggle" type="button"${routeAttr} aria-expanded="false">${leading}<span>${item.label}</span>${icon("chevron", "icon chevron")}</button><div class="nav-children">${item.children.map(child => `<button class="nav-item" type="button" data-route="${child.route}"><span>${child.label}</span>${child.badge === "notifications" && unread > 0 ? `<span class="nav-badge">${Math.min(unread, 99)}</span>` : ""}</button>`).join("")}</div></div>`;\n    }\n\n    return `<button class="nav-item" type="button" data-route="${item.route}">${leading}<span>${item.label}</span>${badge}</button>`;\n}\n\n'
fn_start = sidebar.find('function itemMarkup(item, unread) {')
fn_end = sidebar.find('export function renderSidebar', fn_start)
if 'function navIconMarkup(item)' not in sidebar:
    if fn_start == -1 or fn_end == -1:
        raise SystemExit('Não consegui localizar itemMarkup em sidebar.js.')
    sidebar = sidebar[:fn_start] + new_item_markup + sidebar[fn_end:]

# Se a V2 parcial já criou navIconMarkup, mantém sem duplicar.
sidebar_path.write_text(sidebar, encoding='utf-8')
changed.append(str(sidebar_path))

# 3) Router
router_path = FRONT / 'js' / 'core' / 'router.js'
if not router_path.exists():
    raise SystemExit(f'Arquivo não encontrado: {router_path}')
router = read(router_path)
backup(router_path)
if '"mentor-edu": "Mentor Edu"' not in router:
    anchor = '    overview: "Dashboard",\n'
    if anchor not in router:
        raise SystemExit('Não encontrei a entrada overview no router.js.')
    router = router.replace(anchor, anchor + '    "mentor-edu": "Mentor Edu",\n', 1)
router_path.write_text(router, encoding='utf-8')
changed.append(str(router_path))

# 4) main.js - reparo robusto sem depender da posição exata dos imports
main_path = FRONT / 'js' / 'main.js'
if not main_path.exists():
    raise SystemExit(f'Arquivo não encontrado: {main_path}')
main = read(main_path)
backup(main_path)

mentor_import = 'import { renderStudentMentorEdu } from "./pages/student/mentor-edu.js";\n'
if mentor_import not in main:
    candidates = [
        'import { renderStudentSubjects } from "./pages/student/subjects.js";\n',
        'import { renderStudentGrades } from "./pages/student/grades.js";\n',
        'import { renderStudentDashboard } from "./pages/student/dashboard.js";\n',
    ]
    anchor = next((c for c in candidates if c in main), None)
    if anchor:
        main = main.replace(anchor, mentor_import + anchor, 1)
    else:
        module_anchor = 'const page = document.body.dataset.page;'
        if module_anchor not in main:
            raise SystemExit('Não encontrei um ponto seguro para inserir o import em main.js.')
        main = main.replace(module_anchor, mentor_import + '\n' + module_anchor, 1)

# Remove tentativa antiga que abria overlay, caso esteja presente.
old_special = (
    '        if (route === "mentor-edu" && role === ROLES.STUDENT) {\n'
    '            await renderStudentDashboard(container, user, navigate);\n'
    '            window.dispatchEvent(new CustomEvent("mentor-ai:open"));\n'
    '            setTimeout(() => window.dispatchEvent(new CustomEvent("mentor-ai:open")), 100);\n'
    '            return;\n'
    '        }\n\n'
)
main = main.replace(old_special, '')

if '"mentor-edu": renderStudentMentorEdu,' not in main:
    routes_anchor = '            const studentRoutes = {\n'
    if routes_anchor not in main:
        raise SystemExit('Não encontrei const studentRoutes em main.js.')
    main = main.replace(
        routes_anchor,
        routes_anchor + '                "mentor-edu": renderStudentMentorEdu,\n',
        1,
    )

main_path.write_text(main, encoding='utf-8')
changed.append(str(main_path))

# 5) CSS da página no dashboard.html
dashboard_path = FRONT / 'dashboard.html'
if not dashboard_path.exists():
    raise SystemExit(f'Arquivo não encontrado: {dashboard_path}')
dashboard = read(dashboard_path)
backup(dashboard_path)
if 'css/mentor-ai-page.css' not in dashboard:
    anchor = '    <link rel="stylesheet" href="css/pages.css">\n'
    tag = '    <link rel="stylesheet" href="css/mentor-ai-page.css">\n'
    if anchor in dashboard:
        dashboard = dashboard.replace(anchor, anchor + tag, 1)
    elif '</head>' in dashboard:
        dashboard = dashboard.replace('</head>', tag + '</head>', 1)
    else:
        raise SystemExit('Não encontrei </head> em dashboard.html.')
dashboard_path.write_text(dashboard, encoding='utf-8')
changed.append(str(dashboard_path))

# 6) Integra card/bolha antigos com a página oficial, se existirem
legacy_js_path = FRONT / 'mentor-ai-student.js'
if legacy_js_path.exists():
    legacy = read(legacy_js_path)
    backup(legacy_js_path)
    legacy = legacy.replace(
        'card.querySelector("button").addEventListener("click", () => openMentor("chat"));',
        'card.querySelector("button").addEventListener("click", () => { location.hash = "#/mentor-edu"; });',
    )
    legacy = legacy.replace(
        'if(action === "open"){ nudge.remove(); openMentor("chat"); }',
        'if(action === "open"){ nudge.remove(); location.hash = "#/mentor-edu"; }',
    )
    old_hook = (
        '  // MENTOR_AI_ROUTE_EVENT_V1_4_1\n'
        '  window.addEventListener("mentor-ai:open", () => {\n'
        '    if (shouldMount()) openMentor("chat");\n'
        '  });\n\n'
    )
    legacy = legacy.replace(old_hook, '')
    legacy = legacy.replace(
        '<div class="mentor-ai-mascot" aria-hidden="true">🤖</div>',
        '<div class="mentor-ai-mascot" aria-hidden="true"><img src="assets/brand/mentor-ai-bot.png" alt=""></div>',
    )
    legacy = legacy.replace(
        '<span class="mentor-ai-float-avatar">🤖</span>',
        '<span class="mentor-ai-float-avatar"><img src="assets/brand/mentor-ai-bot.png" alt=""></span>',
    )
    legacy_js_path.write_text(legacy, encoding='utf-8')
    changed.append(str(legacy_js_path))

legacy_css_path = FRONT / 'mentor-ai-student.css'
if legacy_css_path.exists():
    legacy_css = read(legacy_css_path)
    backup(legacy_css_path)
    extra = '\n/* MENTOR_AI_ASSET_FIX_V2_1 */\n.mentor-ai-mascot img,\n.mentor-ai-float-avatar img {\n  width: 100%;\n  height: 100%;\n  object-fit: cover;\n  border-radius: inherit;\n  display: block;\n}\n#mentor-ai-nav-item {\n  display: none !important;\n}\n'
    if 'MENTOR_AI_ASSET_FIX_V2_1' not in legacy_css:
        legacy_css = legacy_css.rstrip() + '\n\n' + extra + '\n'
    legacy_css_path.write_text(legacy_css, encoding='utf-8')
    changed.append(str(legacy_css_path))

print('')
print('REPARO MENTOR EDU ALUNO V2.1 APLICADO COM SUCESSO.')
print('')
print('Conferido/aplicado:')
print('- página oficial Mentor Edu')
print('- import robusto em main.js')
print('- rota mentor-edu')
print('- menu com ícone do robô')
print('- CSS da página')
print('- chat expansível')
print('- card e bolha do Início navegando para a página oficial')
print('')
print('Arquivos tocados:')
for item in dict.fromkeys(changed):
    print('-', item)
print('')
print('Agora use Ctrl + F5 e abra Mentor Edu no menu.')
