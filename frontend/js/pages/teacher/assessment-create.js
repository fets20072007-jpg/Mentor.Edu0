import { getMySubjects } from "../../api/subjects.js";
import {
  createAssessment,
  createAssessmentQuestion,
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

function alternativesFor(q) {
  return ["a", "b", "c", "d", "e"]
    .map(letter => {
      const value = q[`alternativa_${letter}`];
      if (!value) return "";
      return `<div class="question-alt">${letter.toUpperCase()}) ${escapeHtml(value)}</div>`;
    })
    .join("");
}

function questionPreview(q, index) {
  return `
    <article class="question-preview-item">
      <strong>${index + 1}. ${escapeHtml(q.enunciado || "")}</strong>
      ${alternativesFor(q)}
      <small>Valor/peso: ${q.peso ?? 1}</small>
    </article>
  `;
}

function printQuestion(q, index, layout) {
  const isDiscursive = String(q.tipo || "").toLowerCase() === "discursiva";
  const fullWidth = layout === "coluna_unica" || (layout === "hibrido" && isDiscursive);

  return `
    <section class="print-question ${fullWidth ? "full-width" : ""}">
      <div class="question-title">
        ${index + 1}. ${escapeHtml(q.enunciado || "")}
      </div>
      ${alternativesFor(q)}
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

function openPrintableAssessment(assessment, subjectName, questions) {
  const w = window.open("", "_blank");
  if (!w) {
    showToast("Permita pop-ups para visualizar a prova.", "error");
    return;
  }

  const layout = assessment.modelo_layout || "duas_colunas";
  const useCover = Boolean(assessment.usar_capa);
  const separatedKey = Boolean(assessment.gabarito_separado);

  const body = questions.length
    ? questions.map((q, i) => printQuestion(q, i, layout)).join("")
    : "<p>Nenhuma questão adicionada ainda.</p>";

  const key = separatedKey && questions.length
    ? `
      <section class="answer-key">
        <h2>Gabarito</h2>
        <div class="answer-key-grid">
          ${questions.map((q, i) => `
            <div><strong>${i + 1}.</strong> ${escapeHtml(q.resposta_correta || "—")}</div>
          `).join("")}
        </div>
      </section>
    `
    : "";

  const questionClass =
    layout === "coluna_unica"
      ? "questions one-column"
      : layout === "hibrido"
        ? "questions two-columns hybrid"
        : "questions two-columns";

  w.document.write(`<!doctype html>
  <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <title>${escapeHtml(assessment.titulo)}</title>
      <style>
        @page {
          size: A4;
          margin: 13mm 14mm;
        }

        * {
          box-sizing: border-box;
        }

        html, body {
          margin: 0;
          padding: 0;
          background: #fff;
        }

        body {
          font-family: Arial, Helvetica, sans-serif;
          color: #111;
          font-size: 11.2px;
          line-height: 1.35;
        }

        .toolbar {
          max-width: 182mm;
          margin: 10px auto 12px;
        }

        .toolbar button {
          min-height: 34px;
          padding: 0 14px;
          border: 1px solid #aaa;
          border-radius: 5px;
          background: #fff;
          cursor: pointer;
          font: inherit;
        }

        .sheet {
          width: 100%;
          max-width: 182mm;
          margin: 0 auto;
        }

        .cover {
          min-height: 250mm;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
          page-break-after: always;
        }

        .cover .brand {
          font-size: 13px;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .12em;
        }

        .cover h1 {
          max-width: 140mm;
          margin: 18px 0 8px;
          font-size: 27px;
          line-height: 1.15;
          text-transform: uppercase;
        }

        .cover p {
          margin: 3px 0;
          font-size: 14px;
        }

        .exam-header {
          margin-bottom: 12px;
          border-top: 2px solid #111;
          border-bottom: 1px solid #111;
          padding: 8px 0 9px;
        }

        .exam-header-top {
          display: grid;
          grid-template-columns: 1fr auto;
          gap: 14px;
          align-items: start;
        }

        .school {
          font-size: 12px;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .03em;
        }

        .assessment-title {
          margin-top: 2px;
          font-size: 16px;
          font-weight: 800;
          text-transform: uppercase;
          line-height: 1.15;
        }

        .assessment-value {
          white-space: nowrap;
          font-size: 11px;
        }

        .student-fields {
          display: grid;
          grid-template-columns: 2.2fr .55fr 1fr;
          gap: 7px 10px;
          margin-top: 9px;
        }

        .field {
          display: flex;
          align-items: flex-end;
          gap: 5px;
          min-height: 21px;
        }

        .field-label {
          white-space: nowrap;
          font-size: 10.5px;
        }

        .field-line {
          flex: 1;
          min-width: 25px;
          border-bottom: 1px solid #333;
          height: 17px;
        }

        .instructions {
          margin: 0 0 10px;
          font-size: 10.8px;
        }

        /*
         * Duas colunas com fluxo vertical:
         * 1, 2, 3... descem na esquerda e só depois continuam na direita.
         * Não usamos CSS Grid para evitar 1 e 2 lado a lado.
         */
        .questions.two-columns {
          column-count: 2;
          column-gap: 13mm;
          column-rule: 1px solid #d6d6d6;
        }

        .questions.one-column {
          column-count: 1;
        }

        .print-question {
          display: inline-block;
          width: 100%;
          margin: 0 0 10px;
          padding: 0 0 2px;
          vertical-align: top;
          break-inside: avoid-column;
          page-break-inside: avoid;
        }

        .questions.hybrid .print-question.full-width {
          column-span: all;
          display: block;
          margin-top: 5px;
          margin-bottom: 12px;
        }

        .question-title {
          margin-bottom: 5px;
          font-weight: 700;
          line-height: 1.4;
          text-align: justify;
        }

        .question-alt {
          margin: 2.5px 0;
          padding-left: 1px;
          line-height: 1.3;
        }

        .answer-lines {
          margin-top: 7px;
        }

        .answer-lines span {
          display: block;
          height: 23px;
          border-bottom: 1px solid #9b9b9b;
        }

        .answer-key {
          page-break-before: always;
          padding-top: 5px;
        }

        .answer-key h2 {
          margin: 0 0 10px;
          padding-bottom: 5px;
          border-bottom: 1px solid #111;
          font-size: 16px;
          text-transform: uppercase;
        }

        .answer-key-grid {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 8px 12px;
        }

        @media print {
          .toolbar {
            display: none;
          }

          .sheet {
            max-width: none;
          }
        }
      </style>
    </head>

    <body>
      <div class="toolbar">
        <button onclick="window.print()">Imprimir / Salvar em PDF</button>
      </div>

      <div class="sheet">
        ${
          useCover
            ? `<section class="cover">
                <div class="brand">Mentor.Edu</div>
                <h1>${escapeHtml(assessment.titulo)}</h1>
                <p>${escapeHtml(subjectName || "")}</p>
                <p>${escapeHtml(assessment.tipo || "")}</p>
              </section>`
            : ""
        }

        <header class="exam-header">
          <div class="exam-header-top">
            <div>
              <div class="school">Mentor.Edu</div>
              <div class="assessment-title">
                ${escapeHtml(assessment.titulo)}
              </div>
            </div>

            <div class="assessment-value">
              <strong>Valor:</strong> ${assessment.valor ?? 10}
            </div>
          </div>

          <div class="student-fields">
            <div class="field">
              <span class="field-label">Nome:</span>
              <span class="field-line"></span>
            </div>

            <div class="field">
              <span class="field-label">Nº:</span>
              <span class="field-line"></span>
            </div>

            <div class="field">
              <span class="field-label">Turma:</span>
              <span class="field-line"></span>
            </div>

            <div class="field">
              <span class="field-label">Professor:</span>
              <span class="field-line"></span>
            </div>

            <div class="field">
              <span class="field-label">Data:</span>
              <span class="field-line"></span>
            </div>

            <div class="field">
              <span class="field-label">Nota:</span>
              <span class="field-line"></span>
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

        ${key}
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
      <span>
        ${
          published
            ? "Esta avaliação já está lançada no sistema."
            : "A avaliação está salva, mas ainda não foi publicada para os alunos."
        }
      </span>
    </div>
  `;
}

function renderQuestionBuilder(container, assessment, subjectName, questions) {
  const target = container.querySelector("[data-builder]");

  target.innerHTML = surface(`
    ${statusBox(assessment)}

    <div class="assessment-builder-head">
      <div>
        <h3 class="form-title">Questões da avaliação</h3>
        <p>Cada questão adicionada é salva automaticamente no sistema.</p>
      </div>

      <div class="assessment-builder-actions">
        <button type="button" class="mini-button" data-preview>
          Visualizar modelo
        </button>
        <button type="button" class="mini-button" data-save>
          Salvar prova
        </button>
        <button type="button" class="mini-button mini-button--primary" data-publish>
          Publicar avaliação
        </button>
      </div>
    </div>

    <div class="assessment-layout-summary">
      <span><strong>Modelo:</strong> ${
        LAYOUTS.find(([value]) => value === (assessment.modelo_layout || "duas_colunas"))?.[1]
        || "Duas colunas"
      }</span>
      <span><strong>Capa:</strong> ${assessment.usar_capa ? "Sim" : "Não"}</span>
      <span><strong>Gabarito separado:</strong> ${assessment.gabarito_separado ? "Sim" : "Não"}</span>
    </div>

    <form class="inline-form page-section-gap" data-question-form>
      <div class="form-grid">
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

        <label class="form-span-2">
          Enunciado
          <textarea name="enunciado" required rows="3"></textarea>
        </label>

        <label data-alt>A<input name="alternativa_a"></label>
        <label data-alt>B<input name="alternativa_b"></label>
        <label data-alt>C<input name="alternativa_c"></label>
        <label data-alt>D<input name="alternativa_d"></label>

        <label data-alt-e style="display:none">
          E
          <input name="alternativa_e">
        </label>

        <div data-add-e class="assessment-add-e">
          <button type="button" class="mini-button" data-add-e-button>
            + Adicionar o item E
          </button>
          <small>
            Use quando esta questão tiver cinco alternativas.
          </small>
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
          Peso/valor da questão
          <input name="peso" type="number" min="0.1" step="0.1" value="1">
        </label>

        <label>
          Categoria/assunto
          <input name="categoria" placeholder="Ex.: Cinemática">
        </label>

        <label class="form-span-2">
          Explicação para correção (não aparece na prova)
          <textarea name="explicacao" rows="2"></textarea>
        </label>
      </div>

      <div class="form-actions">
        <button class="mini-button mini-button--primary" type="submit">
          Adicionar questão
        </button>
      </div>
    </form>

    <div class="page-section-gap">
      <h3>Prévia das questões</h3>
      <div data-question-list>
        ${
          questions.length
            ? questions.map(questionPreview).join("")
            : emptyBlock(
                "Nenhuma questão",
                "Adicione a primeira questão acima.",
                "book"
              )
        }
      </div>
    </div>
  `);

  const form = target.querySelector("[data-question-form]");
  const type = form.querySelector('[name="tipo"]');
  const altE = form.querySelector("[data-alt-e]");
  const addE = form.querySelector("[data-add-e]");
  const answer = form.querySelector('[name="resposta_correta"]');

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
      el => el.style.display = objetiva ? "" : "none"
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

  target.querySelector("[data-add-e-button]").addEventListener("click", showE);
  type.addEventListener("change", syncType);
  syncType();

  target.querySelector("[data-preview]").addEventListener("click", () => {
    openPrintableAssessment(assessment, subjectName, questions);
  });

  target.querySelector("[data-save]").addEventListener("click", async () => {
    try {
      assessment = await updateAssessment(assessment.id, { ativa: false });
      showToast("Prova salva como rascunho.", "success");
      renderQuestionBuilder(container, assessment, subjectName, questions);
    } catch (error) {
      showToast(error.message || "Não foi possível salvar a prova.", "error");
    }
  });

  target.querySelector("[data-publish]").addEventListener("click", async () => {
    if (!questions.length && !assessment.arquivo) {
      showToast(
        "Adicione pelo menos uma questão ou um arquivo antes de publicar.",
        "error"
      );
      return;
    }

    try {
      assessment = await updateAssessment(assessment.id, { ativa: true });
      showToast("Avaliação publicada no sistema.", "success");
      renderQuestionBuilder(container, assessment, subjectName, questions);
    } catch (error) {
      showToast(
        error.message || "Não foi possível publicar a avaliação.",
        "error"
      );
    }
  });

  form.addEventListener("submit", async event => {
    event.preventDefault();

    const f = new FormData(form);
    const objetiva = f.get("tipo") === "Objetiva";

    try {
      const created = await createAssessmentQuestion(assessment.id, {
        tipo: f.get("tipo"),
        enunciado: String(f.get("enunciado") || "").trim(),
        alternativa_a: objetiva
          ? (String(f.get("alternativa_a") || "").trim() || null)
          : null,
        alternativa_b: objetiva
          ? (String(f.get("alternativa_b") || "").trim() || null)
          : null,
        alternativa_c: objetiva
          ? (String(f.get("alternativa_c") || "").trim() || null)
          : null,
        alternativa_d: objetiva
          ? (String(f.get("alternativa_d") || "").trim() || null)
          : null,
        alternativa_e: objetiva
          ? (String(f.get("alternativa_e") || "").trim() || null)
          : null,
        resposta_correta: objetiva
          ? (f.get("resposta_correta") || null)
          : null,
        explicacao: String(f.get("explicacao") || "").trim() || null,
        dificuldade: f.get("dificuldade"),
        peso: Number(f.get("peso") || 1),
        categoria: String(f.get("categoria") || "").trim() || null
      });

      questions.push(created);
      showToast("Questão adicionada e salva no sistema.", "success");
      renderQuestionBuilder(container, assessment, subjectName, questions);
    } catch (error) {
      showToast(
        error.message || "Não foi possível adicionar a questão.",
        "error"
      );
    }
  });
}

export async function renderTeacherAssessmentCreate(container, navigate) {
  const subs = await getMySubjects();

  container.innerHTML = `
    ${pageHeader(
      "Criar avaliação",
      "Monte a avaliação no Mentor Edu ou publique um arquivo pronto."
    )}

    ${surface(`
      <form class="inline-form" data-form>
        <div class="form-grid">
          <label>
            Disciplina
            <select name="subject_id" required>
              <option value="">Selecione</option>
              ${subs.map(
                s => `<option value="${s.id}">${escapeHtml(s.nome)}</option>`
              ).join("")}
            </select>
          </label>

          <label>
            Tipo
            <select name="tipo" required>
              ${ASSESSMENT_TYPES.map(
                t => `<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`
              ).join("")}
            </select>
          </label>

          <label class="form-span-2">
            Título
            <input
              name="titulo"
              required
              placeholder="Será preenchido automaticamente pela disciplina"
            >
            <small>
              O Mentor Edu sugere o título automaticamente, mas você pode editar.
            </small>
          </label>

          <label class="form-span-2">
            Descrição
            <textarea name="descricao"></textarea>
          </label>

          <label>
            Valor total
            <input
              name="valor"
              type="number"
              step="0.1"
              min="0"
              value="10"
              required
            >
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
              <strong>Modelo da avaliação</strong>
              <small>Escolha como a prova será montada para impressão.</small>
            </div>
          </div>

          <div class="assessment-model-grid">
            ${LAYOUTS.map(([value, label], index) => `
              <label class="assessment-model-option">
                <input
                  type="radio"
                  name="modelo_layout"
                  value="${value}"
                  ${index === 0 ? "checked" : ""}
                >
                <span>
                  <strong>${label}</strong>
                  <small>
                    ${
                      value === "duas_colunas"
                        ? "Ideal para questões objetivas e listas mais compactas."
                        : value === "coluna_unica"
                          ? "Ideal para discursivas, textos e respostas abertas."
                          : "Objetivas em colunas e discursivas ocupando a folha inteira."
                    }
                  </small>
                </span>
              </label>
            `).join("")}
          </div>

          <div class="assessment-extra-options">
            <label>
              <input type="checkbox" name="usar_capa">
              <span>
                <strong>Usar capa</strong>
                <small>Adiciona uma página de abertura antes das questões.</small>
              </span>
            </label>

            <label>
              <input type="checkbox" name="gabarito_separado">
              <span>
                <strong>Gabarito separado</strong>
                <small>Gera uma página de gabarito ao final da impressão.</small>
              </span>
            </label>
          </div>
        </div>

        <div class="assessment-mode-box">
          <strong>Como deseja criar esta avaliação?</strong>

          <div class="assessment-mode-options">
            <label>
              <input type="radio" name="modo" value="sistema" checked>
              Criar no Mentor Edu e adicionar questões
            </label>

            <label>
              <input type="radio" name="modo" value="arquivo">
              Usar um arquivo pronto
            </label>
          </div>
        </div>

        <div data-file-area class="assessment-file-area" style="display:none">
          <label>
            Arquivo pronto da avaliação
            <input
              name="arquivo"
              type="file"
              accept=".pdf,.odt,.doc,.docx,.png,.jpg,.jpeg"
            >
            <small>
              Arquivos aceitos: PDF, ODT, DOC/DOCX e imagens.
            </small>
          </label>
        </div>

        <div class="form-actions" data-create-actions>
          <button
            class="mini-button mini-button--primary"
            type="submit"
          >
            Criar avaliação e adicionar questões
          </button>
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
    if (!titleInput.value.trim() || !titleWasManuallyEdited) {
      titleWasManuallyEdited = false;
    }
    syncSuggestedTitle();
  });

  typeSelect.addEventListener("change", () => {
    if (!titleWasManuallyEdited) syncSuggestedTitle();
  });

  const renderModeActions = () => {
    const modo =
      form.querySelector('[name="modo"]:checked')?.value || "sistema";

    fileArea.style.display = modo === "arquivo" ? "" : "none";

    if (modo === "arquivo") {
      actions.innerHTML = `
        <button class="mini-button" type="button" data-file-draft>
          Salvar arquivo como rascunho
        </button>
        <button
          class="mini-button mini-button--primary"
          type="button"
          data-file-publish
        >
          Publicar arquivo diretamente
        </button>
      `;

      actions.querySelector("[data-file-draft]")
        .addEventListener("click", () => createFromFile(false));

      actions.querySelector("[data-file-publish]")
        .addEventListener("click", () => createFromFile(true));
    } else {
      actions.innerHTML = `
        <button
          class="mini-button mini-button--primary"
          type="submit"
        >
          Criar avaliação e adicionar questões
        </button>
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
      throw new Error("Selecione um arquivo pronto antes de continuar.");
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
      data: f.get("data")
        ? new Date(f.get("data")).toISOString()
        : null,
      semestre: f.get("semestre")
        ? Number(f.get("semestre"))
        : null,
      ano_letivo: f.get("ano_letivo")
        ? Number(f.get("ano_letivo"))
        : null,
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
        published
          ? "Arquivo publicado diretamente no sistema."
          : "Arquivo salvo como rascunho.",
        "success"
      );

      form.querySelectorAll("input,textarea,select,button").forEach(
        el => el.disabled = true
      );

      container.querySelector("[data-builder]").innerHTML = surface(`
        ${statusBox(assessment)}
        <h3>${escapeHtml(assessment.titulo)}</h3>
        <p>
          O arquivo pronto foi
          ${published ? "publicado" : "salvo como rascunho"}.
        </p>
        <p style="color:#64748b">
          ${escapeHtml(assessment.arquivo_nome || "Arquivo anexado")}
        </p>
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

    const modo =
      form.querySelector('[name="modo"]:checked')?.value || "sistema";

    if (modo !== "sistema") return;

    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;

    try {
      const payload = await buildBasePayload(false, false);
      const assessment = await createAssessment(payload);

      showToast(
        "Avaliação criada como rascunho. Agora adicione as questões.",
        "success"
      );

      form.querySelectorAll("input,textarea,select,button").forEach(
        el => el.disabled = true
      );

      const subjectName =
        subs.find(
          s => Number(s.id) === Number(assessment.subject_id)
        )?.nome || "";

      const questions = await getTeacherAssessmentQuestions(
        assessment.id
      ).catch(() => []);

      renderQuestionBuilder(
        container,
        assessment,
        subjectName,
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
