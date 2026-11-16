import json
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
            r"^```(?:json)?\s*",
            "",
            raw,
            flags=re.IGNORECASE,
        )
        raw = re.sub(
            r"\s*```$",
            "",
            raw,
        )

    try:
        return json.loads(raw)

    except json.JSONDecodeError:
        match = re.search(
            r"(\{[\s\S]*\}|\[[\s\S]*\])",
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
            + "\n\nResponda SOMENTE com JSON válido, "
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
