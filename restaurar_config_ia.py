from pathlib import Path
import subprocess

CONFIG_PATH = Path("backend/app/core/config.py")

REQUIRED_OLD_NAMES = (
    "DATABASE_URL",
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "ENVIRONMENT",
    "CORS_ORIGINS",
)

def git(*args):
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    if result.returncode != 0:
        return None
    return result.stdout

if not CONFIG_PATH.exists():
    raise SystemExit(
        "Não encontrei backend/app/core/config.py. "
        "Rode este script na raiz do Mentor.Edu."
    )

history = git(
    "rev-list",
    "HEAD",
    "--",
    "backend/app/core/config.py",
)

if not history:
    raise SystemExit(
        "Não consegui consultar o histórico do config.py."
    )

healthy = None
healthy_commit = None

for commit in history.splitlines():
    content = git(
        "show",
        f"{commit}:backend/app/core/config.py",
    )
    if not content:
        continue

    if all(name in content for name in REQUIRED_OLD_NAMES):
        healthy = content
        healthy_commit = commit
        break

if not healthy:
    raise SystemExit(
        "Não encontrei no histórico uma versão do config.py "
        "contendo todas as configurações originais."
    )

clean = healthy

for marker in (
    "# Mentor Edu AI",
    "# MENTOR EDU AI",
):
    if marker in clean:
        clean = clean.split(marker, 1)[0].rstrip() + "\n"
        break

if "import os" not in clean:
    clean = "import os\n" + clean

ai_block = (
    "\n\n# =========================================================\n"
    "# MENTOR EDU AI\n"
    "# =========================================================\n\n"
    "OPENAI_API_KEY = os.getenv(\n"
    "    \"OPENAI_API_KEY\",\n"
    "    \"\"\n"
    ").strip()\n\n"
    "AI_MODEL_FAST = os.getenv(\n"
    "    \"AI_MODEL_FAST\",\n"
    "    \"gpt-6-luna\"\n"
    ").strip()\n\n"
    "AI_MODEL_SMART = os.getenv(\n"
    "    \"AI_MODEL_SMART\",\n"
    "    \"gpt-6.1-sol\"\n"
    ").strip()\n"
)

final_text = clean.rstrip() + ai_block + "\n"

needed = REQUIRED_OLD_NAMES + (
    "OPENAI_API_KEY",
    "AI_MODEL_FAST",
    "AI_MODEL_SMART",
)

missing = [
    name for name in needed
    if name not in final_text
]

if missing:
    raise SystemExit(
        "Abortado. Ainda faltariam estas configurações: "
        + ", ".join(missing)
    )

compile(
    final_text,
    str(CONFIG_PATH),
    "exec",
)

backup = CONFIG_PATH.with_name(
    "config.py.backup_antes_restauro"
)

backup.write_text(
    CONFIG_PATH.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    ),
    encoding="utf-8",
)

CONFIG_PATH.write_text(
    final_text,
    encoding="utf-8",
)

print("")
print("CONFIG.PY RESTAURADO COM SUCESSO.")
print("Versão-base recuperada do commit:", healthy_commit[:10])
print("")
print("Mantidas/restauradas:")
for name in REQUIRED_OLD_NAMES:
    print("-", name)

print("")
print("Adicionadas para a IA:")
print("- OPENAI_API_KEY")
print("- AI_MODEL_FAST")
print("- AI_MODEL_SMART")
print("")
print("Backup criado em:")
print("backend/app/core/config.py.backup_antes_restauro")
print("")
print("Agora teste:")
print("cd backend")
print("python -c \"from app.main import app; print('BACKEND CARREGOU:', app.title)\"")
