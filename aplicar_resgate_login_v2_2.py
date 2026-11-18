from pathlib import Path
import re
import shutil

ROOT = Path(".")
FRONT = ROOT / "frontend"
HERE = Path(__file__).resolve().parent
FILES = HERE / "files"

INDEX = FRONT / "index.html"
TARGET_LOGIN = FRONT / "js" / "login.js"

if not FRONT.exists():
    raise SystemExit(
        "Não encontrei a pasta frontend. Rode este script na raiz do Mentor.Edu."
    )

if not INDEX.exists():
    raise SystemExit("Não encontrei frontend/index.html.")

required = [
    FRONT / "js" / "api" / "auth.js",
    FRONT / "js" / "api" / "users.js",
    FRONT / "js" / "core" / "session.js",
    FRONT / "js" / "config.js",
]

for path in required:
    if not path.exists():
        raise SystemExit(f"Arquivo necessário do login não encontrado: {path}")

def read(path):
    return path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

# Backup do index atual.
backup = INDEX.with_name(
    "index.html.backup_login_resgate_v2_2"
)
if not backup.exists():
    backup.write_text(
        read(INDEX),
        encoding="utf-8",
    )

# Copia o login isolado.
TARGET_LOGIN.parent.mkdir(
    parents=True,
    exist_ok=True,
)
shutil.copy2(
    FILES / "login.js",
    TARGET_LOGIN,
)

html = read(INDEX)

# Remove qualquer asset da IA do LOGIN.
html = re.sub(
    r'\s*<link[^>]+href=["\'][^"\']*mentor-ai-student\.css["\'][^>]*>\s*',
    "\n",
    html,
    flags=re.I,
)

html = re.sub(
    r'\s*<link[^>]+href=["\'][^"\']*mentor-ai-page\.css["\'][^>]*>\s*',
    "\n",
    html,
    flags=re.I,
)

html = re.sub(
    r'\s*<script[^>]+src=["\'][^"\']*mentor-ai-student\.js["\'][^>]*>\s*</script>\s*',
    "\n",
    html,
    flags=re.I,
)

# O login NÃO deve mais depender de js/main.js.
module_pattern = (
    r'<script\s+type=["\']module["\']\s+'
    r'src=["\']js/(?:main|login)\.js["\']\s*></script>'
)

replacement = (
    '<script type="module" src="js/login.js?v=2.2"></script>'
)

html, count = re.subn(
    module_pattern,
    replacement,
    html,
    count=1,
    flags=re.I,
)

if count == 0:
    # Se o script tiver sido alterado para outro formato,
    # remove main.js e injeta login.js antes do body.
    html = re.sub(
        r'\s*<script[^>]+src=["\']js/main\.js["\'][^>]*>\s*</script>\s*',
        "\n",
        html,
        flags=re.I,
    )

    if "</body>" not in html:
        raise SystemExit(
            "Não encontrei </body> no frontend/index.html."
        )

    html = html.replace(
        "</body>",
        '    <script type="module" src="js/login.js?v=2.2"></script>\n</body>',
        1,
    )

INDEX.write_text(
    html,
    encoding="utf-8",
)

print("")
print("LOGIN RESGATE V2.2 APLICADO COM SUCESSO.")
print("")
print("Mudanças:")
print("- login não depende mais de js/main.js")
print("- criado frontend/js/login.js")
print("- removidos scripts/CSS da IA da página de login")
print("- dashboard continua usando js/main.js normalmente")
print("- erros de autenticação agora aparecem na própria tela")
print("")
print("Teste:")
print("1. Pare e reinicie o servidor do frontend")
print("2. Abra http://127.0.0.1:5500/index.html")
print("3. Pressione Ctrl + F5")
print("4. Faça login")
print("")
print("Se funcionar, NÃO aplique novamente os patches V2/V2.1 antigos.")
