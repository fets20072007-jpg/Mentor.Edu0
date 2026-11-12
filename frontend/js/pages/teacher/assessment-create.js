import { getMySubjects } from "../../api/subjects.js";
import { createAssessment, createAssessmentQuestion, getTeacherAssessmentQuestions } from "../../api/teacher.js";
import { uploadFile } from "../../api/uploads.js";
import { escapeHtml } from "../../core/format.js";
import { pageHeader,surface,emptyBlock } from "../shared/page-ui.js";
import { showToast } from "../../components/toast.js";

const ASSESSMENT_TYPES = ["Prova","Trabalho","Atividade avaliativa","Exercício"];

function questionPreview(q, index) {
  const alternatives = ["a","b","c","d"]
    .map(letter => q[`alternativa_${letter}`] ? `<div style="margin:5px 0">${letter.toUpperCase()}) ${escapeHtml(q[`alternativa_${letter}`])}</div>` : "")
    .join("");
  return `<div style="padding:14px 0;border-bottom:1px solid #e5e7eb">
    <strong>${index + 1}. ${escapeHtml(q.enunciado || "")}</strong>
    ${alternatives}
    <small style="display:block;margin-top:8px;color:#64748b">Valor/peso: ${q.peso ?? 1}</small>
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
  w.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(assessment.titulo)}</title>
    <style>
      body{font-family:Arial,sans-serif;max-width:850px;margin:36px auto;padding:0 30px;color:#111}
      .head{text-align:center;border-bottom:2px solid #111;padding-bottom:18px;margin-bottom:24px}
      .meta{display:flex;gap:24px;flex-wrap:wrap;margin:16px 0 28px}
      .line{display:inline-block;min-width:220px;border-bottom:1px solid #111;height:18px}
      button{margin:20px 0;padding:10px 16px}
      @media print{button{display:none}}
    </style></head><body>
    <div class="head"><h1>${escapeHtml(assessment.titulo)}</h1><div>${escapeHtml(subjectName || "")} · ${escapeHtml(assessment.tipo || "")}</div></div>
    <div class="meta"><div>Aluno: <span class="line"></span></div><div>Turma: <span class="line"></span></div><div>Data: <span class="line"></span></div></div>
    ${assessment.descricao ? `<p>${escapeHtml(assessment.descricao)}</p>` : ""}
    <main>${body}</main>
    <button onclick="window.print()">Imprimir / Salvar em PDF</button>
    </body></html>`);
  w.document.close();
}

function renderQuestionBuilder(container, assessment, subjectName, questions) {
  const target = container.querySelector("[data-builder]");
  target.innerHTML = surface(`
    <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap">
      <div><h3 class="form-title" style="margin-bottom:4px">Questões da avaliação</h3>
      <p style="margin:0;color:#64748b">Cada questão adicionada já entra no modelo da prova.</p></div>
      <button type="button" class="mini-button" data-preview>Visualizar prova pronta</button>
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
        <label class="form-span-2">Enunciado<textarea name="enunciado" required rows="3"></textarea></label>
        <label data-alt>A<input name="alternativa_a"></label>
        <label data-alt>B<input name="alternativa_b"></label>
        <label data-alt>C<input name="alternativa_c"></label>
        <label data-alt>D<input name="alternativa_d"></label>
        <label data-answer>Resposta correta
          <select name="resposta_correta">
            <option value="">Selecione</option><option>A</option><option>B</option><option>C</option><option>D</option>
          </select>
        </label>
        <label>Peso/valor da questão<input name="peso" type="number" min="0.1" step="0.1" value="1"></label>
        <label>Categoria/assunto<input name="categoria" placeholder="Ex.: Cinemática"></label>
        <label class="form-span-2">Explicação para correção (não aparece na prova)<textarea name="explicacao" rows="2"></textarea></label>
      </div>
      <div class="form-actions"><button class="mini-button mini-button--primary" type="submit">Adicionar questão</button></div>
    </form>

    <div class="page-section-gap">
      <h3>Prévia das questões</h3>
      <div data-question-list>${questions.length ? questions.map(questionPreview).join("") : emptyBlock("Nenhuma questão","Adicione a primeira questão acima.","book")}</div>
    </div>
  `);

  const form = target.querySelector("[data-question-form]");
  const type = form.querySelector('[name="tipo"]');
  const syncType = () => {
    const objetiva = type.value === "Objetiva";
    form.querySelectorAll("[data-alt],[data-answer]").forEach(el => el.style.display = objetiva ? "" : "none");
  };
  type.addEventListener("change", syncType);
  syncType();

  target.querySelector("[data-preview]").addEventListener("click", () => openPrintableAssessment(assessment, subjectName, questions));

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
      showToast("Questão adicionada à avaliação.","success");
      renderQuestionBuilder(container, assessment, subjectName, questions);
    } catch (error) {
      showToast(error.message || "Não foi possível adicionar a questão.","error");
    }
  });
}

export async function renderTeacherAssessmentCreate(container,navigate){
  const subs=await getMySubjects();
  container.innerHTML=`${pageHeader("Criar avaliação","Crie a avaliação e monte as questões na mesma tela.")}${surface(`
    <form class="inline-form" data-form>
      <label>Título<input name="titulo" required></label>
      <label>Descrição<textarea name="descricao"></textarea></label>
      <div class="form-grid">
        <label>Tipo
          <select name="tipo" required>
            ${ASSESSMENT_TYPES.map(t=>`<option value="${escapeHtml(t)}">${escapeHtml(t)}</option>`).join("")}
          </select>
        </label>
        <label>Valor total<input name="valor" type="number" step="0.1" min="0" value="10" required></label>
        <label>Disciplina<select name="subject_id" required><option value="">Selecione</option>${subs.map(s=>`<option value="${s.id}">${escapeHtml(s.nome)}</option>`).join('')}</select></label>
        <label>Data<input name="data" type="datetime-local"></label>
        <label>Semestre<input name="semestre" type="number" min="1" max="2"></label>
        <label>Ano letivo<input name="ano_letivo" type="number" min="2000" max="2100"></label>
        <label class="form-span-2">Anexar arquivo de apoio
          <input name="arquivo" type="file" accept=".pdf,.doc,.docx,.png,.jpg,.jpeg">
          <small>PDF é recomendado. O anexo ficará vinculado à avaliação.</small>
        </label>
      </div>
      <div class="form-actions"><button class="mini-button mini-button--primary" type="submit">Criar avaliação e adicionar questões</button></div>
    </form>`) }
    <div data-builder></div>`;

  container.querySelector('[data-form]').addEventListener('submit',async e=>{
    e.preventDefault();
    const form=e.currentTarget;
    const f=new FormData(form);
    const button=form.querySelector('button[type="submit"]');
    button.disabled=true;
    try{
      let arquivo=null, arquivo_nome=null;
      const file=f.get("arquivo");
      if(file && file.size){
        const uploaded=await uploadFile(file);
        arquivo=uploaded.arquivo;
        arquivo_nome=uploaded.nome_original || file.name;
      }
      const assessment=await createAssessment({
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
        ativa:true
      });
      showToast('Avaliação criada. Agora adicione as questões.','success');
      form.querySelectorAll("input,textarea,select,button").forEach(el=>el.disabled=true);
      const subjectName=subs.find(s=>Number(s.id)===Number(assessment.subject_id))?.nome || "";
      const questions=await getTeacherAssessmentQuestions(assessment.id).catch(()=>[]);
      renderQuestionBuilder(container,assessment,subjectName,questions);
    }catch(error){
      button.disabled=false;
      showToast(error.message || 'Não foi possível criar a avaliação.','error');
    }
  });
}
