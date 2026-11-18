from pathlib import Path

ROOT = Path('.')
SIDEBAR = ROOT / 'frontend' / 'js' / 'components' / 'sidebar.js'

if not SIDEBAR.exists():
    raise SystemExit('Não encontrei frontend/js/components/sidebar.js. Rode este script na raiz do Mentor.Edu.')

text = SIDEBAR.read_text(encoding='utf-8-sig', errors='strict')
MARKER = 'MENTOR_EDU_MENU_ETAPA1'

def find_object_span(source: str, anchor: str):
    pos = source.find(anchor)
    if pos == -1:
        return None
    start = source.rfind('{', 0, pos + 1)
    if start == -1:
        return None
    depth = 0
    quote = None
    escaped = False
    for i in range(start, len(source)):
        ch = source[i]
        if quote:
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"', '`'):
            quote = ch
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                while end < len(source) and source[end] in ' \t':
                    end += 1
                if end < len(source) and source[end] == ',':
                    end += 1
                while end < len(source) and source[end] in ' \t':
                    end += 1
                if end < len(source) and source[end] == '\r':
                    end += 1
                if end < len(source) and source[end] == '\n':
                    end += 1
                return start, end
    return None

if MARKER in text:
    print('ETAPA 1 já está aplicada. Nenhuma alteração feita.')
    raise SystemExit(0)

student_start = text.find('aluno: [')
teacher_start = text.find('professor:', student_start)
if student_start == -1 or teacher_start == -1:
    raise SystemExit('Não consegui localizar o bloco de navegação do aluno. Nenhum arquivo foi alterado.')

student = text[student_start:teacher_start]

plan_span = find_object_span(student, 'label: "Plano de estudos"')
if plan_span:
    a, b = plan_span
    student = student[:a] + student[b:]

rec_span = find_object_span(student, 'route: "recommendations"')
if rec_span:
    a, b = rec_span
    student = student[:a] + student[b:]

disc_span = find_object_span(student, 'label: "Disciplinas"')
if not disc_span:
    raise SystemExit('Não encontrei o grupo Disciplinas. Nenhum arquivo foi alterado.')

mentor_group = '        // MENTOR_EDU_MENU_ETAPA1\n        { label: "Mentor Edu", icon: "message", children: [\n            { route: "mentor-edu", label: "Conversar com Mentor.Edu" },\n            { route: "study-plans", label: "Meu plano" },\n            { route: "recommendations", label: "Plano indicado" },\n            { route: "study-sessions", label: "Sessões de estudo" },\n        ]},\n'
insert_at = disc_span[1]
student = student[:insert_at] + mentor_group + student[insert_at:]

new_text = text[:student_start] + student + text[teacher_start:]

required = [
    'label: "Mentor Edu"',
    'route: "mentor-edu"',
    'label: "Conversar com Mentor.Edu"',
    'route: "study-plans"',
    'label: "Meu plano"',
    'route: "recommendations"',
    'label: "Plano indicado"',
    'route: "study-sessions"',
    'label: "Sessões de estudo"',
]
missing = [item for item in required if item not in new_text]
if missing:
    raise SystemExit('A validação falhou. Nenhum arquivo foi alterado. Faltou: ' + ', '.join(missing))

SIDEBAR.write_text(new_text, encoding='utf-8')

print('')
print('ETAPA 1 — MENU MENTOR EDU APLICADA COM SUCESSO.')
print('')
print('Somente este arquivo foi alterado:')
print('- frontend/js/components/sidebar.js')
print('')
print('Estrutura criada:')
print('Mentor Edu')
print('  - Conversar com Mentor.Edu')
print('  - Meu plano')
print('  - Plano indicado')
print('  - Sessões de estudo')
print('')
print('Também foram retirados do nível principal:')
print('- Plano de estudos')
print('- Recomendações')
print('')
print('NÃO foram alterados: login, main.js, router.js, backend, banco e CSS.')
print('')
print('Agora use Ctrl + F5 e teste somente o menu.')
print('Se algo ficar errado: git restore frontend/js/components/sidebar.js')
