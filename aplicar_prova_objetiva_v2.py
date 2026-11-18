from pathlib import Path
import re

ROOT = Path(".")

def read(path):
    p = ROOT / path
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    return p.read_text(encoding="utf-8-sig")

def write(path, text):
    (ROOT / path).write_text(text, encoding="utf-8", newline="\n")

# MODELS
path = "backend/app/database/models.py"
text = read(path)

if "imagem = Column(String, nullable=True)" not in text:
    anchor = "    alternativa_e = Column(String, nullable=True)\n"
    if anchor not in text:
        raise RuntimeError("Não encontrei alternativa_e em Question.")
    text = text.replace(
        anchor,
        anchor
        + "    imagem = Column(String, nullable=True)\n"
        + "    ordem = Column(Integer, default=0, nullable=False)\n",
        1
    )

write(path, text)

# QUESTION SCHEMA
path = "backend/app/schema/question.py"
text = read(path)

if text.count("imagem: Optional[str]") == 0:
    text = text.replace(
        "    alternativa_e: Optional[str] = None\n",
        "    alternativa_e: Optional[str] = None\n"
        "    imagem: Optional[str] = None\n"
        "    ordem: Optional[int] = None\n",
        1
    )

if text.count("imagem: Optional[str]") < 2:
    marker = (
        "    alternativa_e: Optional[str] = None\n\n"
        "    resposta_correta:"
    )
    text = text.replace(
        marker,
        "    alternativa_e: Optional[str] = None\n"
        "    imagem: Optional[str] = None\n"
        "    ordem: int = 0\n\n"
        "    resposta_correta:",
        1
    )

update_section = text.split("class QuestionUpdate(BaseModel):", 1)
if len(update_section) == 2 and "imagem: Optional[str]" not in update_section[1]:
    marker = (
        "    alternativa_e: Optional[str] = None\n"
        "    resposta_correta:"
    )
    text = text.replace(
        marker,
        "    alternativa_e: Optional[str] = None\n"
        "    imagem: Optional[str] = None\n"
        "    ordem: Optional[int] = None\n"
        "    resposta_correta:",
        1
    )

write(path, text)

# STUDENT QUESTION SCHEMA
path = "backend/app/schema/question_student.py"
text = read(path)

if "imagem: Optional[str] = None" not in text:
    text = text.replace(
        "    alternativa_e: Optional[str] = None\n",
        "    alternativa_e: Optional[str] = None\n"
        "    imagem: Optional[str] = None\n"
        "    ordem: int = 0\n",
        1
    )

write(path, text)

# ASSESSMENT ROUTER
path = "backend/app/router/academic/assessment.py"
text = read(path)

if "from sqlalchemy import func" not in text:
    text = text.replace(
        "from sqlalchemy.orm import Session\n",
        "from sqlalchemy.orm import Session\nfrom sqlalchemy import func\n",
        1
    )

old_query = (
    "        db.query(Question)\n"
    "        .filter(\n"
    "            Question.assessment_id\n"
    "            == assessment.id\n"
    "        )\n"
    "        .all()\n"
)

new_query = (
    "        db.query(Question)\n"
    "        .filter(\n"
    "            Question.assessment_id\n"
    "            == assessment.id\n"
    "        )\n"
    "        .order_by(\n"
    "            Question.ordem.asc(),\n"
    "            Question.id.asc()\n"
    "        )\n"
    "        .all()\n"
)

text = text.replace(old_query, new_query)

old_create = (
    "    question.assessment_id = assessment_id\n\n"
    "    nova_questao = Question(\n"
    "        **question.model_dump()\n"
    "    )\n"
)

new_create = (
    "    payload = question.model_dump()\n"
    "    payload[\"assessment_id\"] = assessment_id\n\n"
    "    if not payload.get(\"ordem\"):\n"
    "        max_order = (\n"
    "            db.query(func.max(Question.ordem))\n"
    "            .filter(\n"
    "                Question.assessment_id == assessment_id\n"
    "            )\n"
    "            .scalar()\n"
    "            or 0\n"
    "        )\n\n"
    "        payload[\"ordem\"] = max_order + 1\n\n"
    "    nova_questao = Question(\n"
    "        **payload\n"
    "    )\n"
)

if old_create not in text:
    raise RuntimeError(
        "Não encontrei o bloco de criação de questão no assessment.py."
    )

text = text.replace(old_create, new_create, 1)
write(path, text)

# MIGRATION LEVE
path = "backend/app/main.py"
text = read(path)

old_migration = '"questions": [("alternativa_e", "VARCHAR")],'
new_migration = (
    '"questions": [\n'
    '            ("alternativa_e", "VARCHAR"),\n'
    '            ("imagem", "VARCHAR"),\n'
    '            ("ordem", "INTEGER DEFAULT 0 NOT NULL")\n'
    '        ],'
)

if old_migration in text:
    text = text.replace(old_migration, new_migration, 1)
elif '("imagem", "VARCHAR")' not in text:
    raise RuntimeError("Não encontrei a migration de questions em main.py.")

write(path, text)

# CACHE
path = "frontend/dashboard.html"
text = read(path)

text = re.sub(
    r'assessment-models\.css\?v=[^"]+',
    'assessment-models.css?v=23.0',
    text
)

text = re.sub(
    r'js/main\.js\?v=[^"]+',
    'js/main.js?v=23.0',
    text
)

write(path, text)

print("MODELO DE PROVA OBJETIVA V2 APLICADO.")
print("- editor em uma coluna")
print("- edição, exclusão e reorganização")
print("- imagem por questão")
print("- item E opcional")
print("- A4 com duas colunas")
print("- gabarito separado do aluno")
