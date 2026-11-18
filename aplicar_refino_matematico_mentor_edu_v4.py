from pathlib import Path
import re
import shutil
import sys

ROOT = Path.cwd()
MENTOR = ROOT / "backend" / "app" / "router" / "ai" / "mentor.py"

if not MENTOR.exists():
    raise SystemExit(
        "ERRO: não encontrei backend/app/router/ai/mentor.py.\n"
        "Abra o terminal na raiz do Mentor.Edu e rode novamente."
    )

text = MENTOR.read_text(encoding="utf-8-sig")
original = text

backup = MENTOR.with_name("mentor.py.backup_saida_limpa_v4")
if not backup.exists():
    shutil.copy2(MENTOR, backup)

if not re.search(r"(?m)^import re\s*$", text):
    m = re.search(r"(?m)^import json\s*$", text)
    if m:
        text = text[:m.end()] + "\nimport re" + text[m.end():]
    else:
        text = "import re\n" + text

RULES_V4 = '_TUTOR_CLEAN_OUTPUT_RULES = r"""\nFORMATAÇÃO DE SAÍDA PARA O APLICATIVO — REGRA OBRIGATÓRIA\nA resposta será exibida diretamente no chat do Mentor.Edu.\nEscreva em texto limpo, natural e fácil de ler.\n\nNÃO USE:\n- Markdown;\n- títulos com #;\n- asteriscos ou crases como formatação;\n- blocos de código;\n- delimitadores LaTeX como \\[ \\] \\( \\) ou $$;\n- comandos LaTeX como \\frac, \\dfrac, \\tfrac, \\times, \\sqrt, \\leq ou \\geq.\n\nEM MATEMÁTICA E FÍSICA:\n- escreva fórmulas diretamente com símbolos legíveis;\n- use × para multiplicação e ÷ quando necessário;\n- use ² e ³ para potências simples;\n- use Δ, √, ≤, ≥ e outros símbolos já prontos;\n- sempre deixe espaço entre número e unidade: 3 m/s², 4 s, 24 m.\n\nExemplo correto:\ns = s₀ + v₀ × t + (a × t²) / 2\n\nExemplo incorreto:\ns = s_0 + v_0 t + \\dfrac{a t^2}{2}\n\nSubstituição correta:\ns = 0 + 0 × 4 + (3 × 4²) / 2\n\nNunca exponha caracteres de formatação que o estudante precise interpretar.\n"""\n'
CLEANER_V4 = '\ndef _clean_tutor_output(value: str) -> str:\n    """Normaliza a saída da IA para leitura direta no Mentor.Edu."""\n    if value is None:\n        return ""\n\n    text = str(value)\n    text = text.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n\n    # Markdown comum.\n    text = re.sub(r"```[A-Za-z0-9_-]*\\s*", "", text)\n    text = text.replace("```", "")\n    text = re.sub(r"(?m)^\\s{0,3}#{1,6}\\s*", "", text)\n    text = re.sub(r"\\[([^\\]]+)\\]\\([^)]+\\)", r"\\1", text)\n    text = re.sub(r"\\*\\*([^*\\n]+)\\*\\*", r"\\1", text)\n    text = re.sub(r"__([^_\\n]+)__", r"\\1", text)\n    text = re.sub(r"(?<!\\*)\\*([^*\\n]+)\\*(?!\\*)", r"\\1", text)\n    text = re.sub(r"(?m)^\\s*[-*+]\\s+", "• ", text)\n\n    # Delimitadores e comandos de espaçamento LaTeX.\n    text = text.replace(r"\\[", "").replace(r"\\]", "")\n    text = text.replace(r"\\(", "").replace(r"\\)", "")\n    text = text.replace("$$", "").replace("$", "")\n    text = text.replace(r"\\,", " ")\n    text = text.replace(r"\\;", " ")\n    text = text.replace(r"\\:", " ")\n    text = text.replace(r"\\!", "")\n    text = text.replace("\\\\ ", " ")\n\n    # Remove apenas comandos de dimensionamento.\n    text = text.replace(r"\\left", "").replace(r"\\right", "")\n\n    # Frações: \\frac, \\dfrac e \\tfrac.\n    frac = re.compile(\n        r"\\\\(?:dfrac|tfrac|frac)\\s*\\{([^{}]+)\\}\\s*\\{([^{}]+)\\}"\n    )\n\n    def _fraction_repl(match):\n        numerator = match.group(1).strip()\n        denominator = match.group(2).strip()\n\n        simple_num = bool(re.fullmatch(r"[A-Za-z0-9À-ÿ_.+-]+", numerator))\n        simple_den = bool(re.fullmatch(r"[A-Za-z0-9À-ÿ_.+-]+", denominator))\n\n        if simple_num and simple_den:\n            return f"{numerator}/{denominator}"\n\n        if simple_den:\n            return f"({numerator}) / {denominator}"\n\n        return f"({numerator}) / ({denominator})"\n\n    for _ in range(6):\n        new_text = frac.sub(_fraction_repl, text)\n        if new_text == text:\n            break\n        text = new_text\n\n    # Raiz quadrada simples.\n    text = re.sub(\n        r"\\\\sqrt\\s*\\{([^{}]+)\\}",\n        lambda m: f"√({m.group(1).strip()})",\n        text,\n    )\n\n    replacements = {\n        r"\\times": "×",\n        r"\\cdot": "·",\n        r"\\div": "÷",\n        r"\\leq": "≤",\n        r"\\le": "≤",\n        r"\\geq": "≥",\n        r"\\ge": "≥",\n        r"\\neq": "≠",\n        r"\\approx": "≈",\n        r"\\pm": "±",\n        r"\\Delta": "Δ",\n        r"\\delta": "δ",\n        r"\\pi": "π",\n        r"\\theta": "θ",\n        r"\\alpha": "α",\n        r"\\beta": "β",\n        r"\\gamma": "γ",\n        r"\\omega": "ω",\n        r"\\mu": "μ",\n        r"\\infty": "∞",\n        r"\\%": "%",\n        r"\\_": "_",\n    }\n    for old, new in replacements.items():\n        text = text.replace(old, new)\n\n    # Comandos que só envolvem texto.\n    for _ in range(4):\n        text = re.sub(\n            r"\\\\(?:text|mathrm|mathbf|mathit|operatorname)\\s*\\{([^{}]*)\\}",\n            r"\\1",\n            text,\n        )\n\n    # Expoentes simples.\n    text = re.sub(r"\\^\\s*\\{?\\s*2\\s*\\}?", "²", text)\n    text = re.sub(r"\\^\\s*\\{?\\s*3\\s*\\}?", "³", text)\n\n    # Subscritos numéricos.\n    sub_map = str.maketrans(\n        "0123456789+-=()",\n        "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎",\n    )\n\n    def _sub_repl(match):\n        raw = match.group(1) or match.group(2) or ""\n        return raw.translate(sub_map)\n\n    text = re.sub(\n        r"_\\{([0-9+\\-=()]+)\\}|_([0-9])",\n        _sub_repl,\n        text,\n    )\n\n    # Ambientes LaTeX.\n    text = re.sub(r"\\\\begin\\{[^}]+\\}", "", text)\n    text = re.sub(r"\\\\end\\{[^}]+\\}", "", text)\n    text = text.replace(r"\\\\", "\\n")\n\n    # Chaves residuais de formatação.\n    text = re.sub(r"\\{([^{}\\n]+)\\}", r"\\1", text)\n\n    # Se sobrar algum comando desconhecido, remove só a barra.\n    text = re.sub(r"\\\\([A-Za-z]+)", r"\\1", text)\n\n    # Corrige alguns casos seguros de unidade sem espaço.\n    # Ex.: 3m/s² -> 3 m/s²\n    text = re.sub(\n        r"(?<![A-Za-z0-9_])(\\d+(?:[.,]\\d+)?)(m/s(?:²|³)?)\\b",\n        r"\\1 \\2",\n        text,\n    )\n\n    # Em final de frase, corrige medidas comuns como 24m. -> 24 m.\n    text = re.sub(\n        r"(\\d+(?:[.,]\\d+)?)(m|s|kg|cm|mm|km)(?=[.,;:!?)]|$)",\n        r"\\1 \\2",\n        text,\n    )\n\n    # Limpeza final.\n    text = re.sub(r"[ \\t]+\\n", "\\n", text)\n    text = re.sub(r"\\n[ \\t]+", "\\n", text)\n    text = re.sub(r"[ \\t]{2,}", " ", text)\n    text = re.sub(r"\\n{3,}", "\\n\\n", text)\n    text = re.sub(r"\\s+([.,;:!?])", r"\\1", text)\n\n    return text.strip()\n'

# Atualiza o bloco de regras de saída.
rules_start = text.find("_TUTOR_CLEAN_OUTPUT_RULES =")
if rules_start == -1:
    run = re.search(r"(?m)^def\s+_run_student_tutor\s*\(", text)
    if not run:
        raise SystemExit("ERRO: não encontrei _run_student_tutor().")
    text = text[:run.start()] + RULES_V4 + "\n" + text[run.start():]
else:
    first_quote = text.find('"""', rules_start)
    if first_quote == -1:
        raise SystemExit("ERRO: bloco _TUTOR_CLEAN_OUTPUT_RULES inválido.")
    close_quote = text.find('"""', first_quote + 3)
    if close_quote == -1:
        raise SystemExit("ERRO: fechamento das regras não encontrado.")
    rules_end = close_quote + 3
    text = text[:rules_start] + RULES_V4.rstrip() + text[rules_end:]

# Substitui a função de limpeza inteira pela V4.
clean_start = re.search(r"(?m)^def\s+_clean_tutor_output\s*\(", text)
run = re.search(r"(?m)^def\s+_run_student_tutor\s*\(", text)

if not run:
    raise SystemExit("ERRO: não encontrei _run_student_tutor().")

if clean_start:
    text = text[:clean_start.start()] + CLEANER_V4.strip() + "\n\n" + text[run.start():]
else:
    text = text[:run.start()] + CLEANER_V4.strip() + "\n\n" + text[run.start():]

# Garante que as regras e a limpeza estejam ligadas ao tutor.
run = re.search(r"(?m)^def\s+_run_student_tutor\s*\(", text)
next_fn = re.search(r"(?m)^def\s+", text[run.end():])
run_end = run.end() + next_fn.start() if next_fn else len(text)
block = text[run.start():run_end]

if "_TUTOR_CLEAN_OUTPUT_RULES" not in block:
    block, count = re.subn(
        r"instructions\s*=\s*_tutor_instructions\(\)\s*,",
        "instructions=_tutor_instructions() + _TUTOR_CLEAN_OUTPUT_RULES,",
        block,
        count=1,
    )
    if count == 0:
        raise SystemExit("ERRO: não consegui conectar as regras ao tutor.")

if '_clean_tutor_output(result["text"])' not in block and "_clean_tutor_output(result['text'])" not in block:
    block, count = re.subn(
        r'("resposta"\s*:\s*)result\["text"\]',
        r'\1_clean_tutor_output(result["text"])',
        block,
        count=1,
    )
    if count == 0:
        block, count = re.subn(
            r"('resposta'\s*:\s*)result\['text'\]",
            r"\1_clean_tutor_output(result['text'])",
            block,
            count=1,
        )
    if count == 0:
        raise SystemExit("ERRO: não consegui conectar o filtro à resposta.")

block = re.sub(
    r'("tutor_version"\s*:\s*")[^"]+(")',
    r'\g<1>1.4.4-clean\2',
    block,
    count=1,
)

text = text[:run.start()] + block + text[run_end:]

try:
    compile(text, str(MENTOR), "exec")
except SyntaxError as exc:
    raise SystemExit(
        "ERRO: o reparo geraria erro de sintaxe. NADA foi salvo.\n"
        f"Linha {exc.lineno}: {exc.msg}"
    )

if text == original:
    print("Nenhuma alteração necessária: o V4 já está aplicado.")
    sys.exit(0)

MENTOR.write_text(text, encoding="utf-8")

print()
print("====================================================")
print(" MENTOR.EDU - REFINO MATEMÁTICO V4 APLICADO")
print("====================================================")
print(f"Arquivo: {MENTOR}")
print(f"Backup:  {backup}")
print("Tutor:   1.4.4-clean")
print("Sintaxe: OK")
print()
print("Corrigido:")
print("- \\dfrac / \\tfrac / \\frac")
print("- barras de espaçamento como \\ ")
print("- exemplos com unidades: 3 m/s² e 24 m")
print("- instrução mais forte para não gerar LaTeX visível")
print()
print("Reinicie o backend e repita o mesmo teste.")
