from pathlib import Path

ROOT = Path(".")
CONFIG = ROOT / "backend/app/core/config.py"
CLIENT = ROOT / "backend/app/services/ai/mentor_client.py"
ROUTER = ROOT / "backend/app/router/ai/mentor.py"

for path in (CONFIG, CLIENT, ROUTER):
    if not path.exists():
        raise SystemExit(f"Arquivo não encontrado: {path}")

config = CONFIG.read_text(encoding="utf-8-sig")

if "AI_PROVIDER =" not in config:
    config += "\n\n# PROVEDOR DE IA\n"
    config += 'AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").strip().lower()\n'
    config += 'AI_API_KEY = os.getenv("AI_API_KEY", "").strip()\n'
    config += 'AI_BASE_URL = os.getenv("AI_BASE_URL", "").strip()\n'

compile(config, str(CONFIG), "exec")
CONFIG.write_text(config, encoding="utf-8")

client = '''import json
import re
from typing import Any

from openai import OpenAI

from app.core.config import (
    OPENAI_API_KEY,
    AI_PROVIDER,
    AI_API_KEY,
    AI_BASE_URL,
    AI_MODEL_FAST,
    AI_MODEL_SMART,
)


class MentorAIUnavailable(RuntimeError):
    pass


def _provider_settings() -> dict[str, str]:
    provider = (AI_PROVIDER or "groq").strip().lower()

    if provider == "groq":
        return {
            "provider": "groq",
            "api_key": AI_API_KEY,
            "base_url": AI_BASE_URL or "https://api.groq.com/openai/v1",
        }

    if provider == "openai":
        return {
            "provider": "openai",
            "api_key": AI_API_KEY or OPENAI_API_KEY,
            "base_url": AI_BASE_URL or "https://api.openai.com/v1",
        }

    raise MentorAIUnavailable(
        f"AI_PROVIDER não suportado: {provider}"
    )


def _client() -> tuple[OpenAI, str]:
    settings = _provider_settings()

    if not settings["api_key"]:
        raise MentorAIUnavailable(
            f"Chave da IA não configurada para {settings['provider']}."
        )

    return (
        OpenAI(
            api_key=settings["api_key"],
            base_url=settings["base_url"],
        ),
        settings["provider"],
    )


def ask_text(
    *,
    instructions: str,
    user_input: str,
    smart: bool = False,
) -> dict[str, Any]:
    client, provider = _client()

    model = AI_MODEL_SMART if smart else AI_MODEL_FAST

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_input,
    )

    return {
        "provider": provider,
        "model": model,
        "text": response.output_text.strip(),
        "response_id": response.id,
    }


def _extract_json(text: str) -> Any:
    raw = (text or "").strip()

    if raw.startswith("```"):
        raw = re.sub(
            r"^```(?:json)?\\s*",
            "",
            raw,
            flags=re.IGNORECASE,
        )
        raw = re.sub(
            r"\\s*```$",
            "",
            raw,
        )

    try:
        return json.loads(raw)

    except json.JSONDecodeError:
        match = re.search(
            r"(\\{[\\s\\S]*\\}|\\[[\\s\\S]*\\])",
            raw,
        )

        if not match:
            raise RuntimeError(
                "A IA não retornou JSON válido."
            )

        return json.loads(match.group(1))


def ask_json(
    *,
    instructions: str,
    user_input: str,
    smart: bool = True,
) -> dict[str, Any]:
    result = ask_text(
        instructions=(
            instructions.strip()
            + "\\n\\nResponda SOMENTE com JSON válido, "
              "sem markdown e sem texto fora do JSON."
        ),
        user_input=user_input,
        smart=smart,
    )

    return {
        "provider": result["provider"],
        "model": result["model"],
        "response_id": result["response_id"],
        "data": _extract_json(result["text"]),
    }
'''

compile(client, str(CLIENT), "exec")
CLIENT.write_text(client, encoding="utf-8")

router = ROUTER.read_text(encoding="utf-8-sig")

if '@router.post("/test-ai")' not in router:
    router += '''


@router.post("/test-ai")
def test_ai_provider(request: Request):
    if not AI_TEST_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="AI_TEST_TOKEN não configurado.",
        )

    supplied = request.headers.get("X-Mentor-AI-Test")

    if supplied != AI_TEST_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Token de teste inválido.",
        )

    try:
        result = ask_text(
            instructions=(
                "Você está realizando um teste técnico do Mentor.Edu. "
                "Responda em português brasileiro em uma única frase curta."
            ),
            user_input=(
                "Confirme que a IA do Mentor.Edu está funcionando. "
                "Comece exatamente com: Mentor.Edu IA online"
            ),
            smart=False,
        )
    except Exception as error:
        _raise_ai_error(error)

    return {
        "status": "ok",
        "service": "Mentor Edu AI",
        "provider": result.get("provider"),
        "model": result["model"],
        "response_id": result["response_id"],
        "resposta": result["text"],
    }
'''

compile(router, str(ROUTER), "exec")
ROUTER.write_text(router, encoding="utf-8")

print("GROQ PROVIDER V1 APLICADO COM SUCESSO.")
print("Configure no Render:")
print("AI_PROVIDER=groq")
print("AI_API_KEY=<sua chave Groq>")
print("AI_BASE_URL=https://api.groq.com/openai/v1")
print("AI_MODEL_FAST=openai/gpt-oss-20b")
print("AI_MODEL_SMART=openai/gpt-oss-120b")
