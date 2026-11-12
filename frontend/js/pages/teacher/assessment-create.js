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

const ASSESSMENT_TYPES = ["Prova","Trabalho","Atividade avaliativa","Exercício"];

function questionPreview(q, index) {
  const alternatives = ["a","b","c","d"]
    .map(letter => q[`alternativa_${letter}`]
      ? `<div style="margin:5px 0">${letter.toUpperCase()}) ${escapeHtml(q[`alternativa_${letter}`])}</div>`
      : "")
    .join("");

  return `<div style="padding:14px 0;border-bottom:1px solid #e5e7eb">
    <strong>${index + 1}. ${escapeHtml(q.enunciado || "")}</strong>
    ${alternatives}
    <small style="display:block;margin-top:8px;color:#64748b">
      Valor/peso: ${q.peso ?? 1}
    </small>
  </div>`;
}

function openPrintableAssessment(assessment, subjectName, questions) {
  const w = window.open("", "_blank");
  if (!w) {
    showToast("Permita pop-ups para visualizar a prova.","error");
    return;
  }

  const body = questions.length
    ? questions.map(questionPreview).join("")
    : "<p>Nenhuma questão adicionada ainda.</p>";

  w.document.write(`<!doctype html>
  <html>
    <head>
      <meta charset="utf-8">
      <title>${escapeHtml(assessment.titulo)}</title>
      <style>
        body{font-family:Arial,sans-serif;max-width:850px;margin:36px auto;padding:0 30px;color:#111}
        .head{text-align:center;border-bottom:2px solid #111;padding-bottom:18px;margin-bottom:24px}
        .meta{display:flex;gap:24px;flex-wrap:wrap;margin:16px 0 28px}
        .line{display:inline-block;min-width:220px;border-bottom:1px solid #111;height:18px}
        button{margin:20px 8px 20px 0;padding:10px 16px}
        @media print{button{display:none}}
      </style>
    </head>
    <body>
      <div class="head">
        <h1>${escapeHtml(assessment.titulo)}</h1>
        <div>${escapeHtml(subjectName || "")} · ${escapeHtml(assessment.tipo || "")}</div>
      </div>
      <div class="meta">
        <div>Aluno: <span class="line"></span></div>
        <div>Turma: <span class="line"></span></div>
        <div>Data: <span class="line"></span></div>
      </div>
      ${assessment.descricao ? `<p>${escapeHtml(assessment.descricao)}</p>` : ""}
      <main>${body}</main>
      <button onclick="window.print()">Imprimir / Salvar em PDF</button>
    </body>
  </html>`);

  w.document.close();
}

function statusBox(assessment) {
  const published = Boolean(assessment.ativa);
  return `<div style="
      padding:12px 14px;
      border-radius:12px;
      margin:14px 0;
      background:${published ? "#ecfdf5" : "#fff7ed"};
      border:1px solid ${published ? "#a7f3d0" : "#fed7aa"};
    ">
      <strong>Status: ${published ? "Publicado" : "Rascunho"}</strong>
      <div style="font-size:13px;margin-top:4px;color:#64748b">
        ${published
          ? "Esta avaliação já está lançada no sistema."
          : "A avaliação está salva, mas ainda não foi publicada para os alunos."}
      </div>
    </div>`;
}

function renderQuestionBuilder(container, assessment, subjectName, questions) {
  const target = container.querySelector("[data-builder]");

  target.innerHTML = surface(`
    ${statusBox(assessment)}

    <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap">
      <div>
        <h3 class="form-title" style="margin-bottom:4px">Questões da avaliação</h3>
        <p style="margin:0;color:#64748b">
          Cada questão adicionada é salva automaticamente no sistema.
        </p>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <button type="button" class="mini-button" data-preview>
          Visualizar prova pronta
        </button>
        <button type="button" class="mini-button" data-save>
          Salvar prova
        </button>
        <button type="button" class="mini-button mini-button--primary" data-publish>
          Publicar avaliação
        </button>
      </div>
    </div>

    <form class="inline-form page-section-gap" data-question-form>
      <div class="form-grid">
        <label>Tipo da questão
          <select name="tipo">
            <option value="Objetiva">Objetiva</option>
            <option value="Discursiva">Discursiva</option>
          </select>
        </label>

        <label>Dificuldade
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

        <label data-answer>
          Resposta correta
          <select name="resposta_correta">
            <option value="">Selecione</option>
            <option>A</option><option>B</option><option>C</option><option>D</option>
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
        ${questions.length
          ? questions.map(questionPreview).join("")
          : emptyBlock("Nenhuma questão","Adicione a primeira questão acima.","book")}
      </div>
    </div>
  `);

  const form = target.querySelector("[data-question-form]");
  const type = form.querySelector('[name="tipo"]');

  const syncType = () => {
    const objetiva = type.value === "Objetiva";
    form.querySelectorAll("[data-alt],[data-answer]").forEach(
      el => el.style.display = objetiva ? "" : "none"
    );
  };

  type.addEventListener("change", syncType);
  syncType();

  target.querySelector("[data-preview]").addEventListener("click", () => {
    openPrintableAssessment(assessment, subjectName, questions);
  });

  target.querySelector("[data-save]").addEventListener("click", async () => {
    try {
      assessment = await updateAssessment(assessment.id, { ativa: false });
      showToast("Prova salva como rascunho.","success");
      renderQuestionBuilder(container, assessment, subjectName, questions);
    } catch (error) {
      showToast(error.message || "Não foi possível salvar a prova.","error");
    }
  });

  target.querySelector("[data-publish]").addEventListener("click", async () => {
    if (!questions.length && !assessment.arquivo) {
      showToast("Adicione pelo menos uma questão ou um arquivo antes de publicar.","error");
      return;
    }

    try {
      assessment = await updateAssessment(assessment.id, { ativa: true });
      showToast("Avaliação publicada no sistema.","success");
      renderQuestionBuilder(container, assessment, subjectName, questions);
    } catch (error) {
      showToast(error.message || "Não foi possível publicar a avaliação.","error");
    }
  });

  form.addEventListener("submit", async e => {
    e.preventDefault();
    const f = new FormData(form);
    const objetiva = f.get("tipo") === "Objetiva";

    try {
      const created = await createAssessmentQuestion(assessment.id,{
        tipo:f.get("tipo"),
        enunciado:String(f.get("enunciado")||"").trim(),
        alternativa_a:objetiva ? (String(f.get("alternativa_a")||"").trim() || null) : null,
        alternativa_b:objetiva ? (String(f.get("alternativa_b")||"").trim() || null) : null,
        alternativa_c:objetiva ? (String(f.get("alternativa_c")||"").trim() || null) : null,
        alternativa_d:objetiva ? (String(f.get("alternativa_d")||"").trim() || null) : null,
        resposta_correta:objetiva ? (f.get("resposta_correta") || null) : null,
        explicacao:String(f.get("explicacao")||"").trim() || null,
        dificuldade:f.get("dificuldade"),
        peso:Number(f.get("peso")||1),
        categoria:String(f.get("categoria")||"").trim() || null
      });

      questions.push(created);
      showToast("Questão adicionada e salva no sistema.","success");
      renderQuestionBuilder(container, assessment, subjectName, questions);
    } catch (error) {
      showToast(error.message || "Não foi possível adicionar a questão.","error");
    }
  });
}

export async function renderTeacherAssessmentCreate(container,navigate){
  const subs=await getMySubjects();

  container.innerHTML=`
    ${pageHeader(
      "Criar avaliação",
      "Monte a avaliação no Mentor Edu ou publique um arquivo pronto."
    )}

    ${surface(`
      <form class="inline-form" data-form>
        <label>
          Título
          <input name="titulo" required>
        </label>

        <label>
          Descrição
          <textarea name="descricao"></textarea>
        </label>

        <div class="form-grid">
          <label>
            Tipo
            <select name="tipo" required>
              ${ASSESSMENT_TYPES
                .map(t=>`<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`)
                .join("")}
            </select>
          </label>

          <label>
            Valor total
            <input name="valor" type="number" step="0.1" min="0" value="10" required>
          </label>

          <label>
            Disciplina
            <select name="subject_id" required>
              <option value="">Selecione</option>
              ${subs.map(s=>`<option value="${s.id}">${escapeHtml(s.nome)}</option>`).join('')}
            </select>
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

        <div style="margin-top:18px;padding:16px;border:1px solid #dbe2ea;border-radius:14px">
          <strong>Como deseja criar esta avaliação?</strong>

          <div style="display:flex;gap:20px;flex-wrap:wrap;margin-top:12px">
            <label style="display:flex;gap:8px;align-items:center">
              <input type="radio" name="modo" value="sistema" checked>
              Criar no Mentor Edu e adicionar questões
            </label>

            <label style="display:flex;gap:8px;align-items:center">
              <input type="radio" name="modo" value="arquivo">
              Usar um arquivo pronto
            </label>
          </div>
        </div>

        <div data-file-area style="margin-top:16px;display:none">
          <label>
            Arquivo pronto da avaliação
            <input name="arquivo" type="file" accept=".pdf,.doc,.docx,.png,.jpg,.jpeg">
            <small>
              Use esta opção quando o professor já possuir a prova, atividade,
              trabalho ou exercício pronto.
            </small>
          </label>
        </div>

        <div class="form-actions" data-create-actions>
          <button class="mini-button mini-button--primary" type="submit" data-create-system>
            Criar avaliação e adicionar questões
          </button>
        </div>
      </form>
    `)}

    <div data-builder></div>
  `;

  const form = container.querySelector('[data-form]');
  const fileArea = form.querySelector("[data-file-area]");
  const actions = form.querySelector("[data-create-actions]");

  const renderModeActions = () => {
    const modo = form.querySelector('[name="modo"]:checked')?.value || "sistema";
    fileArea.style.display = modo === "arquivo" ? "" : "none";

    if (modo === "arquivo") {
      actions.innerHTML = `
        <button class="mini-button" type="button" data-file-draft>
          Salvar arquivo como rascunho
        </button>
        <button class="mini-button mini-button--primary" type="button" data-file-publish>
          Publicar arquivo diretamente
        </button>
      `;

      actions.querySelector("[data-file-draft]").addEventListener(
        "click",
        () => createFromFile(false)
      );
      actions.querySelector("[data-file-publish]").addEventListener(
        "click",
        () => createFromFile(true)
      );
    } else {
      actions.innerHTML = `
        <button class="mini-button mini-button--primary" type="submit">
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
    let arquivo=null;
    let arquivo_nome=null;
    const file=f.get("arquivo");

    if (requireFile && (!file || !file.size)) {
      throw new Error("Selecione um arquivo pronto antes de continuar.");
    }

    if(file && file.size){
      const uploaded=await uploadFile(file);
      arquivo=uploaded.arquivo;
      arquivo_nome=uploaded.nome_original || file.name;
    }

    return {
      titulo:f.get('titulo'),
      descricao:f.get('descricao')||null,
      tipo:f.get('tipo'),
      valor:Number(f.get('valor')),
      subject_id:Number(f.get('subject_id')),
      data:f.get('data')?new Date(f.get('data')).toISOString():null,
      semestre:f.get('semestre')?Number(f.get('semestre')):null,
      ano_letivo:f.get('ano_letivo')?Number(f.get('ano_letivo')):null,
      arquivo,
      arquivo_nome,
      ativa:published
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
        el => el.disabled=true
      );

      container.querySelector("[data-builder]").innerHTML = surface(`
        ${statusBox(assessment)}
        <h3>${escapeHtml(assessment.titulo)}</h3>
        <p>
          O arquivo pronto foi ${published ? "publicado" : "salvo como rascunho"}.
        </p>
        <p style="color:#64748b">
          ${escapeHtml(assessment.arquivo_nome || "Arquivo anexado")}
        </p>
      `);
    } catch (error) {
      showToast(error.message || "Não foi possível salvar o arquivo.","error");
    }
  }

  form.addEventListener('submit',async e=>{
    e.preventDefault();

    const modo=form.querySelector('[name="modo"]:checked')?.value || "sistema";
    if (modo !== "sistema") return;

    const button=form.querySelector('button[type="submit"]');
    button.disabled=true;

    try{
      const payload=await buildBasePayload(false, false);
      const assessment=await createAssessment(payload);

      showToast(
        "Avaliação criada como rascunho. Agora adicione as questões.",
        "success"
      );

      form.querySelectorAll("input,textarea,select,button").forEach(
        el=>el.disabled=true
      );

      const subjectName=subs.find(
        s=>Number(s.id)===Number(assessment.subject_id)
      )?.nome || "";

      const questions=await getTeacherAssessmentQuestions(
        assessment.id
      ).catch(()=>[]);

      renderQuestionBuilder(
        container,
        assessment,
        subjectName,
        questions
      );
    }catch(error){
      button.disabled=false;
      showToast(
        error.message || 'Não foi possível criar a avaliação.',
        'error'
      );
    }
  });
}
