from pathlib import Path

ROOT = Path(".")
ROUTER = ROOT / "backend/app/router/ai/mentor.py"

if not ROUTER.exists():
    raise SystemExit(
        "Não encontrei backend/app/router/ai/mentor.py. "
        "Rode este script na raiz do Mentor.Edu."
    )

text = ROUTER.read_text(encoding="utf-8-sig", errors="strict")

if '"tutor_version": "1.3"' not in text:
    raise SystemExit(
        "Tutor V1.3 não encontrado. Aplique a V1.3 antes desta correção."
    )

if '"tutor_version": "1.3.1"' in text:
    print("Tutor Aluno V1.3.1 já está aplicado.")
    raise SystemExit(0)

start = text.find("def _run_student_tutor(")
end = text.find("\n\n@router.post(", start)

if start == -1 or end == -1:
    raise SystemExit("Não encontrei a função _run_student_tutor.")

segment = text[start:end]

# Garante decisão smart dentro da função do tutor.
if "use_smart_model = _tutor_requires_smart_model(mensagem)" not in segment:
    anchor = "    result = ask_text(\n"
    if anchor not in segment:
        raise SystemExit("Não encontrei a chamada ask_text no Tutor.")
    segment = segment.replace(
        anchor,
        "    use_smart_model = _tutor_requires_smart_model(mensagem)\n\n"
        + anchor,
        1,
    )

# Garante que a chamada use a decisão adaptativa.
if "smart=use_smart_model" not in segment:
    if "smart=False" in segment:
        segment = segment.replace(
            "smart=False",
            "smart=use_smart_model",
            1,
        )
    elif "smart=True" in segment:
        segment = segment.replace(
            "smart=True",
            "smart=use_smart_model",
            1,
        )
    else:
        # Insere antes do fechamento da chamada ask_text se não houver argumento smart.
        marker = "        ),\n"
        pos = segment.find(marker, segment.find("result = ask_text("))
        if pos == -1:
            raise SystemExit("Não consegui localizar o fechamento de ask_text.")
        insert_at = pos + len(marker)
        segment = segment[:insert_at] + "        smart=use_smart_model,\n" + segment[insert_at:]

# Garante diagnóstico no retorno.
if '"model_route": "smart" if use_smart_model else "fast"' not in segment:
    needle = '        "provider": result.get("provider"),\n'
    if needle not in segment:
        raise SystemExit("Não encontrei o retorno do provider no Tutor.")
    segment = segment.replace(
        needle,
        needle
        + '        "model_route": "smart" if use_smart_model else "fast",\n',
        1,
    )

# Adiciona booleano para diagnóstico explícito.
if '"smart_requested": use_smart_model' not in segment:
    needle = '        "model_route": "smart" if use_smart_model else "fast",\n'
    segment = segment.replace(
        needle,
        needle + '        "smart_requested": use_smart_model,\n',
        1,
    )

text = text[:start] + segment + text[end:]

# Atualiza versão.
text = text.replace(
    '"tutor_version": "1.3"',
    '"tutor_version": "1.3.1"',
    1,
)

# Troca a mensagem do teste por uma questão que força cálculo + múltipla escolha.
old_test = (
    '            mensagem=(\n'
    '                "Estou estudando velocidade média e não entendi "\n'
    '                "quando devo usar ΔS/Δt. Pode me explicar?"\n'
    '            ),\n'
)

new_test = (
    '            mensagem=(\n'
    '                "Um objeto se move 10 m para a direita e depois 3 m para "\n'
    '                "a esquerda em 5 s. Qual é a velocidade média? "\n'
    '                "Alternativas: (A) 1 m/s, (B) 13 m/s, (C) 3 m/s. "\n'
    '                "Mostre o cálculo e diga se alguma alternativa corresponde "\n'
    '                "exatamente ao resultado."\n'
    '            ),\n'
)

if old_test in text:
    text = text.replace(old_test, new_test, 1)
else:
    # Se a formatação mudou, tenta localizar apenas a mensagem antiga.
    old_phrase = (
        '"Estou estudando velocidade média e não entendi "\n'
        '                "quando devo usar ΔS/Δt. Pode me explicar?"'
    )
    new_phrase = (
        '"Um objeto se move 10 m para a direita e depois 3 m para "\n'
        '                "a esquerda em 5 s. Qual é a velocidade média? "\n'
        '                "Alternativas: (A) 1 m/s, (B) 13 m/s, (C) 3 m/s. "\n'
        '                "Mostre o cálculo e diga se alguma alternativa corresponde "\n'
        '                "exatamente ao resultado."'
    )
    if old_phrase not in text:
        raise SystemExit(
            "Não encontrei a mensagem de teste antiga para atualizar."
        )
    text = text.replace(old_phrase, new_phrase, 1)

compile(text, str(ROUTER), "exec")

backup = ROUTER.with_name("mentor.py.backup_tutor_v1_3_1")
if not backup.exists():
    backup.write_text(
        ROUTER.read_text(encoding="utf-8-sig", errors="strict"),
        encoding="utf-8",
    )

ROUTER.write_text(text, encoding="utf-8")

print("")
print("TUTOR IA DO ALUNO V1.3.1 APLICADO COM SUCESSO.")
print("")
print("Ajustes:")
print("- força o roteamento smart dentro do Tutor")
print("- expõe model_route no retorno")
print("- expõe smart_requested no retorno")
print("- teste agora usa cálculo + alternativas inconsistentes")
print("- tutor_version=1.3.1")
print("")
print("Banco, frontend e cronograma: nenhuma alteração.")
