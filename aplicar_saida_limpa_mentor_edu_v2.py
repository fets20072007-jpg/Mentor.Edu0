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

backup = MENTOR.with_name("mentor.py.backup_saida_limpa_v2")
if not backup.exists():
    shutil.copy2(MENTOR, backup)

# 1) Import re
if not re.search(r"(?m)^import re\s*$", text):
    m = re.search(r"(?m)^import json\s*$", text)
    if m:
        text = text[:m.end()] + "\nimport re" + text[m.end():]
    else:
        text = "import re\n" + text

# 2) Regras de formatação dentro de _tutor_instructions()
if "FORMATAÇÃO PARA O APLICATIVO" not in text:
    fn = re.search(
        r"(?m)^def\s+_tutor_instructions\s*\([^)]*\)\s*(?:->\s*str\s*)?:\s*$",
        text,
    )
    if not fn:
        raise SystemExit(
            "ERRO: não encontrei _tutor_instructions(). Nenhuma alteração foi salva."
        )

    next_fn = re.search(r"(?m)^def\s+", text[fn.end():])
    fn_end = fn.end() + next_fn.start() if next_fn else len(text)
    block = text[fn.start():fn_end]

    q3a = '"' * 3
    q3b = "'" * 3

    ret_pos = block.find("return")
    if ret_pos == -1:
        raise SystemExit(
            "ERRO: encontrei _tutor_instructions(), mas não encontrei return."
        )

    qpos_a = block.find(q3a, ret_pos)
    qpos_b = block.find(q3b, ret_pos)
    candidates = [p for p in (qpos_a, qpos_b) if p != -1]

    if not candidates:
        raise SystemExit(
            "ERRO: não encontrei o texto triplo dentro de _tutor_instructions()."
        )

    open_pos = min(candidates)
    quote = q3a if open_pos == qpos_a else q3b
    close_pos = block.find(quote, open_pos + 3)

    if close_pos == -1:
        raise SystemExit(
            "ERRO: não encontrei o fechamento do prompt do tutor."
        )

    insert_at = fn.start() + close_pos

    rules = (
        "\nFORMATAÇÃO PARA O APLICATIVO\n"
        "- a resposta será exibida diretamente no chat do Mentor.Edu;\n"
        "- escreva em texto limpo, natural e fácil de ler;\n"
        "- não use Markdown;\n"
        "- não use títulos iniciados por #;\n"
        "- não use asteriscos, crases ou blocos de código como formatação;\n"
        "- não use delimitadores ou comandos LaTeX visíveis;\n"
        "- não escreva comandos como frac, times, sqrt, leq ou geq;\n"
        "- em fórmulas, prefira símbolos legíveis como Δ, √, ×, ÷, ≤, ≥, ² e ³;\n"
        "- em frações simples, prefira 1/2, 3/4 e formatos equivalentes;\n"
        "- use listas somente quando ajudarem na leitura;\n"
        "- nunca exponha caracteres de formatação que o estudante precise interpretar.\n"
    )

    text = text[:insert_at] + rules + text[insert_at:]

# 3) Função de limpeza
if "# === SAIDA LIMPA DO TUTOR V2 ===" not in text:
    cleaner = r