from pathlib import Path
import re

dashboard = Path("frontend/dashboard.html")
if not dashboard.exists():
    raise SystemExit("Rode este script na raiz do Mentor.Edu.")

text = dashboard.read_text(encoding="utf-8-sig")

# força recarga do CSS dos modelos
if "assessment-models.css" in text:
    text = re.sub(
        r'assessment-models\.css\?v=[^"]+',
        'assessment-models.css?v=22.1',
        text
    )

# força recarga do JS principal, que importa a tela do professor
text = re.sub(
    r'js/main\.js\?v=[^"]+',
    'js/main.js?v=22.1',
    text
)

dashboard.write_text(text, encoding="utf-8", newline="\n")

print("REFINO VISUAL DA PROVA APLICADO.")
print("- duas colunas com sequência vertical")
print("- cabeçalho mais parecido com prova impressa")
print("- radio buttons e checkboxes compactos")
print("- cards de modelo menores e proporcionais")
