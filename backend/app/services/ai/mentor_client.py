import json
import re
from typing import Any

from openai import OpenAI

from app.core.config import (
    OPENAI_API_KEY,
    AI_MODEL_FAST,
    AI_MODEL_SMART,
)


class MentorAIUnavailable(RuntimeError):
    pass


def _client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise MentorAIUnavailable(
            "OPENAI_API_KEY não configurada no ambiente."
        )
    return OpenAI(api_key=OPENAI_API_KEY)


def ask_text(
    *,
    instructions: str,
    user_input: str,
    smart: bool = False,
) -> dict[str, Any]:
    client = _client()
    model = AI_MODEL_SMART if smart else AI_MODEL_FAST

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_input,
    )

    return {
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
        "model": result["model"],
        "response_id": result["response_id"],
        "data": _extract_json(result["text"]),
    }
