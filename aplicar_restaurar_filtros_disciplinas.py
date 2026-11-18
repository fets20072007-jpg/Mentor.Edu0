from pathlib import Path
import re

dashboard = Path("frontend/dashboard.html")

if not dashboard.exists():
    raise SystemExit(
        "Rode este script na raiz do Mentor.Edu."
    )

text = dashboard.read_text(
    encoding="utf-8-sig"
)

if "subject-filters-restore.css" not in text:
    anchor = (
        '<link rel="stylesheet" '
        'href="css/responsive.css">'
    )

    if anchor not in text:
        raise RuntimeError(
            "Não encontrei responsive.css."
        )

    text = text.replace(
        anchor,
        '<link rel="stylesheet" '
        'href="css/subject-filters-restore.css?v=24.1">\n    '
        + anchor,
        1
    )

text = re.sub(
    r'js/main\.js\?v=[^"]+',
    'js/main.js?v=24.1',
    text
)

dashboard.write_text(
    text,
    encoding="utf-8",
    newline="\n"
)

print("FILTROS DE DISCIPLINAS RESTAURADOS.")
print("- Filtrar por turma")
print("- Pesquisar disciplina, professor ou área")
print("- Editar/Desfazer/Reativar preservados")
