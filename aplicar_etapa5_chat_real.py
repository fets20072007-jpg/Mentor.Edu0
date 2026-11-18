from pathlib import Path

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
client = read(CLIENT)

required_current = [
    "renderStudentMentorEdu",
    "loadStudentProfile",
    'api.get("/mentor-ai/student/profile")',
    "MENTOR_EDU_METRICS_FIX_V4_1",
]
missing = [item for item in required_current if item not in original_page]
if missing:
    raise SystemExit(
        "A página atual não corresponde à Etapa 4.1. "
        "Nenhuma alteração foi gravada. Faltou: "
        + ", ".join(missing)
    )

if "post:" not in client or "apiRequest" not in client:
    raise SystemExit(
        "O cliente da API não possui POST no formato esperado. "
        "Nenhuma alteração foi gravada."
    )

new_page = (FILES / "mentor-edu.js").read_text(encoding="utf-8")
css_add = (FILES / "chat-real.css").read_text(encoding="utf-8")

checks = {
    "endpoint tutor": 'api.post(' in new_page and '"/mentor-ai/student/tutor"' in new_page,
    "histórico": "readChatHistory" in new_page and "writeChatHistory" in new_page,
    "thinking": "data-chat-thinking" in new_page,
    "modo expandido preservado": "is-fullscreen" in new_page,
    "perfil preservado": 'api.get("/mentor-ai/student/profile")' in new_page,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit(
        "Validação da Etapa 5 falhou. Nenhum arquivo foi gravado: "
        + ", ".join(failed)
    )

if "MENTOR_EDU_CHAT_REAL_V5" not in original_css:
    new_css = original_css.rstrip() + "\n\n" + css_add.strip() + "\n"
else:
    new_css = original_css

backup_page = PAGE.with_name(PAGE.name + ".backup_etapa5_chat")
backup_css = CSS.with_name(CSS.name + ".backup_etapa5_chat")

if not backup_page.exists():
    backup_page.write_text(original_page, encoding="utf-8")
if not backup_css.exists():
    backup_css.write_text(original_css, encoding="utf-8")

PAGE.write_text(new_page, encoding="utf-8")
CSS.write_text(new_css, encoding="utf-8")

print("")
print("ETAPA 5 — CHAT REAL DO MENTOR EDU APLICADO COM SUCESSO.")
print("")
print("Alterados somente:")
print("- frontend/js/pages/student/mentor-edu.js")
print("- frontend/css/mentor-ai-page.css")
print("")
print("Conectado:")
print("- POST /mentor-ai/student/tutor")
print("- mensagens do aluno e do Mentor")
print("- indicador Pensando...")
print("- histórico local da conversa")
print("- continuidade com as últimas mensagens")
print("- identificação de modelo/rota quando o backend retornar")
print("- botão Limpar conversa")
print("- modo Expandir/Reduzir preservado")
print("")
print("Proteções:")
print("- erro do Tutor fica dentro do chat")
print("- perfil da Etapa 4 permanece funcionando")
print("- login e Dashboard continuam independentes")
print("")
print("Use Ctrl + F5, abra Mentor Edu e envie uma mensagem.")
