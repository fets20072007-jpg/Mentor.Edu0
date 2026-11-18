from pathlib import Path

ROOT = Path('.')
SIDEBAR = ROOT / 'frontend' / 'js' / 'components' / 'sidebar.js'

if not SIDEBAR.exists():
    raise SystemExit('Não encontrei frontend/js/components/sidebar.js.')

text = SIDEBAR.read_text(encoding='utf-8-sig', errors='strict')
MARKER = 'MENTOR_EDU_MANUAL_COLLAPSE_V5_1_1'

if MARKER in text:
    print('ETAPA 5.1.1 já está aplicada.')
    raise SystemExit(0)

old_toggle = '    root.querySelectorAll("[data-nav-group]").forEach(group => {\n        const button = group.querySelector(".nav-group-toggle");\n        button.addEventListener("click", () => {\n            const open = group.classList.toggle("is-open");\n            button.setAttribute("aria-expanded", String(open));\n        });\n    });\n'
new_toggle = '    // MENTOR_EDU_MANUAL_COLLAPSE_V5_1_1\n    root.querySelectorAll("[data-nav-group]").forEach(group => {\n        const button = group.querySelector(".nav-group-toggle");\n\n        button?.addEventListener("click", event => {\n            event.preventDefault();\n            event.stopPropagation();\n\n            const willOpen = !group.classList.contains("is-open");\n\n            group.classList.toggle("is-open", willOpen);\n            button.setAttribute("aria-expanded", String(willOpen));\n\n            if (willOpen) {\n                delete group.dataset.manualClosed;\n            } else {\n                group.dataset.manualClosed = "true";\n            }\n        });\n    });\n'
old_active = '        if (active) {\n            const group = item.closest("[data-nav-group]");\n            group?.classList.add("is-open");\n            group?.querySelector(".nav-group-toggle")?.setAttribute("aria-expanded", "true");\n        }\n'
new_active = '        if (active) {\n            const group = item.closest("[data-nav-group]");\n\n            if (group && group.dataset.manualClosed !== "true") {\n                group.classList.add("is-open");\n                group\n                    .querySelector(".nav-group-toggle")\n                    ?.setAttribute("aria-expanded", "true");\n            }\n        }\n'

if old_toggle not in text:
    raise SystemExit('Não encontrei o bloco de abrir/fechar grupos no formato esperado. Nenhuma alteração foi gravada.')
text = text.replace(old_toggle, new_toggle, 1)

if old_active not in text:
    raise SystemExit('Não encontrei o bloco de setActiveSidebarRoute no formato esperado. Nenhuma alteração foi gravada.')
text = text.replace(old_active, new_active, 1)

checks = {
    'marcador': MARKER in text,
    'manualClosed': 'group.dataset.manualClosed' in text,
    'bloqueio auto-open': 'group.dataset.manualClosed !== "true"' in text,
    'toggle explícito': 'classList.toggle("is-open", willOpen)' in text,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('Validação falhou. Nenhuma alteração foi gravada: ' + ', '.join(failed))

backup = SIDEBAR.with_name(SIDEBAR.name + '.backup_etapa5_1_1')
if not backup.exists():
    backup.write_text(SIDEBAR.read_text(encoding='utf-8-sig'), encoding='utf-8')

SIDEBAR.write_text(text, encoding='utf-8')

print('')
print('ETAPA 5.1.1 — MENU RECOLHÍVEL CORRIGIDO COM SUCESSO.')
print('')
print('Alterado somente:')
print('- frontend/js/components/sidebar.js')
print('')
print('Agora:')
print('- clique em Mentor Edu -> abre')
print('- clique novamente -> fecha')
print('- a rota ativa não reabre o grupo')
print('- clique novamente -> abre quando quiser')
print('')
print('Use Ctrl + F5.')
