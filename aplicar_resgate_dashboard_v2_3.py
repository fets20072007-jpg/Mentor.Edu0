from pathlib import Path

ROOT = Path('.')
MAIN = ROOT / 'frontend' / 'js' / 'main.js'

if not MAIN.exists():
    raise SystemExit('Não encontrei frontend/js/main.js. Rode este script na raiz do Mentor.Edu.')

text = MAIN.read_text(encoding='utf-8-sig', errors='strict')

backup = MAIN.with_name('main.js.backup_dashboard_resgate_v2_3')
if not backup.exists():
    backup.write_text(text, encoding='utf-8')

# Remove import estático da página Mentor Edu
for item in [
    'import { renderStudentMentorEdu } from "./pages/student/mentor-edu.js";\n',
    "import { renderStudentMentorEdu } from './pages/student/mentor-edu.js';\n",
]:
    text = text.replace(item, '')

# Remove registro estático no mapa de rotas do aluno
text = text.replace('                "mentor-edu": renderStudentMentorEdu,\n', '')
text = text.replace("                'mentor-edu': renderStudentMentorEdu,\n", '')

# Remove bloco antigo que abria o overlay pela rota
old_special = (
    '        if (route === "mentor-edu" && role === ROLES.STUDENT) {\n'
    '            await renderStudentDashboard(container, user, navigate);\n'
    '            window.dispatchEvent(new CustomEvent("mentor-ai:open"));\n'
    '            setTimeout(() => window.dispatchEvent(new CustomEvent("mentor-ai:open")), 100);\n'
    '            return;\n'
    '        }\n\n'
)
text = text.replace(old_special, '')

# Se uma versão anterior colocou mentor-edu junto do overview, volta ao overview normal
old_overview = (
    '        if (route === "overview" || route === "mentor-edu") {\n'
    '            if (role === ROLES.STUDENT) return await renderStudentDashboard(container, user, navigate);\n'
    '            if (role === ROLES.TEACHER) return await renderTeacherDashboard(container, user, navigate);\n'
    '            if (role === ROLES.ADMIN) return await renderAdminDashboard(container, user, navigate);\n'
    '            if (role === ROLES.SUPPORT) return await renderSupportDashboard(container, user, navigate);\n'
    '        }\n'
)
normal_overview = (
    '        if (route === "overview") {\n'
    '            if (role === ROLES.STUDENT) return await renderStudentDashboard(container, user, navigate);\n'
    '            if (role === ROLES.TEACHER) return await renderTeacherDashboard(container, user, navigate);\n'
    '            if (role === ROLES.ADMIN) return await renderAdminDashboard(container, user, navigate);\n'
    '            if (role === ROLES.SUPPORT) return await renderSupportDashboard(container, user, navigate);\n'
    '        }\n'
)
text = text.replace(old_overview, normal_overview)

# Insere rota Mentor Edu com import dinâmico, somente quando clicada
dynamic_marker = '        // MENTOR_EDU_DYNAMIC_ROUTE_V2_3\n'
dynamic_block = (
    dynamic_marker
    + '        if (route === "mentor-edu" && role === ROLES.STUDENT) {\n'
    + '            const module = await import("./pages/student/mentor-edu.js");\n'
    + '            return await module.renderStudentMentorEdu(container, user, navigate);\n'
    + '        }\n\n'
)

if dynamic_marker not in text:
    anchor = '        if (route === "overview") {\n'
    if anchor not in text:
        raise SystemExit("Não encontrei o bloco de overview em main.js. O arquivo não foi alterado.")
    text = text.replace(anchor, dynamic_block + anchor, 1)

MAIN.write_text(text, encoding='utf-8')

print('')
print('DASHBOARD RESGATE V2.3 APLICADO COM SUCESSO.')
print('')
print('- main.js não importa mais a IA durante o boot')
print('- Mentor Edu só carrega quando você clicar nele')
print('- Login V2.2 permanece intacto')
print('- Início e demais páginas não dependem da IA')
print('')
print('Reinicie o frontend e use Ctrl + F5.')
