from pathlib import Path
import shutil
import sys

ROOT = Path.cwd()

# Aceita execução tanto na raiz Mentor.Edu quanto dentro de backend.
if (
    ROOT.name.lower() == "backend"
    and (ROOT / "app" / "main.py").exists()
):
    MAIN = ROOT / "app" / "main.py"
else:
    MAIN = ROOT / "backend" / "app" / "main.py"

if not MAIN.exists():
    raise SystemExit(
        "ERRO: não encontrei backend/app/main.py.\n"
        "Rode este script na raiz Mentor.Edu ou dentro da pasta backend."
    )

text = MAIN.read_text(
    encoding="utf-8-sig",
    errors="strict",
)

original = text

old_startup = (
    'app.add_event_handler(\n'
    '    "startup",\n'
    '    _mentor_focus_push_startup,\n'
    ')\n'
)

old_shutdown = (
    'app.add_event_handler(\n'
    '    "shutdown",\n'
    '    _mentor_focus_push_shutdown,\n'
    ')\n'
)

# Também reconhece a forma de uma linha, caso tenha sido formatada.
old_startup_one = (
    'app.add_event_handler("startup", '
    '_mentor_focus_push_startup)'
)

old_shutdown_one = (
    'app.add_event_handler("shutdown", '
    '_mentor_focus_push_shutdown)'
)

new_startup = (
    'app.on_event("startup")(\n'
    '    _mentor_focus_push_startup\n'
    ')\n'
)

new_shutdown = (
    'app.on_event("shutdown")(\n'
    '    _mentor_focus_push_shutdown\n'
    ')\n'
)

changed = False

if old_startup in text:
    text = text.replace(
        old_startup,
        new_startup,
        1,
    )
    changed = True
elif old_startup_one in text:
    text = text.replace(
        old_startup_one,
        'app.on_event("startup")('
        '_mentor_focus_push_startup)',
        1,
    )
    changed = True
elif (
    'app.on_event("startup")('
    in text
):
    pass
else:
    raise SystemExit(
        "ERRO: não encontrei o registro de startup da Etapa 9B.2.\n"
        "Nenhuma alteração foi salva."
    )

if old_shutdown in text:
    text = text.replace(
        old_shutdown,
        new_shutdown,
        1,
    )
    changed = True
elif old_shutdown_one in text:
    text = text.replace(
        old_shutdown_one,
        'app.on_event("shutdown")('
        '_mentor_focus_push_shutdown)',
        1,
    )
    changed = True
elif (
    'app.on_event("shutdown")('
    in text
):
    pass
else:
    raise SystemExit(
        "ERRO: não encontrei o registro de shutdown da Etapa 9B.2.\n"
        "Nenhuma alteração foi salva."
    )

try:
    compile(
        text,
        str(MAIN),
        "exec",
    )
except SyntaxError as exc:
    raise SystemExit(
        "ERRO: a correção geraria erro de sintaxe. "
        "Nenhuma alteração foi salva.\n"
        f"Linha {exc.lineno}: {exc.msg}"
    )

if not changed:
    print(
        "A correção de compatibilidade já parece estar aplicada."
    )
    sys.exit(0)

backup = MAIN.with_name(
    MAIN.name
    + ".backup_9b2_startup_fastapi"
)

if not backup.exists():
    shutil.copy2(
        MAIN,
        backup,
    )

MAIN.write_text(
    text,
    encoding="utf-8",
)

print()
print("====================================================")
print(" MENTOR.EDU - CORREÇÃO STARTUP 9B.2 APLICADA")
print("====================================================")
print()
print(f"Arquivo: {MAIN}")
print(f"Backup:  {backup}")
print()
print("Corrigido:")
print("- removido app.add_event_handler(...) incompatível")
print("- startup registrado via app.on_event('startup')")
print("- shutdown registrado via app.on_event('shutdown')")
print("- sintaxe Python validada")
print()
print("Agora reinicie o backend.")
