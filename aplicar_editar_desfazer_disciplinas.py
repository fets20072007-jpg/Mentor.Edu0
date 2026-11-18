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

path = "backend/app/schema/subject.py"
text = read(path)

if "class SubjectUpdate(BaseModel):" not in text:
    marker = "class SubjectResponse(BaseModel):"
    block = """class SubjectUpdate(BaseModel):
    nome: Optional[str] = None
    carga_horaria: Optional[int] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    teacher_id: Optional[int] = None
    classroom_id: Optional[int] = None
    ativa: Optional[bool] = None

"""
    if marker not in text:
        raise RuntimeError("Não encontrei SubjectResponse.")
    text = text.replace(marker, block + marker, 1)

write(path, text)

path = "backend/app/router/academic/subject.py"
text = read(path)

if "SubjectUpdate" not in text.split("from app.security", 1)[0]:
    text = text.replace(
        "    SubjectCreate,\n    SubjectResponse,\n    SubjectTeacherUpdate",
        "    SubjectCreate,\n    SubjectUpdate,\n    SubjectResponse,\n    SubjectTeacherUpdate",
        1
    )

if "def update_subject(" not in text:
    marker = (
        "# =========================================================\n"
        "# ADMINISTRAÇÃO\n"
        "# TROCAR PROFESSOR RESPONSÁVEL PELA DISCIPLINA\n"
        "# ========================================================="
    )

    if marker not in text:
        raise RuntimeError("Não encontrei o ponto de inserção.")

    endpoint = """
# =========================================================
# ADMINISTRAÇÃO
# EDITAR / DESFAZER / REATIVAR DISCIPLINA
# =========================================================
@router.patch(
    "/{subject_id}",
    response_model=SubjectResponse
)
def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="Disciplina não encontrada."
        )

    payload = data.model_dump(exclude_unset=True)

    if not payload:
        return subject

    new_teacher_id = payload.get("teacher_id", subject.teacher_id)
    new_classroom_id = payload.get("classroom_id", subject.classroom_id)
    new_active = payload.get("ativa", subject.ativa)
    raw_name = payload.get("nome", subject.nome)
    clean_name = " ".join((raw_name or "").strip().split())

    if not clean_name:
        raise HTTPException(
            status_code=400,
            detail="O nome da disciplina não pode estar vazio."
        )

    teacher = (
        db.query(Teacher)
        .filter(Teacher.id == new_teacher_id)
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado."
        )

    if new_active and not teacher.ativo:
        raise HTTPException(
            status_code=400,
            detail="Professor inativo não pode receber uma disciplina ativa."
        )

    classroom = (
        db.query(Classroom)
        .filter(Classroom.id == new_classroom_id)
        .first()
    )

    if not classroom:
        raise HTTPException(
            status_code=404,
            detail="Turma não encontrada."
        )

    if new_active and not classroom.ativa:
        raise HTTPException(
            status_code=400,
            detail="Não é possível manter uma disciplina ativa em turma inativa."
        )

    if new_active:
        normalized_name = normalize_subject_name(clean_name)

        other_subjects = (
            db.query(Subject)
            .filter(
                Subject.id != subject.id,
                Subject.classroom_id == new_classroom_id,
                Subject.ativa == True
            )
            .all()
        )

        for other in other_subjects:
            if normalize_subject_name(other.nome) == normalized_name:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe uma disciplina ativa com este nome nesta turma."
                )

    old_classroom = (
        db.query(Classroom)
        .filter(Classroom.id == subject.classroom_id)
        .first()
    )

    detaches_old_teacher = (
        not new_active
        or new_teacher_id != subject.teacher_id
        or new_classroom_id != subject.classroom_id
    )

    if (
        subject.ativa
        and old_classroom
        and old_classroom.teacher_id == subject.teacher_id
        and detaches_old_teacher
    ):
        other_active_subject = (
            db.query(Subject)
            .filter(
                Subject.id != subject.id,
                Subject.teacher_id == subject.teacher_id,
                Subject.classroom_id == subject.classroom_id,
                Subject.ativa == True
            )
            .first()
        )

        if not other_active_subject:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Este professor é Diretor de Turma e esta é sua última "
                    "disciplina ativa na turma. Troque ou remova o DT antes."
                )
            )

    subject.nome = clean_name
    subject.teacher_id = new_teacher_id
    subject.classroom_id = new_classroom_id
    subject.ativa = new_active

    if "categoria" in payload:
        subject.categoria = (
            (payload.get("categoria") or "Outras").strip()
            or "Outras"
        )

    if "carga_horaria" in payload:
        carga = payload.get("carga_horaria")

        if carga is None or carga < 1:
            raise HTTPException(
                status_code=400,
                detail="Carga horária inválida."
            )

        subject.carga_horaria = carga

    if "descricao" in payload:
        subject.descricao = payload.get("descricao")

    db.commit()
    db.refresh(subject)

    return subject


"""

    text = text.replace(marker, endpoint + marker, 1)

write(path, text)

path = "frontend/dashboard.html"
text = read(path)

if "subject-actions.css" not in text:
    anchor = '<link rel="stylesheet" href="css/responsive.css">'
    if anchor not in text:
        raise RuntimeError("Não encontrei responsive.css.")
    text = text.replace(
        anchor,
        '<link rel="stylesheet" href="css/subject-actions.css?v=24.0">\n    ' + anchor,
        1
    )

text = re.sub(
    r'js/main\.js\?v=[^"]+',
    'js/main.js?v=24.0',
    text
)

write(path, text)

print("DISCIPLINAS: EDITAR / DESFAZER / REATIVAR APLICADO.")
