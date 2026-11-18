from pathlib import Path
import re
import shutil
import sys

ROOT = Path.cwd()
MENTOR = ROOT / "backend" / "app" / "router" / "ai" / "mentor.py"

if not MENTOR.exists():
    raise SystemExit(
        "ERRO: não encontrei backend/app/router/ai/mentor.py.\n"
        "Abra o terminal na pasta raiz do Mentor.Edu e rode o script novamente."
    )

text = MENTOR.read_text(encoding="utf-8-sig")
original = text

backup = MENTOR.with_name("mentor.py.backup_saida_limpa_v1")
if not backup.exists():
    shutil.copy2(MENTOR, backup)

# 1) Garante import do re no mentor.py.
if "\nimport re\n" not in text:
    if text.startswith("from fastapi import Request\nimport json\n"):
        text = text.replace(
            "from fastapi import Request\nimport json\n",
            "from fastapi import Request\nimport json\nimport re\n",
            1,
        )
    elif "import json\n" in text:
        text = text.replace("import json\n", "import json\nimport re\n", 1)
    else:
        text = "import re\n" + text

# 2) Acrescenta regra de formatação limpa ao prompt do tutor.
format_rules = """
FORMATAÇÃO PARA O APLICATIVO
- a resposta será exibida diretamente no chat do Mentor.Edu;
- escreva em texto limpo e fácil de ler;
- não use Markdown;
- não use títulos iniciados por #;
- não use asteriscos, crases ou blocos de código para formatação;
- não use delimitadores ou comandos de LaTeX;
- não escreva comandos como frac, times, sqrt, leq ou geq;
- em fórmulas, prefira símbolos legíveis como Δ, √, ×, ÷, ≤, ≥, ² e ³;
- para frações simples, escreva 1/2, 3/4 etc.;
- use linhas curtas, números e o marcador • somente quando isso ajudar;
- nunca exponha caracteres de formatação que o estudante precise interpretar.

"""

if "FORMATAÇÃO PARA O APLICATIVO" not in text:
    anchor = "PRECISÃO\nAntes de responder, confira:"
    if anchor in text:
        text = text.replace(anchor, format_rules + anchor, 1)
    else:
        anchor = "FORMATO PREFERIDO\n"
        if anchor in text:
            text = text.replace(anchor, format_rules + anchor, 1)
        else:
            raise SystemExit(
                "ERRO: não encontrei um ponto seguro dentro de _tutor_instructions(). "
                "Nenhuma alteração foi salva."
            )

# 3) Sanitizador de saída.
cleaner = r'''

# === SAIDA LIMPA DO TUTOR V1 ===

def _clean_tutor_output(value: str) -> str:
    """
    Normaliza a resposta do tutor para exibição direta no Mentor.Edu.
    Remove marcas comuns de Markdown/LaTeX sem apagar o conteúdo pedagógico.
    """
    if value is None:
        return ""

    text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Blocos de código / Markdown.
    text = re.sub(r"```[A-Za-z0-9_-]*\s*", "", text)
    text = text.replace("```", "")
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)

    # Links Markdown: [texto](url) -> texto
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Negrito/itálico Markdown.
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_\n]+)__", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", text)

    # Marcadores de lista ficam visualmente limpos.
    text = re.sub(r"(?m)^\s*[-*+]\s+", "• ", text)

    # Delimitadores LaTeX.
    text = text.replace(r"\[", "").replace(r"\]", "")
    text = text.replace(r"\(", "").replace(r"\)", "")
    text = text.replace("$$", "").replace("$", "")

    # Frações simples. Faz algumas passagens para cobrir casos comuns.
    frac_pattern = re.compile(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}")
    for _ in range(4):
        new_text = frac_pattern.sub(
            lambda m: f"{m.group(1).strip()}/{m.group(2).strip()}",
            text,
        )
        if new_text == text:
            break
        text = new_text

    # Raiz quadrada simples.
    text = re.sub(
        r"\\sqrt\s*\{([^{}]+)\}",
        lambda m: f"√({m.group(1).strip()})",
        text,
    )

    replacements = {
        r"\times": "×",
        r"\cdot": "·",
        r"\div": "÷",
        r"\leq": "≤",
        r"\le": "≤",
        r"\geq": "≥",
        r"\ge": "≥",
        r"\neq": "≠",
        r"\approx": "≈",
        r"\pm": "±",
        r"\Delta": "Δ",
        r"\delta": "δ",
        r"\pi": "π",
        r"\theta": "θ",
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\omega": "ω",
        r"\mu": "μ",
        r"\infty": "∞",
        r"\degree": "°",
        r"\%": "%",
        r"\_": "_",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Comandos LaTeX que apenas envolvem texto.
    for _ in range(3):
        text = re.sub(
            r"\\(?:text|mathrm|mathbf|mathit|operatorname)\s*\{([^{}]*)\}",
            r"\1",
            text,
        )

    # Expoentes mais frequentes.
    text = re.sub(r"\^\s*\{?\s*2\s*\}?", "²", text)
    text = re.sub(r"\^\s*\{?\s*3\s*\}?", "³", text)

    # Subscritos simples: v_{0} -> v₀; s_0 -> s₀.
    sub_map = str.maketrans("0123456789+-=()", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")

    def subscript_repl(match):
        raw = match.group(1) or match.group(2) or ""
        return raw.translate(sub_map)

    text = re.sub(
        r"_\{([0-9+\-=()]+)\}|_([0-9])",
        subscript_repl,
        text,
    )

    # Ambientes LaTeX comuns.
    text = re.sub(r"\\begin\{[^}]+\}", "", text)
    text = re.sub(r"\\end\{[^}]+\}", "", text)

    # Quebras usadas em LaTeX.
    text = text.replace(r"\\", "\n")

    # Remove chaves soltas que restaram apenas de formatação.
    text = re.sub(r"\{([^{}\n]+)\}", r"\1", text)

    # Se sobrar um comando LaTeX desconhecido, mostra só o nome,
    # sem a barra que dá aparência de código.
    text = re.sub(r"\\([A-Za-z]+)", r"\1", text)

    # Limpeza final de espaços e linhas vazias excessivas.
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
'''

if "# === SAIDA LIMPA DO TUTOR V1 ===" not in text:
    anchor = "\ndef _run_student_tutor(\n"
    if anchor not in text:
        raise SystemExit(
            "ERRO: não encontrei def _run_student_tutor(). "
            "Nenhuma alteração foi salva."
        )
    text = text.replace(anchor, cleaner + anchor, 1)

# 4) Aplica a limpeza somente na resposta do tutor personalizado.
version_pos = text.find('"tutor_version":')
if version_pos == -1:
    raise SystemExit(
        "ERRO: não encontrei tutor_version no retorno do tutor. "
        "Nenhuma alteração foi salva."
    )

response_pos = text.find('"resposta": result["text"]', version_pos)
if response_pos != -1:
    old = '"resposta": result["text"]'
    new = '"resposta": _clean_tutor_output(result["text"])'
    text = text[:response_pos] + new + text[response_pos + len(old):]
elif '"resposta": _clean_tutor_output(result["text"])' not in text[version_pos:]:
    raise SystemExit(
        "ERRO: não encontrei a linha de resposta do tutor em formato conhecido. "
        "Nenhuma alteração foi salva."
    )

# 5) Atualiza versão do tutor para identificar o reparo.
text = re.sub(
    r'("tutor_version"\s*:\s*")[^"]+(" )'.replace('" )', '")'),
    r'\g<1>1.4.1-clean\2',
    text,
    count=1,
)

if text == original:
    print("Nenhuma alteração necessária: a saída limpa já parece estar aplicada.")
    sys.exit(0)

MENTOR.write_text(text, encoding="utf-8")

print()
print("==============================================")
print(" MENTOR.EDU - SAÍDA LIMPA APLICADA COM SUCESSO")
print("==============================================")
print(f"Arquivo alterado: {MENTOR}")
print(f"Backup: {backup}")
print()
print("Versão esperada do tutor: 1.4.1-clean")
print()
print("Agora reinicie o backend e teste perguntas com:")
print(" - frações")
print(" - fórmulas")
print(" - potência ao quadrado")
print(" - passo a passo")
print()
print("Exemplo de teste:")
print("Um corpo parte do repouso com aceleração de 3 m/s². Qual o deslocamento após 4 s?")
