from pathlib import Path

ROOT = Path('.')
FRONT = ROOT / 'frontend'
SIDEBAR = FRONT / 'js' / 'components' / 'sidebar.js'
ROUTER = FRONT / 'js' / 'core' / 'router.js'
MAIN = FRONT / 'js' / 'main.js'
AI_JS = FRONT / 'mentor-ai-student.js'
AI_CSS = FRONT / 'mentor-ai-student.css'

for path in (SIDEBAR, ROUTER, MAIN):
    if not path.exists():
        raise SystemExit(f'Arquivo obrigatório não encontrado: {path}')

def read(path):
    return path.read_text(encoding='utf-8-sig', errors='strict')

def backup(path):
    target = path.with_name(path.name + '.backup_menu_v1_4_1')
    if not target.exists():
        target.write_text(read(path), encoding='utf-8')

changed = []

# 1) Menu do aluno
sidebar = read(SIDEBAR)
backup(SIDEBAR)
start = sidebar.find('    aluno: [')
end = sidebar.find('    professor: [', start)
if start == -1 or end == -1:
    raise SystemExit('Não consegui localizar o menu do aluno em sidebar.js.')
student_menu = '    aluno: [\n        { route: "overview", label: "Início", icon: "home" },\n        { label: "Disciplinas", icon: "book", children: [\n            { route: "subjects", label: "Minhas disciplinas" },\n            { route: "library", label: "Conteúdos" },\n        ]},\n        { label: "Mentor Edu", icon: "message", children: [\n            { route: "mentor-edu", label: "Conversar com Mentor.Edu" },\n            { route: "study-plans", label: "Meu plano" },\n            { route: "recommendations", label: "Plano indicado" },\n            { route: "study-sessions", label: "Sessões de estudo" },\n        ]},\n        { label: "Avaliações", icon: "clipboard", children: [\n            { route: "assessments", label: "Disponíveis" },\n            { route: "assessment-history", label: "Histórico" },\n            { route: "assessment-results", label: "Resultados" },\n        ]},\n        { route: "grades", label: "Notas", icon: "chart" },\n        { label: "Frequência", icon: "calendar", children: [\n            { route: "attendance", label: "Resumo" },\n            { route: "attendance-justifications", label: "Justificativas" },\n        ]},\n        { route: "record", label: "Histórico acadêmico", icon: "school" },\n        { label: "Biblioteca", icon: "book", children: [\n            { route: "library", label: "Explorar biblioteca" },\n        ]},\n        { route: "schedules", label: "Horários", icon: "calendar" },\n        { route: "notifications", label: "Notificações", icon: "bell", badge: "notifications" },\n        { route: "tickets", label: "Chamados", icon: "message" },\n        { route: "profile", label: "Perfil", icon: "user" },\n    ],\n'
new_sidebar = sidebar[:start] + student_menu + sidebar[end:]
if new_sidebar != sidebar:
    SIDEBAR.write_text(new_sidebar, encoding='utf-8')
    changed.append(str(SIDEBAR))

# 2) Título da rota
router = read(ROUTER)
backup(ROUTER)
if '"mentor-edu": "Mentor Edu"' not in router:
    anchor = '    overview: "Dashboard",\n'
    if anchor not in router:
        raise SystemExit('Não encontrei overview em router.js.')
    router = router.replace(
        anchor,
        anchor + '    "mentor-edu": "Mentor Edu",\n',
        1,
    )
    ROUTER.write_text(router, encoding='utf-8')
    changed.append(str(ROUTER))

# 3) Rota Conversar com Mentor.Edu abre a IA
main = read(MAIN)
backup(MAIN)
overview_anchor = '        if (route === "overview") {\n'
mentor_route_block = '        if (route === "mentor-edu" && role === ROLES.STUDENT) {\n            await renderStudentDashboard(container, user, navigate);\n            window.dispatchEvent(new CustomEvent("mentor-ai:open"));\n            setTimeout(() => window.dispatchEvent(new CustomEvent("mentor-ai:open")), 100);\n            return;\n        }\n\n'
if 'route === "mentor-edu" && role === ROLES.STUDENT' not in main:
    if overview_anchor not in main:
        raise SystemExit('Não encontrei o bloco overview em main.js.')
    main = main.replace(overview_anchor, mentor_route_block + overview_anchor, 1)
    MAIN.write_text(main, encoding='utf-8')
    changed.append(str(MAIN))

# 4) O frontend da IA escuta o evento da rota
if AI_JS.exists():
    ai_js = read(AI_JS)
    backup(AI_JS)
    if 'MENTOR_AI_ROUTE_EVENT_V1_4_1' not in ai_js:
        hook = '  // MENTOR_AI_ROUTE_EVENT_V1_4_1\n  window.addEventListener("mentor-ai:open", () => {\n    if (shouldMount()) openMentor("chat");\n  });\n\n'
        anchors = [
            '  if(document.readyState === "loading"){',
            "  if(document.readyState === 'loading'){",
        ]
        found = next((a for a in anchors if a in ai_js), None)
        if not found:
            raise SystemExit('Não encontrei o ponto de inicialização em mentor-ai-student.js.')
        ai_js = ai_js.replace(found, hook + found, 1)
        AI_JS.write_text(ai_js, encoding='utf-8')
        changed.append(str(AI_JS))

# 5) Esconde o item antigo injetado para não duplicar Mentor Edu
if AI_CSS.exists():
    css = read(AI_CSS)
    backup(AI_CSS)
    if 'MENTOR_EDU_MENU_REORG_V1_4_1' not in css:
        css_fix = '\n/* MENTOR_EDU_MENU_REORG_V1_4_1 */\n#mentor-ai-nav-item {\n  display: none !important;\n}\n'
        AI_CSS.write_text(css.rstrip() + '\n\n' + css_fix + '\n', encoding='utf-8')
        changed.append(str(AI_CSS))

print('')
print('MENU MENTOR EDU V1.4.1 APLICADO COM SUCESSO.')
print('')
print('Estrutura nova:')
print('- Disciplinas')
print('  - Minhas disciplinas')
print('  - Conteúdos')
print('- Mentor Edu')
print('  - Conversar com Mentor.Edu')
print('  - Meu plano')
print('  - Plano indicado')
print('  - Sessões de estudo')
print('')
print('Plano de estudos e Recomendações não ficam mais soltos no menu principal.')
print('Conversar com Mentor.Edu abre o chat da IA.')
print('')
print('Arquivos alterados:')
for item in changed:
    print('-', item)
print('')
print('Agora pressione Ctrl + F5 no navegador.')
