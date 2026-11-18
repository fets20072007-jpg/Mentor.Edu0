from pathlib import Path
import re
import shutil
import sys

ROOT = Path.cwd()
MENTOR = ROOT / "backend" / "app" / "router" / "ai" / "mentor.py"

if not MENTOR.exists():
    raise SystemExit(
        "ERRO: não encontrei backend/app/router/ai/mentor.py.\n"
        "Abra o terminal na pasta raiz do Mentor.Edu e rode novamente."
    )

text = MENTOR.read_text(encoding="utf-8-sig")
original = text

backup = MENTOR.with_name("mentor.py.backup_saida_limpa_v3")
if not backup.exists():
    shutil.copy2(MENTOR, backup)

# 1) Garante import re.
if not re.search(r"(?m)^import re\s*$", text):
    m = re.search(r"(?m)^import json\s*$", text)
    if m:
        text = text[:m.end()] + "\nimport re" + text[m.end():]
    else:
        text = "import re\n" + text

CLEANER_SOURCE = '\n# === SAIDA LIMPA DO TUTOR V3 ===\n\n_TUTOR_CLEAN_OUTPUT_RULES = """\nFORMATAÇÃO DE SAÍDA PARA O APLICATIVO\nA resposta será exibida diretamente no chat do Mentor.Edu.\nEscreva em texto limpo, natural e fácil de ler.\nNão use Markdown, títulos com #, asteriscos, crases ou blocos de código.\nNão use delimitadores LaTeX visíveis como \\[ \\] \\( \\) ou $$.\nNão escreva comandos LaTeX visíveis como \\frac, \\times, \\sqrt, \\leq ou \\geq.\nEm fórmulas, prefira símbolos legíveis como Δ, √, ×, ÷, ≤, ≥, ² e ³.\nPara frações simples, prefira 1/2, 3/4 e formatos equivalentes.\nNunca exponha caracteres de formatação que o estudante precise interpretar.\n"""\n\n\ndef _clean_tutor_output(value: str) -> str:\n    """Normaliza a resposta da IA para exibição direta no Mentor.Edu."""\n    if value is None:\n        return ""\n\n    text = str(value)\n    text = text.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n\n    # Markdown comum.\n    text = re.sub(r"```[A-Za-z0-9_-]*\\s*", "", text)\n    text = text.replace("```", "")\n    text = re.sub(r"(?m)^\\s{0,3}#{1,6}\\s*", "", text)\n    text = re.sub(r"\\[([^\\]]+)\\]\\([^)]+\\)", r"\\1", text)\n    text = re.sub(r"\\*\\*([^*\\n]+)\\*\\*", r"\\1", text)\n    text = re.sub(r"__([^_\\n]+)__", r"\\1", text)\n    text = re.sub(r"(?<!\\*)\\*([^*\\n]+)\\*(?!\\*)", r"\\1", text)\n    text = re.sub(r"(?m)^\\s*[-*+]\\s+", "• ", text)\n\n    # Delimitadores matemáticos.\n    text = text.replace(r"\\[", "").replace(r"\\]", "")\n    text = text.replace(r"\\(", "").replace(r"\\)", "")\n    text = text.replace("$$", "").replace("$", "")\n\n    # Frações LaTeX simples.\n    frac = re.compile(r"\\\\frac\\s*\\{([^{}]+)\\}\\s*\\{([^{}]+)\\}")\n    for _ in range(5):\n        new_text = frac.sub(\n            lambda m: f"{m.group(1).strip()}/{m.group(2).strip()}",\n            text,\n        )\n        if new_text == text:\n            break\n        text = new_text\n\n    # Raiz quadrada simples.\n    text = re.sub(\n        r"\\\\sqrt\\s*\\{([^{}]+)\\}",\n        lambda m: f"√({m.group(1).strip()})",\n        text,\n    )\n\n    replacements = {\n        r"\\times": "×",\n        r"\\cdot": "·",\n        r"\\div": "÷",\n        r"\\leq": "≤",\n        r"\\le": "≤",\n        r"\\geq": "≥",\n        r"\\ge": "≥",\n        r"\\neq": "≠",\n        r"\\approx": "≈",\n        r"\\pm": "±",\n        r"\\Delta": "Δ",\n        r"\\delta": "δ",\n        r"\\pi": "π",\n        r"\\theta": "θ",\n        r"\\alpha": "α",\n        r"\\beta": "β",\n        r"\\gamma": "γ",\n        r"\\omega": "ω",\n        r"\\mu": "μ",\n        r"\\infty": "∞",\n        r"\\%": "%",\n        r"\\_": "_",\n    }\n    for old, new in replacements.items():\n        text = text.replace(old, new)\n\n    # Comandos de estilo que apenas envolvem texto.\n    for _ in range(4):\n        text = re.sub(\n            r"\\\\(?:text|mathrm|mathbf|mathit|operatorname)\\s*\\{([^{}]*)\\}",\n            r"\\1",\n            text,\n        )\n\n    # Expoentes comuns.\n    text = re.sub(r"\\^\\s*\\{?\\s*2\\s*\\}?", "²", text)\n    text = re.sub(r"\\^\\s*\\{?\\s*3\\s*\\}?", "³", text)\n\n    # Subscritos numéricos comuns.\n    sub_map = str.maketrans(\n        "0123456789+-=()",\n        "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎",\n    )\n\n    def _sub_repl(match):\n        raw = match.group(1) or match.group(2) or ""\n        return raw.translate(sub_map)\n\n    text = re.sub(\n        r"_\\{([0-9+\\-=()]+)\\}|_([0-9])",\n        _sub_repl,\n        text,\n    )\n\n    # Ambientes e quebras LaTeX.\n    text = re.sub(r"\\\\begin\\{[^}]+\\}", "", text)\n    text = re.sub(r"\\\\end\\{[^}]+\\}", "", text)\n    text = text.replace(r"\\\\", "\\n")\n\n    # Chaves residuais de formatação.\n    text = re.sub(r"\\{([^{}\\n]+)\\}", r"\\1", text)\n\n    # Comando desconhecido: remove só a barra, preservando a palavra.\n    text = re.sub(r"\\\\([A-Za-z]+)", r"\\1", text)\n\n    # Limpeza de espaços/linhas.\n    text = re.sub(r"[ \\t]+\\n", "\\n", text)\n    text = re.sub(r"\\n[ \\t]+", "\\n", text)\n    text = re.sub(r"[ \\t]{2,}", " ", text)\n    text = re.sub(r"\\n{3,}", "\\n\\n", text)\n\n    return text.strip()\n'

# 2) Insere regras + sanitizador antes de _run_student_tutor.
if "# === SAIDA LIMPA DO TUTOR V3 ===" not in text:
    run = re.search(r"(?m)^def\s+_run_student_tutor\s*\(", text)
    if not run:
        raise SystemExit(
            "ERRO: não encontrei _run_student_tutor(). Nenhuma alteração foi salva."
        )
    text = text[:run.start()] + CLEANER_SOURCE + "\n" + text[run.start():]

# 3) Localiza somente o bloco _run_student_tutor.
run = re.search(r"(?m)^def\s+_run_student_tutor\s*\(", text)
if not run:
    raise SystemExit("ERRO: não encontrei _run_student_tutor().")

next_fn = re.search(r"(?m)^def\s+", text[run.end():])
run_end = run.end() + next_fn.start() if next_fn else len(text)
block = text[run.start():run_end]

# 4) Acrescenta as regras de saída limpa às instruções existentes.
if "_TUTOR_CLEAN_OUTPUT_RULES" not in block:
    new_block, count = re.subn(
        r"instructions\s*=\s*_tutor_instructions\(\)\s*,",
        "instructions=_tutor_instructions() + _TUTOR_CLEAN_OUTPUT_RULES,",
        block,
        count=1,
    )
    if count == 0:
        raise SystemExit(
            "ERRO: encontrei _run_student_tutor(), mas não encontrei "
            "instructions=_tutor_instructions(). Nenhuma alteração foi salva."
        )
    block = new_block

# 5) Sanitiza somente a resposta devolvida pelo tutor.
if '_clean_tutor_output(result["text"])' not in block and "_clean_tutor_output(result['text'])" not in block:
    new_block, count = re.subn(
        r'("resposta"\s*:\s*)result\["text"\]',
        r'\1_clean_tutor_output(result["text"])',
        block,
        count=1,
    )
    if count == 0:
        new_block, count = re.subn(
            r"('resposta'\s*:\s*)result\['text'\]",
            r"\1_clean_tutor_output(result['text'])",
            block,
            count=1,
        )
    if count == 0:
        raise SystemExit(
            "ERRO: não encontrei o retorno da resposta do tutor. "
            "Nenhuma alteração foi salva."
        )
    block = new_block

# 6) Marca a versão.
block = re.sub(
    r'("tutor_version"\s*:\s*")[^"]+(")',
    r'\g<1>1.4.3-clean\2',
    block,
    count=1,
)

text = text[:run.start()] + block + text[run_end:]

# 7) Valida sintaxe do mentor.py antes de gravar.
try:
    compile(text, str(MENTOR), "exec")
except SyntaxError as exc:
    raise SystemExit(
        "ERRO: o reparo geraria um erro de sintaxe. NADA foi salvo.\n"
        f"Linha {exc.lineno}: {exc.msg}"
    )

if text == original:
    print("Nenhuma alteração necessária: o reparo V3 já está aplicado.")
    sys.exit(0)

MENTOR.write_text(text, encoding="utf-8")

print()
print("=================================================")
print(" MENTOR.EDU - SAÍDA LIMPA V3 APLICADA COM SUCESSO")
print("=================================================")
print(f"Arquivo: {MENTOR}")
print(f"Backup:  {backup}")
print("Tutor:   1.4.3-clean")
print("Sintaxe: OK")
print()
print("Agora reinicie o backend e teste o Mentor Edu.")
print()
print("Teste sugerido:")
print("Um corpo parte do repouso com aceleração constante de 3 m/s².")
print("Qual o deslocamento após 4 segundos? Explique passo a passo.")
