from pathlib import Path

ROOT = Path(".")
ROUTER = ROOT / "backend/app/router/ai/mentor.py"

if not ROUTER.exists():
    raise SystemExit("Não encontrei backend/app/router/ai/mentor.py. Rode este script na raiz do Mentor.Edu.")

text = ROUTER.read_text(encoding="utf-8-sig", errors="strict")

if "TUTOR_PEDAGOGICO_V1_2" not in text:
    raise SystemExit("Tutor V1.2 não encontrado. Aplique a V1.2 antes desta correção.")

if "TUTOR_PEDAGOGICO_V1_3" in text:
    print("Tutor Aluno V1.3 já está aplicado.")
    raise SystemExit(0)

needle = (
    "PRECISÃO\n"
    "Antes de responder, confira:\n"
    "1. qual grandeza está sendo pedida;\n"
    "2. qual definição corresponde a ela;\n"
    "3. se as unidades são coerentes;\n"
    "4. se a fórmula realmente responde à pergunta.\n"
)

replacement = (
    "PRECISÃO\n"
    "Antes de responder, confira:\n"
    "1. qual grandeza está sendo pedida;\n"
    "2. qual definição corresponde a ela;\n"
    "3. se as unidades são coerentes;\n"
    "4. se a fórmula realmente responde à pergunta;\n"
    "5. refaça mentalmente toda conta numérica antes de apresentar o resultado;\n"
    "6. se houver alternativas, compare o valor calculado com CADA alternativa;\n"
    "7. nunca marque uma alternativa que não corresponda ao resultado calculado;\n"
    "8. se nenhuma alternativa corresponder, diga explicitamente:\n"
    "   \"Nenhuma das alternativas corresponde ao resultado calculado.\"\n"
    "9. não arredonde um valor apenas para fazê-lo caber em uma alternativa;\n"
    "10. quando arredondar, informe o valor exato ou aproximado e o critério.\n"
)

if needle not in text:
    raise SystemExit("Não encontrei o bloco PRECISÃO esperado no Tutor V1.2.")

text = text.replace(needle, replacement, 1)

marker = "def _run_student_tutor(\n"

route_code = r'''# TUTOR_PEDAGOGICO_V1_3

def _tutor_requires_smart_model(mensagem: str) -> bool:
    """
    Usa o modelo mais forte apenas quando a pergunta parece exigir
    raciocínio matemático/físico, fórmulas, cálculo ou múltipla escolha.
    """
    msg = (mensagem or "").lower()

    stem_terms = (
        "velocidade", "aceleração", "aceleracao", "cinemática", "cinematica",
        "força", "forca", "energia", "potência", "potencia", "trabalho",
        "momento", "vetor", "vetores", "física", "fisica",
        "matemática", "matematica", "equação", "equacao", "função", "funcao",
        "derivada", "integral", "limite", "fração", "fracao",
        "porcentagem", "ângulo", "angulo", "trigonometria",
        "sen", "cos", "tan", "delta", "Δ", "m/s", "km/h",
        "newton", "joule", "watt",
    )

    option_terms = (
        "(a)", "(b)", "(c)", "(d)", "(e)",
        "alternativa", "alternativas", "múltipla escolha", "multipla escolha",
    )

    math_symbols = (
        "=", "+", "-", "*", "/", "^", "√", "²", "³",
    )

    has_stem_term = any(term in msg for term in stem_terms)
    has_options = any(term in msg for term in option_terms)
    has_math = any(symbol in msg for symbol in math_symbols)
    has_digits = any(ch.isdigit() for ch in msg)

    return has_stem_term or has_options or (has_math and has_digits)
'''

if marker not in text:
    raise SystemExit("Não encontrei _run_student_tutor para inserir o roteamento.")

text = text.replace(marker, route_code + "\n\n" + marker, 1)

needle_call = (
    "    result = ask_text(\n"
    "        instructions=_tutor_instructions(),\n"
    "        user_input=(\n"
)

if needle_call not in text:
    raise SystemExit("Não encontrei a chamada ask_text do Tutor.")

text = text.replace(
    needle_call,
    (
        "    use_smart_model = _tutor_requires_smart_model(mensagem)\n\n"
        "    result = ask_text(\n"
        "        instructions=_tutor_instructions(),\n"
        "        user_input=(\n"
    ),
    1,
)

if "        smart=False,\n" not in text:
    raise SystemExit("Não encontrei smart=False no Tutor.")

text = text.replace("        smart=False,\n", "        smart=use_smart_model,\n", 1)

text = text.replace('"tutor_version": "1.2"', '"tutor_version": "1.3"', 1)

needle_return = (
    '        "provider": result.get("provider"),\n'
    '        "model": result["model"],\n'
)

if needle_return not in text:
    raise SystemExit("Não encontrei o bloco de retorno do Tutor.")

text = text.replace(
    needle_return,
    (
        '        "provider": result.get("provider"),\n'
        '        "model_route": "smart" if use_smart_model else "fast",\n'
        '        "model": result["model"],\n'
    ),
    1,
)

compile(text, str(ROUTER), "exec")

backup = ROUTER.with_name("mentor.py.backup_tutor_v1_3")
if not backup.exists():
    backup.write_text(ROUTER.read_text(encoding="utf-8-sig", errors="strict"), encoding="utf-8")

ROUTER.write_text(text, encoding="utf-8")

print("")
print("TUTOR IA DO ALUNO V1.3 APLICADO COM SUCESSO.")
print("")
print("Alterações:")
print("- checagem obrigatória de contas e alternativas")
print("- não arredonda para forçar encaixe em alternativa")
print("- avisa quando nenhuma alternativa corresponde")
print("- roteamento adaptativo fast/smart")
print("- Física/Matemática/cálculos usam AI_MODEL_SMART")
print("- perguntas simples continuam em AI_MODEL_FAST")
print("- tutor_version=1.3")
print("")
print("Banco de dados: nenhuma alteração.")
print("Frontend: nenhuma alteração.")
print("Cronograma: nenhuma alteração.")
