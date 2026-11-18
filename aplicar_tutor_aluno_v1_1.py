from pathlib import Path

ROOT = Path(".")
ROUTER = ROOT / "backend/app/router/ai/mentor.py"

if not ROUTER.exists():
    raise SystemExit("Não encontrei backend/app/router/ai/mentor.py. Rode este script na raiz do Mentor.Edu.")

text = ROUTER.read_text(encoding="utf-8-sig", errors="strict")

if "# === TUTOR ALUNO V1 ===" not in text:
    raise SystemExit("Tutor Aluno V1 não encontrado. Aplique a versão V1 antes desta correção.")

if "TUTOR_PEDAGOGICO_V1_1" in text:
    print("Tutor Aluno V1.1 já está aplicado.")
    raise SystemExit(0)

start = text.find("def _tutor_instructions() -> str:")
end = text.find("\ndef _run_student_tutor(", start)

if start == -1 or end == -1:
    raise SystemExit("Não encontrei as funções do Tutor V1 no formato esperado.")

NEW_INSTRUCTIONS = 'def _tutor_instructions() -> str:\n    return """\nVocê é o Tutor IA do Mentor.Edu.\n\nMISSÃO\nAjude o estudante a compreender o conteúdo. Não seja apenas um resolvedor\nde exercícios e não entregue explicações maiores do que o necessário.\n\nESTILO DA RESPOSTA\n- responda em português brasileiro;\n- seja didático, direto e progressivo;\n- por padrão, use no máximo 4 blocos curtos;\n- evite tabelas e separadores longos quando não forem necessários;\n- em Matemática e Física, mostre fórmula, substituição e cálculo passo a passo;\n- explique o significado dos símbolos antes de usá-los quando houver dúvida;\n- use exemplos escolares simples;\n- não introduza cálculo, derivadas, integrais ou conteúdo mais avançado\n  se a pergunta puder ser resolvida no nível atual do estudante;\n- só aprofunde quando o aluno pedir.\n\nPRECISÃO\nAntes de responder, confira mentalmente:\n1. qual grandeza está sendo pedida;\n2. qual definição física/matemática corresponde a ela;\n3. se as unidades são coerentes;\n4. se a fórmula usada responde exatamente à pergunta.\n\nREGRAS IMPORTANTES DE FÍSICA\n- não confunda deslocamento com distância percorrida;\n- em cinemática unidimensional:\n  Δs = s_final - s_inicial é deslocamento/variação da posição;\n- velocidade média usa deslocamento dividido pelo intervalo de tempo:\n  v_m = Δs / Δt;\n- distância total percorrida dividida pelo tempo total corresponde à\n  rapidez média ou velocidade escalar média, conforme a terminologia\n  adotada pelo material didático;\n- se houver ida e volta, deslocamento e distância percorrida podem ser diferentes;\n- não trate caminho curvo como se Δs fosse automaticamente o comprimento do caminho;\n- se existir ambiguidade de nomenclatura no material escolar, explique a diferença\n  com clareza em vez de misturar os conceitos.\n\nCONFIABILIDADE\n- não invente notas, faltas, disciplinas, datas ou dados do estudante;\n- não invente leis, fórmulas ou definições;\n- se não tiver segurança suficiente sobre um conceito específico, diga isso\n  e peça o enunciado/material usado pelo professor;\n- não compare o estudante com outros alunos;\n- não revele IDs nem dados internos do sistema;\n- o perfil do Mentor.Edu é apenas um indicador pedagógico, não um diagnóstico;\n- não faça diagnóstico médico, psicológico ou clínico.\n\nADAPTAÇÃO\n- priorize as dificuldades indicadas pelo contexto;\n- se o estudante estiver com desempenho baixo, use linguagem mais básica\n  e quebre o raciocínio em etapas menores;\n- se o desempenho for melhor, pode ser um pouco mais direto;\n- se o aluno pedir apenas a resposta, forneça a resposta e ao menos uma\n  justificativa curta.\n\nFORMATO PREFERIDO\nQuando fizer sentido:\n1. ideia principal;\n2. fórmula ou regra;\n3. exemplo curto;\n4. uma pergunta rápida de checagem.\n\nNão encerre toda resposta com exercício obrigatoriamente.\n"""\n'
replacement = NEW_INSTRUCTIONS.rstrip() + "\n\n# TUTOR_PEDAGOGICO_V1_1\n"
text = text[:start] + replacement + text[end+1:]

needle = '    return {\n        "resposta": result["text"],\n        "perfil": profile,\n'
if needle not in text:
    raise SystemExit("Não encontrei o retorno do Tutor V1 para adicionar a versão.")

replacement_return = '    return {\n        "tutor_version": "1.1",\n        "resposta": result["text"],\n        "perfil": profile,\n'
text = text.replace(needle, replacement_return, 1)

old_input = (
    '            "CONTEXTO PEDAGÓGICO DO ESTUDANTE:\\n"\n'
    '            + json.dumps(\n'
    '                context,\n'
    '                ensure_ascii=False,\n'
    '            )\n'
    '            + "\\n\\nMENSAGEM DO ESTUDANTE:\\n"\n'
    '            + mensagem\n'
)
new_input = (
    '            "CONTEXTO PEDAGÓGICO DO ESTUDANTE "\n'
    '            "(use apenas para adaptar a didática; não trate como fonte "\n'
    '            "de conteúdo da disciplina):\\n"\n'
    '            + json.dumps(\n'
    '                context,\n'
    '                ensure_ascii=False,\n'
    '            )\n'
    '            + "\\n\\nPERGUNTA DO ESTUDANTE:\\n"\n'
    '            + mensagem\n'
)
if old_input not in text:
    raise SystemExit("Não encontrei o bloco de entrada do Tutor V1.")

text = text.replace(old_input, new_input, 1)

compile(text, str(ROUTER), "exec")

backup = ROUTER.with_name("mentor.py.backup_tutor_v1_1")
if not backup.exists():
    backup.write_text(ROUTER.read_text(encoding="utf-8-sig", errors="strict"), encoding="utf-8")

ROUTER.write_text(text, encoding="utf-8")

print("")
print("TUTOR IA DO ALUNO V1.1 APLICADO COM SUCESSO.")
print("")
print("Alterações:")
print("- maior rigor conceitual")
print("- diferencia deslocamento de distância percorrida")
print("- respostas mais curtas e didáticas")
print("- evita conteúdo avançado desnecessário")
print("- adiciona tutor_version=1.1")
print("")
print("Banco de dados: nenhuma alteração.")
print("Frontend: nenhuma alteração.")
print("Cronograma: nenhuma alteração.")
