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

# BACKEND
path = "backend/app/router/academic/assessment.py"
text = read(path)
text = text.replace(
    "from app.database.models import User, Assessment, Question",
    "from app.database.models import User, Assessment, Question, Grade"
)

delete_assessment_block = """
# =========================================================
# PROFESSOR - EXCLUIR AVALIAÇÃO
# =========================================================
@router.delete("/{assessment_id}")
def delete_assessment(
    assessment_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    assessment = get_teacher_assessment(
        db=db,
        assessment_id=assessment_id,
        teacher_user_id=current_user.id
    )

    db.query(Grade).filter(
        Grade.assessment_id == assessment.id
    ).delete(synchronize_session=False)

    db.delete(assessment)
    db.commit()

    return {"ok": True, "message": "Avaliação excluída com sucesso."}

"""

if "def delete_assessment(" not in text:
    marker = "# =========================================================\n# ALUNO - VER PRÓPRIO RESULTADO"
    if marker not in text:
        raise RuntimeError("Não encontrei o ponto para inserir DELETE da avaliação.")
    text = text.replace(marker, delete_assessment_block + marker, 1)

delete_question_block = """
@router.delete("/{assessment_id}/questions/{question_id}")
def delete_assessment_question(
    assessment_id: int,
    question_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db)
):
    get_teacher_assessment(
        db=db,
        assessment_id=assessment_id,
        teacher_user_id=current_user.id
    )

    question = (
        db.query(Question)
        .filter(
            Question.id == question_id,
            Question.assessment_id == assessment_id
        )
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=404,
            detail="Questão não encontrada nesta avaliação."
        )

    db.delete(question)
    db.commit()

    return {"ok": True, "message": "Questão excluída com sucesso."}

"""

if "def delete_assessment_question(" not in text:
    marker = '@router.get(\n    "/{assessment_id}/results/students/{student_id}"'
    if marker not in text:
        raise RuntimeError("Não encontrei o ponto para inserir DELETE da questão.")
    text = text.replace(marker, delete_question_block + marker, 1)

write(path, text)

# API FRONTEND
path = "frontend/js/api/teacher.js"
text = read(path)

if "deleteAssessment =" not in text:
    anchor = "export const updateAssessment = (id, data) => api.patch(`/assessments/${id}`, data);"
    if anchor not in text:
        raise RuntimeError("Não encontrei updateAssessment em teacher.js.")
    text = text.replace(
        anchor,
        anchor + '\nexport const deleteAssessment = id => api.delete(`/assessments/${id}`);'
    )

if "deleteAssessmentQuestion =" not in text:
    anchor = "export const createAssessmentQuestion = (id, data) => api.post(`/assessments/${id}/questions`, data);"
    if anchor not in text:
        raise RuntimeError("Não encontrei createAssessmentQuestion em teacher.js.")
    text = text.replace(
        anchor,
        anchor + '\nexport const deleteAssessmentQuestion = (assessmentId, questionId) => api.delete(`/assessments/${assessmentId}/questions/${questionId}`);'
    )

write(path, text)

# CRIAÇÃO DE AVALIAÇÃO
path = "frontend/js/pages/teacher/assessment-create.js"
text = read(path)

if "deleteAssessmentQuestion" not in text.split('from "../../api/teacher.js";')[0]:
    text = text.replace(
        "  createAssessmentQuestion,\n",
        "  createAssessmentQuestion,\n  deleteAssessmentQuestion,\n",
        1
    )

old_preview = """function questionPreview(q, index) {
  return `
    <article class="question-preview-item">
      <strong>${index + 1}. ${escapeHtml(q.enunciado || "")}</strong>
      ${alternativesFor(q)}
      <small>Valor/peso: ${q.peso ?? 1}</small>
    </article>
  `;
}"""

new_preview = """function questionPreview(q, index) {
  return `
    <article class="question-preview-item">
      <div class="question-preview-head">
        <strong>${index + 1}. ${escapeHtml(q.enunciado || "")}</strong>
        <button
          type="button"
          class="mini-button mini-button--danger question-preview-delete"
          data-delete-question="${q.id}"
        >
          Excluir
        </button>
      </div>
      ${alternativesFor(q)}
      <small>Valor/peso: ${q.peso ?? 1}</small>
    </article>
  `;
}"""

if old_preview in text:
    text = text.replace(old_preview, new_preview, 1)
elif 'data-delete-question="${q.id}"' not in text:
    raise RuntimeError("Não consegui localizar questionPreview.")

listener_block = """
  target.querySelectorAll("[data-delete-question]").forEach(button => {
    button.addEventListener("click", async () => {
      const questionId = Number(button.dataset.deleteQuestion);
      const index = questions.findIndex(q => Number(q.id) === questionId);

      if (index < 0) return;

      const confirmed = window.confirm(
        `Excluir a questão ${index + 1}?\\n\\n` +
        "Se já houver respostas vinculadas a ela, elas também serão removidas."
      );

      if (!confirmed) return;
      button.disabled = true;

      try {
        await deleteAssessmentQuestion(assessment.id, questionId);
        questions.splice(index, 1);
        showToast("Questão excluída.", "success");
        renderQuestionBuilder(container, assessment, subjectName, questions);
      } catch (error) {
        button.disabled = false;
        showToast(
          error.message || "Não foi possível excluir a questão.",
          "error"
        );
      }
    });
  });

"""

if 'target.querySelectorAll("[data-delete-question]")' not in text:
    marker = '  const form = target.querySelector("[data-question-form]");'
    if marker not in text:
        raise RuntimeError("Não encontrei o ponto para ativar exclusão das questões.")
    text = text.replace(marker, listener_block + marker, 1)

write(path, text)

# DASHBOARD
path = "frontend/dashboard.html"
text = read(path)

if "assessment-delete.css" not in text:
    anchor = '<link rel="stylesheet" href="css/responsive.css">'
    if anchor not in text:
        raise RuntimeError("Não encontrei responsive.css.")
    text = text.replace(
        anchor,
        '<link rel="stylesheet" href="css/assessment-delete.css?v=22.2">\n    ' + anchor
    )

text = re.sub(r'js/main\.js\?v=[^"]+', 'js/main.js?v=22.2', text)
write(path, text)

print("EXCLUSÃO DE AVALIAÇÕES E QUESTÕES APLICADA.")
print("Agora rode:")
print('git add backend frontend')
print('git commit -m "feat: adiciona exclusao de avaliacoes e questoes"')
print('git push origin main')