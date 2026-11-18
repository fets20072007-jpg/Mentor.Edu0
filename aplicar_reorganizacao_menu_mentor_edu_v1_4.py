from pathlib import Path
import re

ROOT = Path(".")
FRONT = ROOT / "frontend"

if not FRONT.exists():
    raise SystemExit("Não encontrei a pasta frontend. Rode este script na raiz do Mentor.Edu.")

sidebar_js = FRONT / "js" / "components" / "sidebar.js"
router_js = FRONT / "js" / "core" / "router.js"
main_js = FRONT / "js" / "main.js"
mentor_ai_css = FRONT / "mentor-ai-student.css"

for path in [sidebar_js, router_js, main_js]:
    if not path.exists():
        raise SystemExit(f"Arquivo obrigatório não encontrado: {path}")

changed = []

def backup_file(path: Path, suffix: str):
    backup = path.with_name(path.name + suffix)
    if not backup.exists():
        backup.write_text(path.read_text(encoding="utf-8-sig", errors="ignore"), encoding="utf-8")
    return backup

sidebar_text = sidebar_js.read_text(encoding="utf-8-sig", errors="ignore")
backup_file(sidebar_js, ".backup_menu_v1_4")

student_block_pattern = r'aluno:\s*\[(.*?)\],\s*professor:'
new_student_block = """aluno: [
        { route: "overview", label: "Início", icon: "home" },
        { label: "Disciplinas", icon: "book", children: [
            { route: "subjects", label: "Minhas disciplinas" },
            { route: "library", label: "Conteúdos" },
        ]},
        { label: "Mentor Edu", icon: "message", children: [
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
    professor:"""

sidebar_new, sidebar_count = re.subn(student_block_pattern, new_student_block, sidebar_text, count=1, flags=re.S)
if sidebar_count != 1:
    raise SystemExit("Não consegui localizar o bloco do menu do aluno em frontend/js/components/sidebar.js.")
if sidebar_new != sidebar_text:
    sidebar_js.write_text(sidebar_new, encoding="utf-8")
    changed.append(str(sidebar_js))

router_text = router_js.read_text(encoding="utf-8-sig", errors="ignore")
backup_file(router_js, ".backup_menu_v1_4")
if '"mentor-edu": "Mentor Edu",' not in router_text:
    if 'overview: "Dashboard",' in router_text:
        router_text = router_text.replace('overview: "Dashboard",', 'overview: "Dashboard",
    "mentor-edu": "Mentor Edu",', 1)
    else:
        raise SystemExit("Não consegui inserir o título da rota mentor-edu em frontend/js/core/router.js.")
router_js.write_text(router_text, encoding="utf-8")
if str(router_js) not in changed:
    changed.append(str(router_js))

main_text = main_js.read_text(encoding="utf-8-sig", errors="ignore")
backup_file(main_js, ".backup_menu_v1_4")
old_block = """        if (route === "overview") {
            if (role === ROLES.STUDENT) return await renderStudentDashboard(container, user, navigate);
            if (role === ROLES.TEACHER) return await renderTeacherDashboard(container, user, navigate);
            if (role === ROLES.ADMIN) return await renderAdminDashboard(container, user, navigate);
            if (role === ROLES.SUPPORT) return await renderSupportDashboard(container, user, navigate);
        }
"""
new_block = """        if (route === "overview" || route === "mentor-edu") {
            if (role === ROLES.STUDENT) return await renderStudentDashboard(container, user, navigate);
            if (role === ROLES.TEACHER) return await renderTeacherDashboard(container, user, navigate);
            if (role === ROLES.ADMIN) return await renderAdminDashboard(container, user, navigate);
            if (role === ROLES.SUPPORT) return await renderSupportDashboard(container, user, navigate);
        }
"""
if old_block not in main_text and new_block not in main_text:
    raise SystemExit("Não consegui localizar o bloco de overview em frontend/js/main.js.")
if old_block in main_text:
    main_text = main_text.replace(old_block, new_block, 1)
    main_js.write_text(main_text, encoding="utf-8")
    changed.append(str(main_js))
elif new_block in main_text:
    main_js.write_text(main_text, encoding="utf-8")
    if str(main_js) not in changed:
        changed.append(str(main_js))

if mentor_ai_css.exists():
    css_text = mentor_ai_css.read_text(encoding="utf-8-sig", errors="ignore")
    backup_file(mentor_ai_css, ".backup_menu_v1_4")
    marker = "/* MENTOR_EDU_MENU_REORG_V1_4 */"
    css_fix = """

/* MENTOR_EDU_MENU_REORG_V1_4 */
#mentor-ai-nav-item{
  display:none !important;
}
"""
    if marker not in css_text:
        mentor_ai_css.write_text(css_text.rstrip() + css_fix + "
", encoding="utf-8")
        changed.append(str(mentor_ai_css))

print("")
print("REORGANIZAÇÃO DO MENU MENTOR EDU V1.4 APLICADA COM SUCESSO.")
print("")
print("O que foi ajustado:")
print("- Mentor Edu sai do bloco visual de Disciplinas")
print("- Mentor Edu vira um grupo próprio no menu lateral")
print("- Plano de estudos sai do nível principal")
print("- Recomendações sai do nível principal")
print("- Dentro de Mentor Edu ficam:")
print("  • Conversar com Mentor.Edu")
print("  • Meu plano")
print("  • Plano indicado")
print("  • Sessões de estudo")
print("- Item injetado antigo do Mentor Edu foi ocultado")
print("")
print("Arquivos alterados:")
for item in changed:
    print("-", item)
print("")
print("Depois faça:")
print("1) Ctrl + F5")
print("2) Se ficar bom: git add frontend/js/components/sidebar.js frontend/js/core/router.js frontend/js/main.js")
print("3) Se existir: git add frontend/mentor-ai-student.css")
print("4) git commit -m "fix: reorganiza menu do Mentor Edu no aluno"")
print("5) git push origin main")
print("")
print("Backend e banco: nenhuma alteração.")
