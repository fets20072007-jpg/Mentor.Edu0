from pathlib import Path

ROOT = Path('.')


def read(path: str) -> str:
    p = ROOT / path
    if not p.exists():
        raise FileNotFoundError(f'Arquivo não encontrado: {path}')
    return p.read_text(encoding='utf-8-sig', errors='ignore')


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding='utf-8')


# 1) requirements.txt
req = None
for candidate in ('backend/requirements.txt', 'requirements.txt'):
    p = ROOT / candidate
    if p.exists():
        req = p
        break

if req is None:
    raise RuntimeError('Não encontrei requirements.txt.')

text = req.read_text(encoding='utf-8-sig', errors='ignore')
text = text.replace('openai>=2.0.0\\n', 'openai>=2.0.0\n')

lines = [line.strip() for line in text.splitlines() if line.strip()]
clean = []
openai_seen = False

for line in lines:
    if line.lower().startswith('openai'):
        if not openai_seen:
            clean.append('openai>=2.0.0')
            openai_seen = True
        continue
    clean.append(line)

if not openai_seen:
    clean.append('openai>=2.0.0')

req.write_text('\n'.join(clean) + '\n', encoding='utf-8')


# 2) config.py
path = 'backend/app/core/config.py'
text = read(path)
text = text.replace('\\n', '\n')

if 'import os' not in text:
    text = 'import os\n' + text

marker = '# Mentor Edu AI'
if marker in text:
    text = text.split(marker, 1)[0].rstrip() + '\n\n'

text += (
    '# Mentor Edu AI\n'
    'OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()\n'
    'AI_MODEL_FAST = os.getenv("AI_MODEL_FAST", "gpt-6-luna").strip()\n'
    'AI_MODEL_SMART = os.getenv("AI_MODEL_SMART", "gpt-6.1-sol").strip()\n'
)
write(path, text)


# 3) main.py
path = 'backend/app/main.py'
text = read(path)
text = text.replace(
    '\\nfrom app.router.ai.mentor import router as mentor_ai_router',
    '\nfrom app.router.ai.mentor import router as mentor_ai_router',
)
text = text.replace(
    '\\napp.include_router(mentor_ai_router)',
    '\napp.include_router(mentor_ai_router)',
)
write(path, text)


# 4) .env.example (se existir)
env_path = ROOT / '.env.example'
if env_path.exists():
    env = env_path.read_text(encoding='utf-8-sig', errors='ignore')
    env = env.replace('\\n', '\n')
    if '# Mentor Edu AI' in env:
        env = env.split('# Mentor Edu AI', 1)[0].rstrip() + '\n\n'
    env += (
        '# Mentor Edu AI\n'
        'OPENAI_API_KEY=\n'
        'AI_MODEL_FAST=gpt-6-luna\n'
        'AI_MODEL_SMART=gpt-6.1-sol\n'
    )
    env_path.write_text(env, encoding='utf-8')


# 5) validar sintaxe dos arquivos principais
for py_path in (
    'backend/app/core/config.py',
    'backend/app/main.py',
    'backend/app/router/ai/mentor.py',
    'backend/app/services/ai/mentor_client.py',
    'backend/app/services/ai/context_builder.py',
    'backend/app/schema/ai_mentor.py',
):
    p = ROOT / py_path
    if p.exists():
        compile(p.read_text(encoding='utf-8-sig'), py_path, 'exec')

print('CORREÇÃO DA IA APLICADA COM SUCESSO.')
print('Agora faça commit e push novamente.')
