from pathlib import Path

ROOT = Path(".")
ROUTER = ROOT / "frontend" / "js" / "core" / "router.js"

if not ROUTER.exists():
    raise SystemExit(
        "Não encontrei frontend/js/core/router.js. "
        "Rode este script na raiz do Mentor.Edu."
    )

text = ROUTER.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

MARKER = '"mentor-edu": "Mentor Edu"'

if MARKER in text:
    print("ETAPA 2 já está aplicada. Nenhuma alteração feita.")
    raise SystemExit(0)

anchor = '    overview: "Dashboard",\n'

if anchor not in text:
    raise SystemExit(
        'Não encontrei a entrada overview: "Dashboard" em router.js. '
        "Nenhum arquivo foi alterado."
    )

new_text = text.replace(
    anchor,
    anchor + '    "mentor-edu": "Mentor Edu",\n',
    1,
)

ROUTER.write_text(
    new_text,
    encoding="utf-8",
)

print("")
print("ETAPA 2 — ROTA MENTOR EDU APLICADA COM SUCESSO.")
print("")
print("Somente este arquivo foi alterado:")
print("- frontend/js/core/router.js")
print("")
print("Agora #/mentor-edu é reconhecido oficialmente como:")
print("- Mentor Edu")
print("")
print("NÃO foram alterados:")
print("- login")
print("- main.js")
print("- sidebar.js")
print("- backend")
print("- banco")
print("- CSS")
print("- IA")
print("")
print("Atualize com Ctrl + F5.")
print("Clique em Mentor Edu > Conversar com Mentor.Edu.")
print("Nesta etapa ainda aparecerá uma página genérica/placeholder.")
print("")
print("Se algo der errado:")
print("git restore frontend/js/core/router.js")
