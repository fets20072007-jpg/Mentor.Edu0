from pathlib import Path
import shutil

ROOT = Path('.')
FRONT = ROOT / 'frontend'
HERE = Path(__file__).resolve().parent
FILES = HERE / 'files'

if not FRONT.exists():
    raise SystemExit('Não encontrei a pasta frontend. Rode este script na raiz do Mentor.Edu.')

required = [
    FRONT / 'js' / 'components' / 'sidebar.js',
    FRONT / 'js' / 'core' / 'router.js',
    FRONT / 'js' / 'main.js',
    FRONT / 'dashboard.html',
]
for path in required:
    if not path.exists():
        raise SystemExit(f'Arquivo obrigatório não encontrado: {path}')

def read(path):
    return path.read_text(encoding='utf-8-sig', errors='strict')

def backup(path, label='mentor_v2'):
    target = path.with_name(path.name + f'.backup_{label}')
    if not target.exists():
        target.write_text(read(path), encoding='utf-8')

changed = []

# Copia arquivos novos.
target_page = FRONT / 'js' / 'pages' / 'student' / 'mentor-edu.js'
target_css = FRONT / 'css' / 'mentor-ai-page.css'
target_bot = FRONT / 'assets' / 'brand' / 'mentor-ai-bot.png'
for target in [target_page.parent, target_css.parent, target_bot.parent]:
    target.mkdir(parents=True, exist_ok=True)
shutil.copy2(FILES / 'mentor-edu.js', target_page)
shutil.copy2(FILES / 'mentor-ai-page.css', target_css)
shutil.copy2(FILES / 'mentor-ai-bot.png', target_bot)
changed += [str(target_page), str(target_css), str(target_bot)]

# SIDEBAR
sidebar_path = FRONT / 'js' / 'components' / 'sidebar.js'
sidebar = read(sidebar_path)
backup(sidebar_path)
start = sidebar.find('    aluno: [')
end = sidebar.find('    professor: [', start)
if start == -1 or end == -1:
    raise SystemExit('Não consegui localizar o menu do aluno em sidebar.js.')
student_menu = '''    aluno: [
        { route: "overview", label: "Início", icon: "home" },
        { label: "Disciplinas", icon: "book", children: [
            { route: "subjects", label: "Minhas disciplinas" },
            { route: "library", label: "Conteúdos" },
        ]},
        { route: "mentor-edu", label: "Mentor Edu", icon: "mentor-ai", children: [
            { route: "mentor-edu", label: "Conversar com Mentor.Edu" },
            { route: "study-plans", label: "Meu plano" },
            { route: "recommendations", label: "Plano indicado" },
            { route: "study-sessions", label: "Sessões de estudo" },
        ]},
        { label: "Avaliações", icon: "clipboard", children: [
            { route: "assessments", label: "Disponíveis" },
            { route: "assessment-history", label: "Histórico" },
            { route: "assessment-results", label: "Resultados" },
        ]},
        { route: "grades", label: "Notas", icon: "chart" },
        { label: "Frequência", icon: "calendar", children: [
            { route: "attendance", label: "Resumo" },
            { route: "attendance-justifications", label: "Justificativas" },
        ]},
        { route: "record", label: "Histórico acadêmico", icon: "school" },
        { label: "Biblioteca", icon: "book", children: [
            { route: "library", label: "Explorar biblioteca" },
        ]},
        { route: "schedules", label: "Horários", icon: "calendar" },
        { route: "notifications", label: "Notificações", icon: "bell", badge: "notifications" },
        { route: "tickets", label: "Chamados", icon: "message" },
        { route: "profile", label: "Perfil", icon: "user" },
    ],
'''
sidebar = sidebar[:start] + student_menu + sidebar[end:]
fn_start = sidebar.find('function itemMarkup(item, unread) {')
fn_end = sidebar.find('export function renderSidebar', fn_start)
if fn_start == -1 or fn_end == -1:
    raise SystemExit('Não consegui localizar itemMarkup em sidebar.js.')
new_item_markup = '''function navIconMarkup(item) {
    if (item.icon === "mentor-ai") {
        return `<span class="mentor-ai-menu-icon" aria-hidden="true"><img src="assets/brand/mentor-ai-bot.png" alt=""></span>`;
    }
    return icon(item.icon);
}

function itemMarkup(item, unread) {
    const badge = item.badge === "notifications" && unread > 0 ? `<span class="nav-badge">${Math.min(unread, 99)}</span>` : "";
    const leading = navIconMarkup(item);
    if (item.children) {
        const routeAttr = item.route ? ` data-route="${item.route}"` : "";
        return `<div class="nav-group" data-nav-group><button class="nav-group-toggle" type="button"${routeAttr} aria-expanded="false">${leading}<span>${item.label}</span>${icon("chevron", "icon chevron")}</button><div class="nav-children">${item.children.map(child => `<button class="nav-item" type="button" data-route="${child.route}"><span>${child.label}</span>${child.badge === "notifications" && unread > 0 ? `<span class="nav-badge">${Math.min(unread, 99)}</span>` : ""}</button>`).join("")}</div></div>`;
    }
    return `<button class="nav-item" type="button" data-route="${item.route}">${leading}<span>${item.label}</span>${badge}</button>`;
}

'''
sidebar = sidebar[:fn_start] + new_item_markup + sidebar[fn_end:]
sidebar_path.write_text(sidebar, encoding='utf-8')
changed.append(str(sidebar_path))

# ROUTER
router_path = FRONT / 'js' / 'core' / 'router.js'
router = read(router_path)
backup(router_path)
if '"mentor-edu": "Mentor Edu"' not in router:
    anchor = '    overview: "Dashboard",\n'
    if anchor not in router:
        raise SystemExit('Não encontrei a rota overview em router.js.')
    router = router.replace(anchor, anchor + '    "mentor-edu": "Mentor Edu",\n', 1)
router_path.write_text(router, encoding='utf-8')
changed.append(str(router_path))

# MAIN
main_path = FRONT / 'js' / 'main.js'
main = read(main_path)
backup(main_path)
import_anchor = 'import { renderStudentDashboard } from "./pages/student/dashboard.js";\n'
mentor_import = 'import { renderStudentMentorEdu } from "./pages/student/mentor-edu.js";\n'
if mentor_import not in main:
    if import_anchor not in main:
        raise SystemExit('Não encontrei o import do dashboard do aluno em main.js.')
    main = main.replace(import_anchor, import_anchor + mentor_import, 1)
old_special = '''        if (route === "mentor-edu" && role === ROLES.STUDENT) {
            await renderStudentDashboard(container, user, navigate);
            window.dispatchEvent(new CustomEvent("mentor-ai:open"));
            setTimeout(() => window.dispatchEvent(new CustomEvent("mentor-ai:open")), 100);
            return;
        }

'''
main = main.replace(old_special, '')
student_map_anchor = '''            const studentRoutes = {
                subjects: renderStudentSubjects,
'''
if '"mentor-edu": renderStudentMentorEdu,' not in main:
    if student_map_anchor not in main:
        raise SystemExit('Não encontrei o mapa de rotas do aluno em main.js.')
    main = main.replace(student_map_anchor, '''            const studentRoutes = {
                "mentor-edu": renderStudentMentorEdu,
                subjects: renderStudentSubjects,
''', 1)
main_path.write_text(main, encoding='utf-8')
changed.append(str(main_path))

# DASHBOARD HTML
dashboard_path = FRONT / 'dashboard.html'
dashboard = read(dashboard_path)
backup(dashboard_path)
css_tag = '    <link rel="stylesheet" href="css/mentor-ai-page.css">\n'
if 'css/mentor-ai-page.css' not in dashboard:
    anchor = '    <link rel="stylesheet" href="css/pages.css">\n'
    if anchor in dashboard:
        dashboard = dashboard.replace(anchor, anchor + css_tag, 1)
    else:
        dashboard = dashboard.replace('</head>', css_tag + '</head>', 1)
dashboard_path.write_text(dashboard, encoding='utf-8')
changed.append(str(dashboard_path))

# LEGADO IA NO INÍCIO
legacy_js_path = FRONT / 'mentor-ai-student.js'
if legacy_js_path.exists():
    legacy = read(legacy_js_path)
    backup(legacy_js_path)
    legacy = legacy.replace('card.querySelector("button").addEventListener("click", () => openMentor("chat"));', 'card.querySelector("button").addEventListener("click", () => { location.hash = "#/mentor-edu"; });')
    legacy = legacy.replace('if(action === "open"){ nudge.remove(); openMentor("chat"); }', 'if(action === "open"){ nudge.remove(); location.hash = "#/mentor-edu"; }')
    old_hook = '''  // MENTOR_AI_ROUTE_EVENT_V1_4_1
  window.addEventListener("mentor-ai:open", () => {
    if (shouldMount()) openMentor("chat");
  });

'''
    legacy = legacy.replace(old_hook, '')
    legacy = legacy.replace('<div class="mentor-ai-mascot" aria-hidden="true">🤖</div>', '<div class="mentor-ai-mascot" aria-hidden="true"><img src="assets/brand/mentor-ai-bot.png" alt=""></div>')
    legacy = legacy.replace('<span class="mentor-ai-float-avatar">🤖</span>', '<span class="mentor-ai-float-avatar"><img src="assets/brand/mentor-ai-bot.png" alt=""></span>')
    legacy_js_path.write_text(legacy, encoding='utf-8')
    changed.append(str(legacy_js_path))

legacy_css_path = FRONT / 'mentor-ai-student.css'
if legacy_css_path.exists():
    legacy_css = read(legacy_css_path)
    backup(legacy_css_path)
    marker = '/* MENTOR_AI_ASSET_FIX_V2 */'
    extra = '''

/* MENTOR_AI_ASSET_FIX_V2 */
.mentor-ai-mascot img,
.mentor-ai-float-avatar img { width:100%; height:100%; object-fit:cover; border-radius:inherit; display:block; }
#mentor-ai-nav-item { display:none !important; }
'''
    if marker not in legacy_css:
        legacy_css += extra
    legacy_css_path.write_text(legacy_css, encoding='utf-8')
    changed.append(str(legacy_css_path))

print('')
print('MENTOR EDU — PÁGINA IA DO ALUNO V2 APLICADA COM SUCESSO.')
print('')
print('- ícone do robô no menu Mentor Edu')
print('- Mentor Edu como grupo oficial, fora de Disciplinas')
print('- clique no Mentor Edu abre a página de Insights com IA')
print('- informações recolhíveis com Ver mais / Fechar')
print('- chat compacto com Expandir chat / Reduzir chat')
print('- chat conectado a /mentor-ai/student/tutor')
print('- insights conectados a /mentor-ai/student/profile')
print('- cards e atalhos do Início preservados')
print('')
print('Arquivos alterados/criados:')
for item in dict.fromkeys(changed): print('-', item)
print('')
print('Backend e banco: nenhuma alteração.')
print('Atualize com Ctrl + F5.')
