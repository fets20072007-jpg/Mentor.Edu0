from pathlib import Path
import subprocess

REQ_PATH = Path("backend/requirements.txt")

if not REQ_PATH.exists():
    raise SystemExit(
        "Não encontrei backend/requirements.txt. "
        "Rode este script na raiz do Mentor.Edu."
    )


def run_git(*args):
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


def is_healthy_requirements(text):
    if not text:
        return False

    lower = text.lower()

    # O projeto FastAPI precisa destes pontos básicos.
    return (
        "fastapi" in lower
        and "uvicorn" in lower
        and (
            "sqlalchemy" in lower
            or "psycopg" in lower
            or "psycopg2" in lower
        )
    )


# 1. Procura no histórico do Git uma versão saudável.
history = run_git(
    "rev-list",
    "HEAD",
    "--",
    "backend/requirements.txt",
)

if not history:
    raise SystemExit(
        "Não consegui consultar o histórico do Git."
    )

healthy = None
healthy_commit = None

for commit in history.splitlines():
    content = run_git(
        "show",
        f"{commit}:backend/requirements.txt",
    )

    if is_healthy_requirements(content):
        healthy = content
        healthy_commit = commit
        break


if not healthy:
    raise SystemExit(
        "Não encontrei no histórico uma versão saudável "
        "do backend/requirements.txt."
    )


# 2. Normaliza e preserva todas as dependências antigas.
lines = []

for raw in healthy.splitlines():
    line = raw.strip()

    if not line:
        continue

    # Remove openai antiga para recolocar uma única vez.
    if line.lower().startswith("openai"):
        continue

    lines.append(line)


# 3. Adiciona a OpenAI sem apagar nada.
lines.append("openai>=2.0.0")

REQ_PATH.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)


# 4. Checagem rápida.
final_text = REQ_PATH.read_text(
    encoding="utf-8",
)

if not is_healthy_requirements(final_text):
    raise SystemExit(
        "A restauração terminou, mas o arquivo ainda "
        "não contém as dependências principais."
    )


print("")
print("REQUIREMENTS RESTAURADO COM SUCESSO.")
print("")
print(
    "Versão saudável recuperada do commit:",
    healthy_commit[:10],
)
print("")
print("Preservado:")
print("- FastAPI")
print("- Uvicorn")
print("- SQLAlchemy / PostgreSQL")
print("- demais dependências antigas")
print("- OpenAI adicionada ao final")
print("")
print("Agora rode:")
print("git add backend/requirements.txt")
print('git commit -m "fix: restaura dependencias do backend com OpenAI"')
print("git push origin main")
