from pathlib import Path
import re

ROOT = Path(".")

dashboard = ROOT / "frontend/dashboard.html"
if dashboard.exists():
    text = dashboard.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r'\s*<link rel="stylesheet" href="css/admin-polish\.css\?v=[^"]+">\s*', "\n    ", text)
    dashboard.write_text(text, encoding="utf-8", newline="\n")

EXTS = {".js", ".html", ".css"}
replacements = {
    "UsuÃ¡rios": "Usuários",
    "MatrÃ­culas": "Matrículas",
    "HorÃ¡rios": "Horários",
    "CalendÃ¡rio acadÃªmico": "Calendário acadêmico",
    "AvaliaÃ§Ãµes": "Avaliações",
    "RelatÃ³rios": "Relatórios",
    "ConfiguraÃ§Ãµes": "Configurações",
    "AdministraÃ§Ã£o": "Administração",
    "FrequÃªncia": "Frequência",
    "NotificaÃ§Ãµes": "Notificações",
    "DireÃ§Ã£o": "Direção",
    "CiÃªncias": "Ciências",
    "TÃ©cnica": "Técnica",
    "ReuniÃ£o": "Reunião",
    "DescriÃ§Ã£o": "Descrição",
    "instituiÃ§Ã£o": "instituição",
    "avaliaÃ§Ã£o": "avaliação",
}

def fix_text(text):
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    for _ in range(2):
        if not any(m in text for m in ("Ã", "Â", "â€", "�")):
            break
        improved = None
        for enc in ("cp1252", "latin1"):
            try:
                candidate = text.encode(enc).decode("utf-8")
                before = text.count("Ã") + text.count("Â") + text.count("�")
                after = candidate.count("Ã") + candidate.count("Â") + candidate.count("�")
                if after < before:
                    improved = candidate
                    break
            except Exception:
                pass
        if improved is None:
            break
        text = improved
    return text

changed = []
for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in EXTS:
        continue
    if ".git" in p.parts or ".venv" in p.parts:
        continue
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    fixed = fix_text(text)
    if fixed != text:
        p.write_text(fixed, encoding="utf-8", newline="\n")
        changed.append(str(p))

profile_css = ROOT / "frontend/css/admin-profile-only.css"
profile_css.write_text("""
.admin-profile-shell{max-width:1120px}
.admin-profile-head{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:16px;padding-bottom:20px;margin-bottom:22px;border-bottom:1px solid #edf0f4}
.admin-profile-avatar{width:58px;height:58px;display:grid;place-items:center;border-radius:16px;color:#fff;background:linear-gradient(135deg,#123966,#2f80ed);font-weight:850;box-shadow:0 10px 20px rgba(27,115,223,.18)}
.admin-profile-eyebrow{display:block;margin-bottom:4px;color:#2f80ed;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.08em}
.admin-profile-head h3{margin:0;font-size:20px}
.admin-profile-head p{margin-top:4px;color:#667085;font-size:12px}
.admin-role-chip{min-height:31px;padding:0 12px;display:inline-flex;align-items:center;border-radius:999px;color:#174b8a;background:#eaf3ff;font-size:10px;font-weight:800}
.admin-profile-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.admin-profile-grid input,.admin-profile-grid textarea{border-radius:12px}
.admin-profile-footer{margin-top:22px;padding-top:18px;border-top:1px solid #edf0f4;display:flex;align-items:center;justify-content:space-between;gap:16px}
@media(max-width:760px){.admin-profile-grid{grid-template-columns:1fr}.admin-profile-grid .form-span-2{grid-column:auto}.admin-profile-head{grid-template-columns:auto 1fr}.admin-role-chip{grid-column:1/-1;width:max-content}}
""".strip(), encoding="utf-8", newline="\n")

if dashboard.exists():
    text = dashboard.read_text(encoding="utf-8", errors="ignore")
    if "admin-profile-only.css" not in text:
        anchor = '<link rel="stylesheet" href="css/responsive.css">'
        text = text.replace(anchor, '<link rel="stylesheet" href="css/admin-profile-only.css?v=20.2">\n    ' + anchor)
    dashboard.write_text(text, encoding="utf-8", newline="\n")

print("Correção concluída.")
print("Arquivos corrigidos:", len(changed))
for p in changed:
    print(" -", p)
