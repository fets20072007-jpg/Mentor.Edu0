from pathlib import Path
import re

root = Path(".")

# 1) Remove hotfixes visuais anteriores da sidebar que não devem mais atuar.
dashboard = root / "frontend/dashboard.html"
if dashboard.exists():
    text = dashboard.read_text(encoding="utf-8-sig", errors="ignore")
    text = re.sub(
        r'\s*<link rel="stylesheet" href="css/sidebar-active-fix\.css\?v=[^"]+">\s*',
        "\n    ",
        text
    )
    text = re.sub(
        r'\s*<link rel="stylesheet" href="css/admin-polish\.css\?v=[^"]+">\s*',
        "\n    ",
        text
    )

    # Inclui apenas o CSS corretivo desta revisão.
    if "admin-correction.css" not in text:
        anchor = '<link rel="stylesheet" href="css/responsive.css">'
        text = text.replace(
            anchor,
            '<link rel="stylesheet" href="css/admin-correction.css?v=21.0">\n    ' + anchor
        )

    # Força nova versão do JS principal.
    text = re.sub(
        r'js/main\.js\?v=[^"]+',
        'js/main.js?v=21.0',
        text
    )

    # Corrige aria label caso esteja corrompido.
    text = text.replace("NavegaÃ§Ã£o principal", "Navegação principal")
    dashboard.write_text(text, encoding="utf-8", newline="\n")

# 2) Corrige SOMENTE textos da sidebar, sem alterar sua lógica.
sidebar = root / "frontend/js/components/sidebar.js"
if sidebar.exists():
    text = sidebar.read_text(encoding="utf-8-sig", errors="ignore")
    fixes = {
        "InÃ­cio": "Início",
        "avaliaÃ§Ãµes": "avaliações",
        "AvaliaÃ§Ãµes": "Avaliações",
        "CorreÃ§Ãµes": "Correções",
        "LiberaÃ§Ã£o": "Liberação",
        "PendÃªncias": "Pendências",
        "questÃµes": "questões",
        "QuestÃµes": "Questões",
        "pedagÃ³gica": "pedagógica",
        "EvoluÃ§Ã£o": "Evolução",
        "CapÃ­tulos": "Capítulos",
        "ConteÃºdos": "Conteúdos",
        "ConfiguraÃ§Ãµes": "Configurações",
        "UsuÃ¡rios": "Usuários",
        "MatrÃ­culas": "Matrículas",
        "HorÃ¡rios": "Horários",
        "CalendÃ¡rio": "Calendário",
        "acadÃªmico": "acadêmico",
        "RelatÃ³rios": "Relatórios"
    }
    for bad, good in fixes.items():
        text = text.replace(bad, good)
    sidebar.write_text(text, encoding="utf-8", newline="\n")

# 3) Remove arquivos antigos se existirem.
for name in (
    "frontend/css/sidebar-active-fix.css",
    "frontend/css/admin-polish.css"
):
    p = root / name
    if p.exists():
        p.unlink()

print("Correção aplicada.")
print("- Sidebar voltou ao CSS original do projeto.")
print("- Textos da sidebar corrigidos.")
print("- CSS de filtros/relatórios ativado.")
print("- main.js atualizado para v21.0.")
