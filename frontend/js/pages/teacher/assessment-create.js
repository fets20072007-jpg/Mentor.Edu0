import { getMySubjects } from "../../api/subjects.js";
import {
  getTeacherClassrooms,
  createAssessment,
  createAssessmentQuestion,
  updateAssessmentQuestion,
  deleteAssessmentQuestion,
  getTeacherAssessmentQuestions,
  updateAssessment
} from "../../api/teacher.js";
import { uploadFile } from "../../api/uploads.js";
import { escapeHtml } from "../../core/format.js";
import { pageHeader, surface, emptyBlock } from "../shared/page-ui.js";
import { showToast } from "../../components/toast.js";

const ASSESSMENT_TYPES = [
  "Prova",
  "Trabalho",
  "Atividade avaliativa",
  "Exercício"
];

const LAYOUTS = [
  ["duas_colunas", "Duas colunas"],
  ["coluna_unica", "Coluna única"],
  ["hibrido", "Híbrido"]
];

function subjectOptionLabel(subject) {
  const subjectName = String(subject?.nome || "").trim();
  const classroomName = String(
    subject?.classroom_nome
    || subject?.turma_nome
    || subject?.classroom?.nome
    || ""
  ).trim();

  if (!classroomName) {
    return subjectName || "Disciplina";
  }

  return `${subjectName} — ${classroomName}`;
}

function titleFor(type, subjectName) {
  const subject = String(subjectName || "").trim();
  if (!subject) return type || "Avaliação";

  const normalized = String(type || "").toLowerCase();

  if (normalized === "prova") return `Avaliação de ${subject}`;
  if (normalized === "exercício") return `Exercício de ${subject}`;
  if (normalized === "trabalho") return `Trabalho de ${subject}`;
  if (normalized === "atividade avaliativa") {
    return `Atividade Avaliativa de ${subject}`;
  }

  return `${type} de ${subject}`;
}

function questionNumber(index) {
  return String(index + 1).padStart(2, "0");
}

function sortQuestions(questions) {
  return [...questions].sort((a, b) => {
    const oa = Number(a.ordem || 0);
    const ob = Number(b.ordem || 0);

    if (oa && ob && oa !== ob) return oa - ob;
    if (oa && !ob) return -1;
    if (!oa && ob) return 1;

    return Number(a.id || 0) - Number(b.id || 0);
  });
}

function alternativesFor(q, className = "question-alt") {
  return ["a", "b", "c", "d", "e"]
    .map(letter => {
      const value = q[`alternativa_${letter}`];
      if (!value) return "";

      return `
        <div class="${className}">
          <span class="alt-letter">${letter.toLowerCase()})</span>
          <span>${escapeHtml(value)}</span>
        </div>
      `;
    })
    .join("");
}

function imageForQuestion(q, className = "question-image") {
  if (!q.imagem) return "";

  return `
    <figure class="${className}">
      <img src="${escapeHtml(q.imagem)}" alt="Imagem da questão">
    </figure>
  `;
}

function questionPreview(q, index, total) {
  return `
    <article class="question-editor-card" data-question-id="${q.id}">
      <div class="question-editor-card__top">
        <div class="question-editor-number">${questionNumber(index)}</div>

        <div class="question-editor-actions">
          <button type="button" class="mini-button question-action-button"
            data-move-up="${q.id}" ${index === 0 ? "disabled" : ""} title="Mover para cima">↑</button>

          <button type="button" class="mini-button question-action-button"
            data-move-down="${q.id}" ${index === total - 1 ? "disabled" : ""} title="Mover para baixo">↓</button>

          <button type="button" class="mini-button question-action-button"
            data-edit-question="${q.id}">Editar</button>

          <button type="button" class="mini-button mini-button--danger question-action-button"
            data-delete-question="${q.id}">Excluir</button>
        </div>
      </div>

      <div class="question-editor-content">
        <div class="question-editor-statement">${escapeHtml(q.enunciado || "")}</div>

        ${imageForQuestion(q, "question-editor-image")}

        <div class="question-editor-alternatives">
          ${alternativesFor(q)}
        </div>

        <div class="question-editor-meta">
          <span>${escapeHtml(q.tipo || "Objetiva")}</span>
          <span>${escapeHtml(q.dificuldade || "Médio")}</span>
          <span>Valor: ${q.peso ?? 1}</span>
          ${q.categoria ? `<span>${escapeHtml(q.categoria)}</span>` : ""}
        </div>
      </div>
    </article>
  `;
}

function printQuestion(q, index, layout) {
  const isDiscursive =
    String(q.tipo || "").trim().toLowerCase() === "discursiva";

  const fullWidth =
    layout === "coluna_unica" ||
    (layout === "hibrido" && isDiscursive);

  return `
    <section class="print-question ${fullWidth ? "full-width" : ""}">
      <div class="print-question-title">
        <strong>${questionNumber(index)}.</strong>
        <span>${escapeHtml(q.enunciado || "")}</span>
      </div>

      ${imageForQuestion(q, "print-question-image")}

      <div class="print-alternatives">
        ${alternativesFor(q, "print-alt")}
      </div>

      ${
        isDiscursive
          ? `<div class="answer-lines">
              <span></span><span></span><span></span><span></span>
            </div>`
          : ""
      }
    </section>
  `;
}

function openTeacherAnswerKey(assessment, questions) {
  const ordered = sortQuestions(questions);
  const w = window.open("", "_blank");

  if (!w) {
    showToast("Permita pop-ups para abrir o gabarito.", "error");
    return;
  }

  w.document.write(`<!doctype html>
  <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <title>Gabarito - ${escapeHtml(assessment.titulo)}</title>
      <style>
        @page { size: A4; margin: 18mm; }
        * { box-sizing: border-box; }
        body { font-family: "Times New Roman", Times, serif; color: #111; margin: 0; }
        .toolbar { font-family: Arial, sans-serif; max-width: 180mm; margin: 12px auto; }
        .toolbar button { min-height: 34px; padding: 0 13px; border: 1px solid #aaa; border-radius: 6px; background: white; cursor: pointer; }
        .page { max-width: 180mm; margin: 0 auto; }
        h1 { text-align: center; font-size: 17px; margin: 0 0 5px; text-transform: uppercase; }
        h2 { text-align: center; font-size: 14px; margin: 0 0 18px; font-weight: normal; }
        .key-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; border-top: 1px solid #111; padding-top: 12px; }
        .key-item { border-bottom: 1px solid #aaa; padding: 6px 0; text-align: center; }
        @media print { .toolbar { display: none; } .page { max-width: none; } }
      </style>
    </head>
    <body>
      <div class="toolbar"><button onclick="window.print()">Imprimir gabarito</button></div>
      <main class="page">
        <h1>Gabarito do professor</h1>
        <h2>${escapeHtml(assessment.titulo)}</h2>
        <div class="key-grid">
          ${ordered.map((q, i) => `
            <div class="key-item"><strong>${questionNumber(i)}.</strong> ${escapeHtml(q.resposta_correta || "—")}</div>
          `).join("")}
        </div>
      </main>
    </body>
  </html>`);

  w.document.close();
}

function openPrintableAssessment(assessment, subjectName, classroom, questions) {
  const ordered = sortQuestions(questions);
  const w = window.open("", "_blank");

  if (!w) {
    showToast("Permita pop-ups para visualizar a prova.", "error");
    return;
  }

  const layout = assessment.modelo_layout || "duas_colunas";
  const useCover = Boolean(assessment.usar_capa);

  const classInfo = [classroom?.serie, classroom?.turno].filter(Boolean);
  const titleLine = [
    String(assessment.titulo || "").toUpperCase(),
    ...classInfo.map(item => String(item).toUpperCase())
  ].join(" – ");

  const questionClass =
    layout === "coluna_unica"
      ? "questions one-column"
      : layout === "hibrido"
        ? "questions two-columns hybrid"
        : "questions two-columns";

  const body = ordered.length
    ? ordered.map((q, i) => printQuestion(q, i, layout)).join("")
    : "<p>Nenhuma questão adicionada ainda.</p>";

  w.document.write(`<!doctype html>
  <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <title>${escapeHtml(assessment.titulo)}</title>
      <style>
        @page { size: A4; margin: 10mm 12mm 12mm; }
        * { box-sizing: border-box; }
        html, body { margin: 0; padding: 0; background: #fff; }
        body {
          color: #111;
          font-family: "Times New Roman", Times, serif;
          font-size: 11.7pt;
          line-height: 1.18;
        }
        .toolbar { max-width: 186mm; margin: 10px auto 12px; font-family: Arial, sans-serif; }
        .toolbar button { min-height: 34px; padding: 0 14px; border: 1px solid #aeb6c2; border-radius: 6px; background: #fff; cursor: pointer; }
        .page { width: 100%; max-width: 186mm; margin: 0 auto; background: #fff; }

        .cover {
          min-height: 260mm;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          page-break-after: always;
        }
        .cover .brand { font-size: 15pt; font-weight: 700; text-transform: uppercase; }
        .cover h1 { margin: 18px 0 7px; max-width: 145mm; font-size: 23pt; line-height: 1.05; text-transform: uppercase; }
        .cover p { margin: 3px 0; font-size: 13pt; }

        .exam-header { margin-bottom: 7mm; }
        .institution-row {
          display: grid;
          grid-template-columns: 18mm 1fr 18mm;
          align-items: center;
          min-height: 15mm;
        }
        .logo-space { width: 16mm; height: 13mm; }
        .header-center { text-align: center; }
        .institution { font-size: 14.2pt; line-height: 1.05; font-weight: 700; text-transform: uppercase; }
        .assessment-heading { margin-top: 2mm; font-size: 13.2pt; line-height: 1.1; font-weight: 700; text-transform: uppercase; }

        .student-row {
          display: grid;
          grid-template-columns: minmax(0, 1fr) 28mm 38mm;
          gap: 4mm;
          align-items: end;
          margin-top: 4mm;
          font-size: 11.5pt;
          font-weight: 700;
        }
        .student-field { display: flex; gap: 2mm; align-items: flex-end; white-space: nowrap; }
        .student-line { display: block; flex: 1; min-width: 8mm; height: 5mm; border-bottom: .5pt solid #111; }

        .instructions { margin: -2mm 0 5mm; font-size: 10.8pt; text-align: justify; }

        .questions.two-columns {
          column-count: 2;
          column-gap: 8mm;
          column-rule: .5pt solid #555;
          column-fill: balance;
        }
        .questions.one-column { column-count: 1; }

        .print-question {
          display: inline-block;
          width: 100%;
          margin: 0 0 7mm;
          padding: 0;
          vertical-align: top;
          break-inside: avoid-column;
          page-break-inside: avoid;
        }

        .questions.hybrid .print-question.full-width {
          column-span: all;
          display: block;
          margin-bottom: 8mm;
        }

        .print-question-title {
          display: flex;
          gap: 1.5mm;
          align-items: flex-start;
          margin: 0 0 3.2mm;
          text-align: justify;
          hyphens: auto;
        }
        .print-question-title strong { flex: 0 0 auto; font-weight: 700; }
        .print-question-title span { flex: 1; min-width: 0; }

        .print-question-image { margin: 2mm auto 4mm; text-align: center; }
        .print-question-image img {
          max-width: 92%;
          max-height: 62mm;
          width: auto;
          height: auto;
          object-fit: contain;
          print-color-adjust: exact;
          -webkit-print-color-adjust: exact;
        }

        .print-alternatives { margin-top: 1mm; }
        .print-alt {
          display: grid;
          grid-template-columns: 6mm 1fr;
          gap: 1mm;
          margin: 2.2mm 0;
          line-height: 1.16;
        }
        .alt-letter { white-space: nowrap; }

        .answer-lines { margin-top: 4mm; }
        .answer-lines span { display: block; height: 8mm; border-bottom: .45pt solid #777; }

        @media print { .toolbar { display: none; } .page { max-width: none; } }
      </style>
    </head>
    <body>
      <div class="toolbar">
        <button onclick="window.print()">Imprimir / Salvar em PDF</button>
      </div>

      <div class="page">
        ${
          useCover
            ? `<section class="cover">
                <div class="brand">Mentor.Edu</div>
                <h1>${escapeHtml(assessment.titulo)}</h1>
                <p>${escapeHtml(subjectName || "")}</p>
                ${classInfo.length ? `<p>${escapeHtml(classInfo.join(" – "))}</p>` : ""}
              </section>`
            : ""
        }

        <header class="exam-header">
          <div class="institution-row">
            <div class="logo-space"></div>
            <div class="header-center">
              <div class="institution">Mentor.Edu</div>
              <div class="assessment-heading">${escapeHtml(titleLine)}</div>
            </div>
            <div class="logo-space"></div>
          </div>

          <div class="student-row">
            <div class="student-field">
              <span>Nome completo:</span>
              <span class="student-line"></span>
            </div>
            <div class="student-field">
              <span>Nº:</span>
              <span class="student-line"></span>
            </div>
            <div class="student-field">
              <span>Turma:</span>
              <span class="student-line"></span>
            </div>
          </div>
        </header>

        ${
          assessment.descricao
            ? `<p class="instructions">${escapeHtml(assessment.descricao)}</p>`
            : ""
        }

        <main class="${questionClass}">
          ${body}
        </main>
      </div>
    </body>
  </html>`);

  w.document.close();
}

function statusBox(assessment) {
  const published = Boolean(assessment.ativa);

  return `
    <div class="assessment-status ${published ? "is-published" : "is-draft"}">
      <strong>Status: ${published ? "Publicado" : "Rascunho"}</strong>
      <span>${published ? "Esta avaliação já está publicada." : "A avaliação está salva como rascunho."}</span>
    </div>
  `;
}

function renderQuestionBuilder(container, assessment, subjectName, classroom, rawQuestions) {
  let questions = sortQuestions(rawQuestions);
  const target = container.querySelector("[data-builder]");

  target.innerHTML = surface(`
    ${statusBox(assessment)}

    <div class="assessment-builder-head">
      <div>
        <h3 class="form-title">Editor de questões</h3>
        <p>As questões ficam em uma única coluna no editor. A divisão em colunas acontece apenas na impressão.</p>
      </div>

      <div class="assessment-builder-actions">
        <button type="button" class="mini-button" data-preview>Visualizar prova</button>
        ${
          assessment.gabarito_separado
            ? `<button type="button" class="mini-button" data-answer-key>Gabarito do professor</button>`
            : ""
        }
        <button type="button" class="mini-button" data-save>Salvar rascunho</button>
        <button type="button" class="mini-button mini-button--primary" data-publish>Publicar avaliação</button>
      </div>
    </div>

    <div class="assessment-layout-summary">
      <span><strong>Modelo:</strong> ${
        LAYOUTS.find(([value]) => value === (assessment.modelo_layout || "duas_colunas"))?.[1] || "Duas colunas"
      }</span>
      <span><strong>Turma:</strong> ${escapeHtml(classroom?.nome || "—")}</span>
      <span><strong>Série:</strong> ${escapeHtml(classroom?.serie || "—")}</span>
      <span><strong>Turno:</strong> ${escapeHtml(classroom?.turno || "—")}</span>
    </div>

    <form class="question-form page-section-gap" data-question-form>
      <div class="question-form-title-row">
        <div>
          <h3 data-question-form-title>Adicionar questão</h3>
          <small>Preencha o enunciado e as alternativas. O item E continua opcional.</small>
        </div>
        <button type="button" class="mini-button" data-cancel-edit style="display:none">Cancelar edição</button>
      </div>

      <div class="question-form-grid">
        <label>
          Tipo da questão
          <select name="tipo">
            <option value="Objetiva">Objetiva</option>
            <option value="Discursiva">Discursiva</option>
          </select>
        </label>

        <label>
          Dificuldade
          <select name="dificuldade">
            <option value="Fácil">Fácil</option>
            <option value="Médio" selected>Médio</option>
            <option value="Difícil">Difícil</option>
          </select>
        </label>

        <label class="question-form-span">
          Enunciado
          <textarea name="enunciado" required rows="5" placeholder="Digite o enunciado da questão..."></textarea>
          <small>Pode incluir símbolos, unidades e fórmulas digitadas no próprio texto.</small>
        </label>

        <label class="question-form-span">
          Imagem, gráfico ou diagrama
          <input type="file" name="imagem" accept=".png,.jpg,.jpeg,.webp">
          <small>Opcional. Use para figuras, gráficos, esquemas ou diagramas.</small>
        </label>

        <div class="question-current-image question-form-span" data-current-image style="display:none"></div>

        <div class="question-alternatives-grid question-form-span">
          <label data-alt>A<input name="alternativa_a"></label>
          <label data-alt>B<input name="alternativa_b"></label>
          <label data-alt>C<input name="alternativa_c"></label>
          <label data-alt>D<input name="alternativa_d"></label>

          <label data-alt-e style="display:none">
            E
            <input name="alternativa_e">
          </label>

          <div data-add-e class="assessment-add-e">
            <button type="button" class="mini-button" data-add-e-button>+ item E</button>
            <small>Adicione a quinta alternativa somente quando precisar.</small>
          </div>
        </div>

        <label data-answer>
          Resposta correta
          <select name="resposta_correta">
            <option value="">Selecione</option>
            <option>A</option>
            <option>B</option>
            <option>C</option>
            <option>D</option>
          </select>
        </label>

        <label>
          Valor da questão
          <input name="peso" type="number" min="0.1" step="0.1" value="1">
        </label>

        <label>
          Categoria/assunto
          <input name="categoria" placeholder="Ex.: Cinemática">
        </label>

        <label class="question-form-span">
          Explicação para correção
          <textarea name="explicacao" rows="3" placeholder="Uso interno do professor. Não aparece na prova do aluno."></textarea>
        </label>
      </div>

      <div class="form-actions">
        <button class="mini-button mini-button--primary" type="submit" data-submit-question>Adicionar questão</button>
      </div>
    </form>

    <div class="page-section-gap">
      <div class="question-list-heading">
        <div>
          <h3>Questões da avaliação</h3>
          <p>Use ↑ e ↓ para reorganizar. A numeração é automática.</p>
        </div>
        <span class="soft-label">${questions.length} questão(ões)</span>
      </div>

      <div class="question-editor-list" data-question-list>
        ${
          questions.length
            ? questions.map((q, index) => questionPreview(q, index, questions.length)).join("")
            : emptyBlock("Nenhuma questão", "Adicione a primeira questão acima.", "book")
        }
      </div>
    </div>
  `);

  const form = target.querySelector("[data-question-form]");
  const type = form.querySelector('[name="tipo"]');
  const altE = form.querySelector("[data-alt-e]");
  const addE = form.querySelector("[data-add-e]");
  const answer = form.querySelector('[name="resposta_correta"]');
  const formTitle = form.querySelector("[data-question-form-title]");
  const cancelEdit = form.querySelector("[data-cancel-edit]");
  const submitButton = form.querySelector("[data-submit-question]");
  const currentImage = form.querySelector("[data-current-image]");

  let editingQuestionId = null;
  let editingImage = null;

  const addEOption = () => {
    if (![...answer.options].some(option => option.value === "E")) {
      answer.insertAdjacentHTML("beforeend", "<option>E</option>");
    }
  };

  const removeEOption = () => {
    [...answer.options]
      .filter(option => option.value === "E")
      .forEach(option => option.remove());

    if (answer.value === "E") answer.value = "";
  };

  const showE = () => {
    altE.style.display = "";
    addE.style.display = "none";
    addEOption();
  };

  const hideE = () => {
    altE.style.display = "none";
    altE.querySelector("input").value = "";
    addE.style.display = "";
    removeEOption();
  };

  const syncType = () => {
    const objetiva = type.value === "Objetiva";

    form.querySelectorAll("[data-alt],[data-answer]").forEach(
      el => { el.style.display = objetiva ? "" : "none"; }
    );

    if (!objetiva) {
      altE.style.display = "none";
      addE.style.display = "none";
    } else if (altE.querySelector("input").value) {
      showE();
    } else {
      hideE();
    }
  };

  const resetQuestionForm = () => {
    editingQuestionId = null;
    editingImage = null;
    form.reset();
    type.value = "Objetiva";
    form.querySelector('[name="dificuldade"]').value = "Médio";
    form.querySelector('[name="peso"]').value = "1";
    formTitle.textContent = "Adicionar questão";
    submitButton.textContent = "Adicionar questão";
    cancelEdit.style.display = "none";
    currentImage.style.display = "none";
    currentImage.innerHTML = "";
    hideE();
    syncType();
  };

  const startEdit = question => {
    editingQuestionId = Number(question.id);
    editingImage = question.imagem || null;

    type.value = question.tipo || "Objetiva";
    form.querySelector('[name="dificuldade"]').value = question.dificuldade || "Médio";
    form.querySelector('[name="enunciado"]').value = question.enunciado || "";
    form.querySelector('[name="alternativa_a"]').value = question.alternativa_a || "";
    form.querySelector('[name="alternativa_b"]').value = question.alternativa_b || "";
    form.querySelector('[name="alternativa_c"]').value = question.alternativa_c || "";
    form.querySelector('[name="alternativa_d"]').value = question.alternativa_d || "";
    form.querySelector('[name="alternativa_e"]').value = question.alternativa_e || "";
    form.querySelector('[name="resposta_correta"]').value = question.resposta_correta || "";
    form.querySelector('[name="peso"]').value = question.peso ?? 1;
    form.querySelector('[name="categoria"]').value = question.categoria || "";
    form.querySelector('[name="explicacao"]').value = question.explicacao || "";

    if (question.alternativa_e) showE();
    else hideE();

    if (editingImage) {
      currentImage.style.display = "";
      currentImage.innerHTML = `
        <span>Imagem atual:</span>
        <img src="${escapeHtml(editingImage)}" alt="Imagem atual da questão">
      `;
    } else {
      currentImage.style.display = "none";
      currentImage.innerHTML = "";
    }

    syncType();

    const currentIndex = questions.findIndex(q => Number(q.id) === editingQuestionId);
    formTitle.textContent = `Editando questão ${questionNumber(currentIndex)}`;
    submitButton.textContent = "Salvar alterações";
    cancelEdit.style.display = "";

    form.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  async function moveQuestion(questionId, direction) {
    const ordered = sortQuestions(questions);
    const currentIndex = ordered.findIndex(q => Number(q.id) === Number(questionId));
    const targetIndex = currentIndex + direction;

    if (currentIndex < 0 || targetIndex < 0 || targetIndex >= ordered.length) return;

    const current = ordered[currentIndex];
    const targetQuestion = ordered[targetIndex];

    try {
      await Promise.all([
        updateAssessmentQuestion(assessment.id, current.id, { ordem: targetIndex + 1 }),
        updateAssessmentQuestion(assessment.id, targetQuestion.id, { ordem: currentIndex + 1 })
      ]);

      ordered[currentIndex] = { ...targetQuestion, ordem: currentIndex + 1 };
      ordered[targetIndex] = { ...current, ordem: targetIndex + 1 };
      questions = ordered;

      renderQuestionBuilder(container, assessment, subjectName, classroom, questions);
    } catch (error) {
      showToast(error.message || "Não foi possível reorganizar as questões.", "error");
    }
  }

  target.querySelector("[data-add-e-button]").addEventListener("click", showE);
  type.addEventListener("change", syncType);
  cancelEdit.addEventListener("click", resetQuestionForm);
  syncType();

  target.querySelector("[data-preview]").addEventListener("click", () => {
    openPrintableAssessment(assessment, subjectName, classroom, questions);
  });

  target.querySelector("[data-answer-key]")?.addEventListener("click", () => {
    openTeacherAnswerKey(assessment, questions);
  });

  target.querySelector("[data-save]").addEventListener("click", async () => {
    try {
      assessment = await updateAssessment(assessment.id, { ativa: false });
      showToast("Avaliação salva como rascunho.", "success");
      renderQuestionBuilder(container, assessment, subjectName, classroom, questions);
    } catch (error) {
      showToast(error.message || "Não foi possível salvar a avaliação.", "error");
    }
  });

  target.querySelector("[data-publish]").addEventListener("click", async () => {
    if (!questions.length && !assessment.arquivo) {
      showToast("Adicione pelo menos uma questão antes de publicar.", "error");
      return;
    }

    try {
      assessment = await updateAssessment(assessment.id, { ativa: true });
      showToast("Avaliação publicada.", "success");
      renderQuestionBuilder(container, assessment, subjectName, classroom, questions);
    } catch (error) {
      showToast(error.message || "Não foi possível publicar a avaliação.", "error");
    }
  });

  target.querySelectorAll("[data-edit-question]").forEach(button => {
    button.addEventListener("click", () => {
      const id = Number(button.dataset.editQuestion);
      const question = questions.find(q => Number(q.id) === id);
      if (question) startEdit(question);
    });
  });

  target.querySelectorAll("[data-move-up]").forEach(button => {
    button.addEventListener("click", () => moveQuestion(Number(button.dataset.moveUp), -1));
  });

  target.querySelectorAll("[data-move-down]").forEach(button => {
    button.addEventListener("click", () => moveQuestion(Number(button.dataset.moveDown), 1));
  });

  target.querySelectorAll("[data-delete-question]").forEach(button => {
    button.addEventListener("click", async () => {
      const questionId = Number(button.dataset.deleteQuestion);
      const index = questions.findIndex(q => Number(q.id) === questionId);
      if (index < 0) return;

      const confirmed = window.confirm(
        `Excluir a questão ${questionNumber(index)}?\n\nEssa ação é permanente.`
      );
      if (!confirmed) return;

      button.disabled = true;

      try {
        await deleteAssessmentQuestion(assessment.id, questionId);
        questions.splice(index, 1);
        showToast("Questão excluída.", "success");
        renderQuestionBuilder(container, assessment, subjectName, classroom, questions);
      } catch (error) {
        button.disabled = false;
        showToast(error.message || "Não foi possível excluir a questão.", "error");
      }
    });
  });

  form.addEventListener("submit", async event => {
    event.preventDefault();

    const f = new FormData(form);
    const objetiva = f.get("tipo") === "Objetiva";
    submitButton.disabled = true;

    try {
      let imagem = editingImage;
      const imageFile = f.get("imagem");

      if (imageFile && imageFile.size) {
        const uploaded = await uploadFile(imageFile);
        imagem = uploaded.arquivo;
      }

      const payload = {
        tipo: f.get("tipo"),
        enunciado: String(f.get("enunciado") || "").trim(),
        alternativa_a: objetiva ? (String(f.get("alternativa_a") || "").trim() || null) : null,
        alternativa_b: objetiva ? (String(f.get("alternativa_b") || "").trim() || null) : null,
        alternativa_c: objetiva ? (String(f.get("alternativa_c") || "").trim() || null) : null,
        alternativa_d: objetiva ? (String(f.get("alternativa_d") || "").trim() || null) : null,
        alternativa_e: objetiva ? (String(f.get("alternativa_e") || "").trim() || null) : null,
        resposta_correta: objetiva ? (f.get("resposta_correta") || null) : null,
        explicacao: String(f.get("explicacao") || "").trim() || null,
        dificuldade: f.get("dificuldade"),
        peso: Number(f.get("peso") || 1),
        categoria: String(f.get("categoria") || "").trim() || null,
        imagem
      };

      if (editingQuestionId) {
        const updated = await updateAssessmentQuestion(
          assessment.id,
          editingQuestionId,
          payload
        );

        questions = questions.map(q =>
          Number(q.id) === editingQuestionId ? updated : q
        );

        showToast("Questão atualizada.", "success");
      } else {
        payload.ordem = questions.length + 1;

        const created = await createAssessmentQuestion(
          assessment.id,
          payload
        );

        questions.push(created);
        showToast("Questão adicionada à avaliação.", "success");
      }

      renderQuestionBuilder(container, assessment, subjectName, classroom, questions);
    } catch (error) {
      submitButton.disabled = false;
      showToast(error.message || "Não foi possível salvar a questão.", "error");
    }
  });
}

export async function renderTeacherAssessmentCreate(container, navigate) {
  const [subs, classrooms] = await Promise.all([
    getMySubjects(),
    getTeacherClassrooms()
  ]);

  container.innerHTML = `
    ${pageHeader(
      "Criar avaliação",
      "Monte a prova no Mentor Edu ou publique um arquivo pronto."
    )}

    ${surface(`
      <form class="inline-form" data-form>
        <div class="form-grid">
          <label>
            Disciplina
            <select name="subject_id" required>
              <option value="">Selecione</option>
              ${subs.map(s => `<option value="${s.id}">${escapeHtml(subjectOptionLabel(s))}</option>`).join("")}
            </select>
          </label>

          <label>
            Tipo
            <select name="tipo" required>
              ${ASSESSMENT_TYPES.map(type => `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`).join("")}
            </select>
          </label>

          <label class="form-span-2">
            Título
            <input name="titulo" required placeholder="Preenchido automaticamente pela disciplina">
            <small>O Mentor Edu sugere o título, mas você pode editar.</small>
          </label>

          <label class="form-span-2">
            Descrição / instruções
            <textarea name="descricao" rows="3" placeholder="Ex.: Leia atentamente e marque apenas uma alternativa."></textarea>
          </label>

          <label>
            Valor total
            <input name="valor" type="number" step="0.1" min="0" value="10" required>
          </label>

          <label>
            Data
            <input name="data" type="datetime-local">
          </label>

          <label>
            Semestre
            <input name="semestre" type="number" min="1" max="2">
          </label>

          <label>
            Ano letivo
            <input name="ano_letivo" type="number" min="2000" max="2100">
          </label>
        </div>

        <div class="assessment-model-box">
          <div class="assessment-model-title">
            <div>
              <strong>Modelo de impressão</strong>
              <small>Isso altera a folha impressa, não a ordem das questões no editor.</small>
            </div>
          </div>

          <div class="assessment-model-grid">
            ${LAYOUTS.map(([value, label], index) => `
              <label class="assessment-model-option">
                <input type="radio" name="modelo_layout" value="${value}" ${index === 0 ? "checked" : ""}>
                <span>
                  <strong>${label}</strong>
                  <small>
                    ${
                      value === "duas_colunas"
                        ? "Modelo objetivo semelhante à prova escolar de referência."
                        : value === "coluna_unica"
                          ? "Questões ocupam toda a largura da folha."
                          : "Objetivas em colunas e discursivas em largura total."
                    }
                  </small>
                </span>
              </label>
            `).join("")}
          </div>

          <div class="assessment-extra-options">
            <label>
              <input type="checkbox" name="usar_capa">
              <span><strong>Usar capa</strong><small>Adiciona uma página de abertura.</small></span>
            </label>

            <label>
              <input type="checkbox" name="gabarito_separado">
              <span><strong>Gabarito do professor</strong><small>Fica separado da prova destinada ao aluno.</small></span>
            </label>
          </div>
        </div>

        <div class="assessment-mode-box">
          <strong>Como deseja criar esta avaliação?</strong>

          <div class="assessment-mode-options">
            <label>
              <input type="radio" name="modo" value="sistema" checked>
              Criar no Mentor Edu
            </label>

            <label>
              <input type="radio" name="modo" value="arquivo">
              Usar arquivo pronto
            </label>
          </div>
        </div>

        <div data-file-area class="assessment-file-area" style="display:none">
          <label>
            Arquivo pronto da avaliação
            <input name="arquivo" type="file" accept=".pdf,.odt,.doc,.docx,.png,.jpg,.jpeg">
            <small>PDF, ODT, DOC/DOCX ou imagem.</small>
          </label>
        </div>

        <div class="form-actions" data-create-actions>
          <button class="mini-button mini-button--primary" type="submit">Criar avaliação</button>
        </div>
      </form>
    `)}

    <div data-builder></div>
  `;

  const form = container.querySelector("[data-form]");
  const subjectSelect = form.querySelector('[name="subject_id"]');
  const typeSelect = form.querySelector('[name="tipo"]');
  const titleInput = form.querySelector('[name="titulo"]');
  const fileArea = form.querySelector("[data-file-area]");
  const actions = form.querySelector("[data-create-actions]");

  let titleWasManuallyEdited = false;

  const syncSuggestedTitle = () => {
    if (titleWasManuallyEdited) return;

    const subject = subs.find(
      s => Number(s.id) === Number(subjectSelect.value)
    );

    titleInput.value = titleFor(typeSelect.value, subject?.nome || "");
  };

  titleInput.addEventListener("input", () => {
    titleWasManuallyEdited = Boolean(titleInput.value.trim());
  });

  subjectSelect.addEventListener("change", () => {
    if (!titleInput.value.trim()) titleWasManuallyEdited = false;
    syncSuggestedTitle();
  });

  typeSelect.addEventListener("change", () => {
    if (!titleWasManuallyEdited) syncSuggestedTitle();
  });

  const renderModeActions = () => {
    const modo = form.querySelector('[name="modo"]:checked')?.value || "sistema";
    fileArea.style.display = modo === "arquivo" ? "" : "none";

    if (modo === "arquivo") {
      actions.innerHTML = `
        <button class="mini-button" type="button" data-file-draft>Salvar como rascunho</button>
        <button class="mini-button mini-button--primary" type="button" data-file-publish>Publicar arquivo</button>
      `;

      actions.querySelector("[data-file-draft]")
        .addEventListener("click", () => createFromFile(false));

      actions.querySelector("[data-file-publish]")
        .addEventListener("click", () => createFromFile(true));
    } else {
      actions.innerHTML = `
        <button class="mini-button mini-button--primary" type="submit">Criar avaliação</button>
      `;
    }
  };

  form.querySelectorAll('[name="modo"]').forEach(
    radio => radio.addEventListener("change", renderModeActions)
  );

  renderModeActions();

  async function buildBasePayload(published, requireFile = false) {
    const f = new FormData(form);

    let arquivo = null;
    let arquivo_nome = null;
    const file = f.get("arquivo");

    if (requireFile && (!file || !file.size)) {
      throw new Error("Selecione um arquivo antes de continuar.");
    }

    if (file && file.size) {
      const uploaded = await uploadFile(file);
      arquivo = uploaded.arquivo;
      arquivo_nome = uploaded.nome_original || file.name;
    }

    return {
      titulo: String(f.get("titulo") || "").trim(),
      descricao: String(f.get("descricao") || "").trim() || null,
      tipo: f.get("tipo"),
      valor: Number(f.get("valor")),
      subject_id: Number(f.get("subject_id")),
      data: f.get("data") ? new Date(f.get("data")).toISOString() : null,
      semestre: f.get("semestre") ? Number(f.get("semestre")) : null,
      ano_letivo: f.get("ano_letivo") ? Number(f.get("ano_letivo")) : null,
      modelo_layout: f.get("modelo_layout") || "duas_colunas",
      usar_capa: f.get("usar_capa") === "on",
      gabarito_separado: f.get("gabarito_separado") === "on",
      arquivo,
      arquivo_nome,
      ativa: published
    };
  }

  async function createFromFile(published) {
    try {
      const payload = await buildBasePayload(published, true);
      const assessment = await createAssessment(payload);

      showToast(
        published ? "Arquivo publicado." : "Arquivo salvo como rascunho.",
        "success"
      );

      form.querySelectorAll("input,textarea,select,button").forEach(
        el => { el.disabled = true; }
      );

      container.querySelector("[data-builder]").innerHTML = surface(`
        ${statusBox(assessment)}
        <h3>${escapeHtml(assessment.titulo)}</h3>
        <p>${escapeHtml(assessment.arquivo_nome || "Arquivo anexado")}</p>
      `);
    } catch (error) {
      showToast(
        error.message || "Não foi possível salvar o arquivo.",
        "error"
      );
    }
  }

  form.addEventListener("submit", async event => {
    event.preventDefault();

    const modo = form.querySelector('[name="modo"]:checked')?.value || "sistema";
    if (modo !== "sistema") return;

    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;

    try {
      const payload = await buildBasePayload(false, false);
      const assessment = await createAssessment(payload);

      const subject = subs.find(
        s => Number(s.id) === Number(assessment.subject_id)
      );

      const classroom = classrooms.find(
        c =>
          Number(c.id) ===
          Number(assessment.classroom_id || subject?.classroom_id)
      ) || null;

      const questions = await getTeacherAssessmentQuestions(
        assessment.id
      ).catch(() => []);

      showToast(
        "Avaliação criada. Agora adicione as questões.",
        "success"
      );

      form.querySelectorAll("input,textarea,select,button").forEach(
        el => { el.disabled = true; }
      );

      renderQuestionBuilder(
        container,
        assessment,
        subject?.nome || "",
        classroom,
        questions
      );
    } catch (error) {
      button.disabled = false;
      showToast(
        error.message || "Não foi possível criar a avaliação.",
        "error"
      );
    }
  });

  syncSuggestedTitle();
}
