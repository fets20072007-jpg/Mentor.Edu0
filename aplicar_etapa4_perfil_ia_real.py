from pathlib import Path
import shutil

ROOT = Path(".")
FRONT = ROOT / "frontend"
HERE = Path(__file__).resolve().parent
FILES = HERE / "files"

PAGE = FRONT / "js" / "pages" / "student" / "mentor-edu.js"
CSS = FRONT / "css" / "mentor-ai-page.css"
CLIENT = FRONT / "js" / "api" / "client.js"

for path in (PAGE, CSS, CLIENT):
    if not path.exists():
        raise SystemExit(f"Arquivo necessário não encontrado: {path}")

def read(path):
    return path.read_text(encoding="utf-8-sig", errors="strict")

original_page = read(PAGE)
original_css = read(CSS)

# Segurança: só substitui a página que foi criada nas Etapas 3/3.1.
if "renderStudentMentorEdu" not in original_page or "MENTOR EDU • INSIGHTS COM IA" not in original_page:
    raise SystemExit(
        "O mentor-edu.js não corresponde à página visual esperada. "
        "Nenhuma alteração foi gravada."
    )

new_page = (FILES / "mentor-edu.js").read_text(encoding="utf-8")
css_add = (FILES / "profile-real.css").read_text(encoding="utf-8")

# Confirma que o cliente da API suporta GET.
client = read(CLIENT)
if "get:" not in client or "apiRequest" not in client:
    raise SystemExit(
        "O frontend/js/api/client.js não tem o cliente API esperado. "
        "Nenhuma alteração foi gravada."
    )

if "MENTOR_EDU_PROFILE_REAL_V1" not in original_css:
    new_css = original_css.rstrip() + "\n\n" + css_add.strip() + "\n"
else:
    new_css = original_css

checks = {
    "import api": 'import { api } from "../../api/client.js";' in new_page,
    "endpoint profile": 'api.get("/mentor-ai/student/profile")' in new_page,
    "cache 5 min": "PROFILE_CACHE_MS = 5 * 60 * 1000" in new_page,
    "perfil real": "applyProfileData" in new_page,
    "erro isolado": "applyProfileError" in new_page,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit(
        "Validação da Etapa 4 falhou. Nenhum arquivo foi gravado: "
        + ", ".join(failed)
    )

backup_page = PAGE.with_name(PAGE.name + ".backup_etapa4_perfil")
backup_css = CSS.with_name(CSS.name + ".backup_etapa4_perfil")

if not backup_page.exists():
    backup_page.write_text(original_page, encoding="utf-8")
if not backup_css.exists():
    backup_css.write_text(original_css, encoding="utf-8")

PAGE.write_text(new_page, encoding="utf-8")
CSS.write_text(new_css, encoding="utf-8")

print("")
print("ETAPA 4 — PERFIL REAL DA IA APLICADO COM SUCESSO.")
print("")
print("Alterados somente:")
print("- frontend/js/pages/student/mentor-edu.js")
print("- frontend/css/mentor-ai-page.css")
print("")
print("Conectado:")
print("- GET /mentor-ai/student/profile")
print("- perfil de aprendizagem")
print("- pontos fortes")
print("- pontos para melhorar")
print("- sugestões do Mentor")
print("- resumo lateral")
print("")
print("Proteções:")
print("- cache de 5 minutos em sessionStorage")
print("- botão Atualizar análise força nova consulta")
print("- erro da IA fica isolado dentro da página")
print("- login e Dashboard não dependem desta chamada")
print("")
print("O chat ainda é visual. Ele será conectado na Etapa 5.")
print("Use Ctrl + F5 e abra Mentor Edu.")
