from pathlib import Path
import re

ROOT = Path(".")

def read(path):
    p = ROOT / path
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    return p.read_text(encoding="utf-8-sig")

def write(path, text):
    p = ROOT / path
    p.write_text(text, encoding="utf-8", newline="\n")

# models.py
path = "backend/app/database/models.py"
text = read(path)

if "alternativa_e = Column(String, nullable=True)" not in text:
    text = text.replace(
        "    alternativa_d = Column(String, nullable=True)\n",
        "    alternativa_d = Column(String, nullable=True)\n"
        "    alternativa_e = Column(String, nullable=True)\n",
        1
    )

if "modelo_layout = Column(String" not in text:
    text = text.replace(
        "    arquivo_nome = Column(String, nullable=True)\n",
        "    arquivo_nome = Column(String, nullable=True)\n"
        "    modelo_layout = Column(String, default=\"duas_colunas\", nullable=False)\n"
        "    usar_capa = Column(Boolean, default=False, nullable=False)\n"
        "    gabarito_separado = Column(Boolean, default=False, nullable=False)\n",
        1
    )

write(path, text)

# question schema
path = "backend/app/schema/question.py"
text = read(path)

text = re.sub(
    r"(class QuestionCreate\(BaseModel\):[\s\S]*?    alternativa_d: Optional\[str\] = None\n)(?!    alternativa_e)",
    r"\1    alternativa_e: Optional[str] = None\n",
    text,
    count=1
)

text = re.sub(
    r"(class QuestionResponse\(BaseModel\):[\s\S]*?    alternativa_d: Optional\[str\]\n)(?!    alternativa_e)",
    r"\1    alternativa_e: Optional[str] = None\n",
    text,
    count=1
)

text = re.sub(
    r"(class QuestionUpdate\(BaseModel\):[\s\S]*?    alternativa_d: Optional\[str\] = None\n)(?!    alternativa_e)",
    r"\1    alternativa_e: Optional[str] = None\n",
    text,
    count=1
)

write(path, text)

# question student schema
path = "backend/app/schema/question_student.py"
text = read(path)

if "alternativa_e: Optional[str] = None" not in text:
    text = text.replace(
        "    alternativa_d: Optional[str] = None\n",
        "    alternativa_d: Optional[str] = None\n"
        "    alternativa_e: Optional[str] = None\n"
    )

write(path, text)

# assessment schema
path = "backend/app/schema/assessment.py"
text = read(path)

if 'modelo_layout: str = "duas_colunas"' not in text:
    text = text.replace(
        "    subject_id: int\n",
        "    subject_id: int\n"
        "    modelo_layout: str = \"duas_colunas\"\n"
        "    usar_capa: bool = False\n"
        "    gabarito_separado: bool = False\n",
        1
    )

if text.count("modelo_layout") < 2:
    text = text.replace(
        "    subject_id: int\n    class Config:",
        "    subject_id: int\n"
        "    modelo_layout: str = \"duas_colunas\"\n"
        "    usar_capa: bool = False\n"
        "    gabarito_separado: bool = False\n"
        "    class Config:"
    )

if "modelo_layout: Optional[str]" not in text:
    text = text.replace(
        "    subject_id: Optional[int] = None\n",
        "    subject_id: Optional[int] = None\n"
        "    modelo_layout: Optional[str] = None\n"
        "    usar_capa: Optional[bool] = None\n"
        "    gabarito_separado: Optional[bool] = None\n"
    )

write(path, text)

# assessment service
path = "backend/app/services/academic/assessment_service.py"
text = read(path)

if "modelo_layout=assessment.modelo_layout" not in text:
    text = text.replace(
        "        subject_id=subject.id,\n",
        "        subject_id=subject.id,\n"
        "        modelo_layout=assessment.modelo_layout,\n"
        "        usar_capa=assessment.usar_capa,\n"
        "        gabarito_separado=assessment.gabarito_separado,\n",
        1
    )

write(path, text)

# main migrations
path = "backend/app/main.py"
text = read(path)

old = '"assessments": [("arquivo", "VARCHAR"), ("arquivo_nome", "VARCHAR")],'
new = '''"assessments": [
            ("arquivo", "VARCHAR"),
            ("arquivo_nome", "VARCHAR"),
            ("modelo_layout", "VARCHAR DEFAULT 'duas_colunas' NOT NULL"),
            ("usar_capa", "BOOLEAN DEFAULT FALSE NOT NULL"),
            ("gabarito_separado", "BOOLEAN DEFAULT FALSE NOT NULL")
        ],
        "questions": [("alternativa_e", "VARCHAR")],'''

if '"questions": [("alternativa_e", "VARCHAR")]' not in text:
    if old not in text:
        raise RuntimeError("Não encontrei o bloco de migrations de assessments em backend/app/main.py")
    text = text.replace(old, new)

write(path, text)

# dashboard css include
path = "frontend/dashboard.html"
text = read(path)

if "assessment-models.css" not in text:
    anchor = '<link rel="stylesheet" href="css/responsive.css">'
    if anchor not in text:
        raise RuntimeError("Não encontrei css/responsive.css em dashboard.html")
    text = text.replace(
        anchor,
        '<link rel="stylesheet" href="css/assessment-models.css?v=22.0">\n    ' + anchor
    )

text = re.sub(r'js/main\.js\?v=[^"]+', 'js/main.js?v=22.0', text)
write(path, text)

print("FASE 1 DE MODELOS DE AVALIAÇÃO APLICADA.")
print("- alternativa E opcional")
print("- duas colunas / coluna única / híbrido")
print("- capa opcional")
print("- gabarito separado")
print("- título automático por disciplina/tipo")
print("- upload aceita ODT e DOCX")
