from pathlib import Path

ROOT = Path(".")
CONFIG = ROOT / "backend/app/core/config.py"
ROUTER = ROOT / "backend/app/router/ai/mentor.py"

for path in (CONFIG, ROUTER):
    if not path.exists():
        raise SystemExit(f"Arquivo não encontrado: {path}")

config = CONFIG.read_text(encoding="utf-8-sig")

if "AI_TEST_TOKEN" not in config:
    config += "\n\nAI_TEST_TOKEN = os.getenv(\n    \"AI_TEST_TOKEN\",\n    \"\"\n).strip()\n"

compile(config, str(CONFIG), "exec")
CONFIG.write_text(config, encoding="utf-8")

router = ROUTER.read_text(encoding="utf-8-sig")

if "from fastapi import Request" not in router:
    router = "from fastapi import Request\n" + router

if "from app.core.config import AI_TEST_TOKEN" not in router:
    marker = "from app.core.permissions import ("
    if marker not in router:
        raise SystemExit("Não encontrei o bloco de imports esperado em mentor.py.")
    router = router.replace(
        marker,
        "from app.core.config import AI_TEST_TOKEN\n\n" + marker,
        1,
    )

if '@router.post("/test-openai")' not in router:
    route_block = '''

@router.post("/test-openai")
def test_openai(request: Request):
    """Teste técnico protegido da conexão Mentor.Edu -> OpenAI."""

    if not AI_TEST_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="AI_TEST_TOKEN não configurado no servidor.",
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
                "Responda em português brasileiro, em uma única frase curta."
            ),
            user_input=(
                "Confirme que a conexão com a IA está funcionando. "
                "Comece exatamente com: Mentor.Edu IA online"
            ),
            smart=False,
        )
    except Exception as error:
        _raise_ai_error(error)

    return {
        "status": "ok",
        "service": "Mentor Edu AI",
        "model": result["model"],
        "response_id": result["response_id"],
        "resposta": result["text"],
    }
'''
    router += route_block

compile(router, str(ROUTER), "exec")
ROUTER.write_text(router, encoding="utf-8")

print("")
print("TESTE OPENAI V1 ADICIONADO COM SUCESSO.")
print("")
print("Configure no Render:")
print("AI_TEST_TOKEN = uma senha aleatória escolhida por você")
print("")
print("Depois faça commit e push.")