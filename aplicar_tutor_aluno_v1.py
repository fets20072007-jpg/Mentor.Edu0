from pathlib import Path

ROOT = Path(".")
ROUTER = ROOT / "backend/app/router/ai/mentor.py"

if not ROUTER.exists():
    raise SystemExit(
        "Não encontrei backend/app/router/ai/mentor.py. "
        "Rode este script na raiz do Mentor.Edu."
    )

text = ROUTER.read_text(
    encoding="utf-8-sig",
    errors="ignore",
)

marker = "# === TUTOR ALUNO V1 ==="

if marker in text:
    print("Tutor Aluno V1 já está aplicado.")
    raise SystemExit(0)

if "from fastapi import Request" not in text:
    text = "from fastapi import Request\n" + text

if "from app.core.config import AI_TEST_TOKEN" not in text:
    anchor = "from app.core.permissions import ("
    if anchor not in text:
        raise SystemExit(
            "Não encontrei o bloco de imports esperado em mentor.py."
        )
    text = text.replace(
        anchor,
        "from app.core.config import AI_TEST_TOKEN\n\n" + anchor,
        1,
    )

block = '\n# === TUTOR ALUNO V1 ===\n\ndef _tutor_focus(metrics: dict) -> list[dict]:\n    subjects = metrics.get("desempenho_por_disciplina") or []\n\n    valid = [\n        item\n        for item in subjects\n        if item.get("media_percentual") is not None\n    ]\n\n    valid.sort(\n        key=lambda item: item["media_percentual"]\n    )\n\n    return valid[:3]\n\n\ndef _tutor_instructions() -> str:\n    return """\nVocê é o Tutor IA do Mentor.Edu.\n\nSeu objetivo é ajudar o estudante a APRENDER, e não apenas\nentregar respostas prontas.\n\nREGRAS PEDAGÓGICAS:\n- fale em português brasileiro;\n- explique de forma clara e progressiva;\n- adapte o nível ao contexto pedagógico fornecido;\n- priorize os pontos de maior dificuldade do aluno;\n- em Matemática/Física, mostre fórmulas, substituições e contas;\n- quando houver exercício, explique o raciocínio passo a passo;\n- se o aluno pedir somente a resposta, ainda forneça uma explicação curta;\n- use exemplos próximos da realidade escolar e, quando fizer sentido,\n  de cursos técnicos;\n- não invente notas, faltas, disciplinas ou informações do estudante;\n- não faça diagnóstico médico, psicológico ou clínico;\n- não compare o estudante com outros alunos;\n- não revele IDs ou dados internos do sistema;\n- quando os dados forem insuficientes, diga isso naturalmente;\n- seja encorajador sem exagero;\n- finalize, quando útil, com uma pequena pergunta ou exercício de checagem.\n\nO perfil calculado pelo Mentor.Edu é apenas um INDICADOR PEDAGÓGICO\ne deve orientar a adaptação da explicação.\n"""\n\n\ndef _run_student_tutor(\n    *,\n    mensagem: str,\n    metrics: dict,\n) -> dict:\n    profile = classify_profile(metrics)\n    focus = _tutor_focus(metrics)\n\n    context = {\n        "perfil_pedagogico": profile,\n        "media_geral_percentual": (\n            metrics.get("media_geral_percentual")\n        ),\n        "frequencia": metrics.get("frequencia"),\n        "foco_prioritario": focus,\n        "objetivo_declarado": (\n            metrics.get("objetivo_declarado")\n        ),\n        "dificuldades_declaradas": (\n            metrics.get("dificuldades_declaradas")\n        ),\n        "horas_estudo_dia": (\n            metrics.get("horas_estudo_dia")\n        ),\n    }\n\n    result = ask_text(\n        instructions=_tutor_instructions(),\n        user_input=(\n            "CONTEXTO PEDAGÓGICO DO ESTUDANTE:\\n"\n            + json.dumps(\n                context,\n                ensure_ascii=False,\n            )\n            + "\\n\\nMENSAGEM DO ESTUDANTE:\\n"\n            + mensagem\n        ),\n        smart=False,\n    )\n\n    return {\n        "resposta": result["text"],\n        "perfil": profile,\n        "foco_prioritario": focus,\n        "provider": result.get("provider"),\n        "model": result["model"],\n        "response_id": result["response_id"],\n    }\n\n\n@router.post("/student/tutor")\ndef student_tutor_v1(\n    payload: AIChatRequest,\n    current_user: User = Depends(\n        require_student\n    ),\n    db: Session = Depends(get_db),\n):\n    """\n    Tutor IA personalizado do aluno.\n    Usa somente contexto pedagógico do usuário autenticado.\n    """\n    metrics = build_student_metrics(\n        db,\n        current_user,\n    )\n\n    try:\n        return _run_student_tutor(\n            mensagem=payload.mensagem,\n            metrics=metrics,\n        )\n    except Exception as error:\n        _raise_ai_error(error)\n\n\n@router.post("/test-student-tutor")\ndef test_student_tutor_v1(\n    request: Request,\n):\n    """\n    Teste protegido com dados FICTÍCIOS.\n    Não acessa banco nem dados reais de alunos.\n    """\n    if not AI_TEST_TOKEN:\n        raise HTTPException(\n            status_code=503,\n            detail="AI_TEST_TOKEN não configurado.",\n        )\n\n    supplied = request.headers.get(\n        "X-Mentor-AI-Test"\n    )\n\n    if supplied != AI_TEST_TOKEN:\n        raise HTTPException(\n            status_code=403,\n            detail="Token de teste inválido.",\n        )\n\n    fake_metrics = {\n        "media_geral_percentual": 62.0,\n        "desempenho_por_disciplina": [\n            {\n                "disciplina": "Física",\n                "media_percentual": 48.0,\n                "avaliacoes": 3,\n            },\n            {\n                "disciplina": "Matemática",\n                "media_percentual": 58.0,\n                "avaliacoes": 4,\n            },\n            {\n                "disciplina": "Português",\n                "media_percentual": 80.0,\n                "avaliacoes": 3,\n            },\n        ],\n        "frequencia": {\n            "registros": 40,\n            "presentes": 35,\n            "faltas": 5,\n            "atrasos": 0,\n            "taxa_presenca": 87.5,\n        },\n        "objetivo_declarado": (\n            "Melhorar o desempenho em Física."\n        ),\n        "dificuldades_declaradas": (\n            "Cinemática e interpretação de fórmulas."\n        ),\n        "horas_estudo_dia": 1.5,\n        "respostas_avaliadas": {\n            "quantidade": 10,\n            "media_percentual": 60.0,\n        },\n    }\n\n    try:\n        result = _run_student_tutor(\n            mensagem=(\n                "Estou estudando velocidade média e não entendi "\n                "quando devo usar ΔS/Δt. Pode me explicar?"\n            ),\n            metrics=fake_metrics,\n        )\n    except Exception as error:\n        _raise_ai_error(error)\n\n    return {\n        "status": "ok",\n        "modo": "demonstracao",\n        **result,\n    }\n'
text = text.rstrip() + "\n\n" + block.strip() + "\n"

compile(
    text,
    str(ROUTER),
    "exec",
)

backup = ROUTER.with_name(
    "mentor.py.backup_tutor_v1"
)

if not backup.exists():
    backup.write_text(
        ROUTER.read_text(
            encoding="utf-8-sig",
            errors="ignore",
        ),
        encoding="utf-8",
    )

ROUTER.write_text(
    text,
    encoding="utf-8",
)

print("")
print("TUTOR IA DO ALUNO V1 APLICADO COM SUCESSO.")
print("")
print("Rotas adicionadas:")
print("POST /mentor-ai/student/tutor")
print("POST /mentor-ai/test-student-tutor")
print("")
print("Nenhuma tabela do banco foi alterada.")
