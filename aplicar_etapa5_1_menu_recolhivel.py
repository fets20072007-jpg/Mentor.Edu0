from pathlib import Path

ROOT = Path(".")
SIDEBAR = ROOT / "frontend" / "js" / "components" / "sidebar.js"

if not SIDEBAR.exists():
    raise SystemExit(
        "Não encontrei frontend/js/components/sidebar.js."
    )

text = SIDEBAR.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

MARKER = "MENTOR_EDU_COLLAPSIBLE_FIX_V5_1"

if MARKER in text:
    print("ETAPA 5.1 já está aplicada.")
    raise SystemExit(0)

old = '{ route: "mentor-edu", label: "Mentor Edu", icon: "mentor-ai", children: ['
new = '/* MENTOR_EDU_COLLAPSIBLE_FIX_V5_1 */\n        { label: "Mentor Edu", icon: "mentor-ai", children: ['

if old not in text:
    # Aceita também a versão em aspas simples, caso tenha sido formatada.
    old_alt = "{ route: 'mentor-edu', label: 'Mentor Edu', icon: 'mentor-ai', children: ["
    if old_alt in text:
        old = old_alt
        new = "/* MENTOR_EDU_COLLAPSIBLE_FIX_V5_1 */\n        { label: 'Mentor Edu', icon: 'mentor-ai', children: ["
    else:
        raise SystemExit(
            "Não encontrei o grupo Mentor Edu no formato esperado. "
            "Nenhuma alteração foi gravada."
        )

new_text = text.replace(old, new, 1)

# Segurança: o filho que realmente abre a página precisa permanecer.
required = [
    'route: "mentor-edu"',
    'label: "Conversar com Mentor.Edu"',
    'label: "Meu plano"',
    'label: "Plano indicado"',
    'label: "Sessões de estudo"',
]

missing = [item for item in required if item not in new_text]
if missing:
    raise SystemExit(
        "Validação falhou. Nenhuma alteração foi gravada. Faltou: "
        + ", ".join(missing)
    )

backup = SIDEBAR.with_name(
    SIDEBAR.name + ".backup_etapa5_1_menu_recolhivel"
)

if not backup.exists():
    backup.write_text(
        text,
        encoding="utf-8",
    )

SIDEBAR.write_text(
    new_text,
    encoding="utf-8",
)

print("")
print("ETAPA 5.1 — MENU MENTOR EDU RECOLHÍVEL APLICADO COM SUCESSO.")
print("")
print("Alterado somente:")
print("- frontend/js/components/sidebar.js")
print("")
print("Agora:")
print("- clicar em Mentor Edu / setinha abre o grupo")
print("- clicar novamente fecha o grupo")
print("- Conversar com Mentor.Edu abre a página da IA")
print("- Meu plano / Plano indicado / Sessões continuam disponíveis")
print("")
print("NÃO foram alterados:")
print("- chat")
print("- IA")
print("- main.js")
print("- router.js")
print("- dashboard")
print("- backend")
print("")
print("Use Ctrl + F5 e teste abrir/fechar o menu Mentor Edu.")
