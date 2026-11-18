import {
    listAssessments,
    getAssessmentQuestions,
    getAssessmentAvailability,
    getAssessmentResult,
    getAssessmentSubmission,
    getAssessmentAnswerKey,
} from "../../api/assessments.js";
import { getMyAnswers, answerQuestion } from "../../api/answers.js";
import { getMySubjects } from "../../api/subjects.js";
import { escapeHtml, formatDateTime, formatNumber } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "../shared/page-ui.js";
import { showToast } from "../../components/toast.js";

function availabilityLabel(info) {
    if (!info) return ["Consultar", "neutral"];
    if (info.pode_responder) return ["Disponível", "success"];
    const status = String(info.status || "").toLowerCase();
    if (status.includes("agend")) return ["Agendada", "info"];
    if (status.includes("encerr") || status.includes("fech")) return ["Encerrada", "neutral"];
    return [info.status || "Indisponível", "warning"];
}

function questionInput(question, existing) {
    if (existing) {
        return `<div class="answered-box"><strong>Resposta enviada</strong><p>${escapeHtml(existing.resposta)}</p></div>`;
    }
    if (String(question.tipo || "").toLowerCase().includes("objet")) {
        const options = ["a","b","c","d"].map(letter => [letter.toUpperCase(), question[`alternativa_${letter}`]]).filter(([,text]) => text);
        return `<div class="answer-options">${options.map(([letter,text]) => `<label><input type="radio" name="question-${question.id}" value="${letter}"><span><b>${letter}</b>${escapeHtml(text)}</span></label>`).join("")}</div>`;
    }
    return `<textarea class="answer-textarea" rows="4" data-answer-text="${question.id}" placeholder="Digite sua resposta..."></textarea>`;
}

export async function renderStudentAssessments(container) {
    const [assessments, subjects, answers] = await Promise.all([listAssessments(), getMySubjects(), getMyAnswers()]);
    const subjectMap = new Map(subjects.map(item => [item.id, item.nome]));
    const answerMap = new Map(answers.map(item => [item.question_id, item]));
    const availabilityPairs = await Promise.all(assessments.map(async item => {
        try { return [item.id, await getAssessmentAvailability(item.id)]; }
        catch { return [item.id, null]; }
    }));
    const availabilityMap = new Map(availabilityPairs);

    const listMarkup = assessments.length ? `<div class="assessment-list">${assessments.map(item => {
        const availability = availabilityMap.get(item.id);
        const [label, tone] = availabilityLabel(availability);
        return `<article class="assessment-card"><div class="assessment-card-main"><div class="assessment-card-top"><span class="entity-card-kicker">${escapeHtml(subjectMap.get(item.subject_id) || `Disciplina #${item.subject_id}`)}</span>${statusPill(label, tone)}</div><h3>${escapeHtml(item.titulo)}</h3><p>${escapeHtml(item.descricao || "Sem descrição.")}</p><div class="assessment-meta"><span>${escapeHtml(item.tipo)}</span><span>Valor: ${formatNumber(item.valor, 1)}</span>${item.data ? `<span>${formatDateTime(item.data)}</span>` : ""}</div></div><button type="button" class="mini-button mini-button--primary" data-open-assessment="${item.id}">Ver</button></article>`;
    }).join("")}</div>` : emptyBlock("Nenhuma avaliação encontrada", "Quando houver avaliações vinculadas à sua turma, elas aparecerão aqui.", "clipboard");

    container.innerHTML = `${pageHeader("Avaliações", "Consulte avaliações, prazos e respostas em um único lugar.")}${surface(listMarkup)}<div class="assessment-detail-host" data-assessment-detail></div>`;

    container.querySelectorAll("[data-open-assessment]").forEach(button => button.addEventListener("click", async () => {
        const id = Number(button.dataset.openAssessment);
        const assessment = assessments.find(item => item.id === id);
        const availability = availabilityMap.get(id) || await getAssessmentAvailability(id);
        const host = container.querySelector("[data-assessment-detail]");
        host.innerHTML = `<div class="page-loading"><span class="spinner"></span><p>Carregando avaliação...</p></div>`;
        host.scrollIntoView({ behavior: "smooth", block: "start" });
        try {
            const questions = availability.prova_liberada || availability.pode_responder ? await getAssessmentQuestions(id) : [];
            let result = null, submission = [], answerKey = [];
            if (availability.resultado_liberado) { try { result = await getAssessmentResult(id); } catch {} }
            if (availability.prova_liberada) { try { submission = await getAssessmentSubmission(id); } catch {} }
            if (availability.gabarito_liberado) { try { answerKey = await getAssessmentAnswerKey(id); } catch {} }

            host.innerHTML = `<section class="content-surface assessment-detail"><div class="assessment-detail-head"><div><span class="entity-card-kicker">${escapeHtml(subjectMap.get(assessment.subject_id) || "Disciplina")}</span><h2>${escapeHtml(assessment.titulo)}</h2><p>${escapeHtml(assessment.descricao || "")}</p></div><button type="button" class="mini-button" data-close-assessment>Fechar</button></div><div class="detail-facts"><div><small>Status</small><strong>${escapeHtml(availability.status)}</strong></div><div><small>Abertura</small><strong>${formatDateTime(availability.data_abertura)}</strong></div><div><small>Encerramento</small><strong>${formatDateTime(availability.data_encerramento)}</strong></div>${result ? `<div><small>Resultado</small><strong>${formatNumber(result.nota_final, 1)} / ${formatNumber(assessment.valor, 1)}</strong></div>` : ""}</div>${availability.pode_responder && questions.length ? `<div class="question-stack">${questions.map((question,index) => `<article class="question-card" data-question-card="${question.id}"><div class="question-number">${index + 1}</div><div class="question-content"><div class="question-tags"><span>${escapeHtml(question.dificuldade)}</span><span>Peso ${formatNumber(question.peso, 1)}</span></div><h3>${escapeHtml(question.enunciado)}</h3>${questionInput(question, answerMap.get(question.id))}${answerMap.has(question.id) ? "" : `<button type="button" class="mini-button mini-button--primary" data-submit-answer="${question.id}">Enviar resposta</button>`}</div></article>`).join("")}</div>` : !availability.pode_responder ? `<div class="inline-alert"><strong>Esta avaliação não está aberta para respostas.</strong><p>O status atual é “${escapeHtml(availability.status)}”.</p></div>` : emptyBlock("Sem questões", "A avaliação ainda não possui questões disponíveis.", "clipboard")}${submission.length ? `<div class="subsection"><h3>Prova respondida</h3><div class="compact-list">${submission.map(item => `<article class="compact-row"><div><strong>${escapeHtml(item.enunciado)}</strong><p>${escapeHtml(item.resposta || "Sem resposta")}</p></div></article>`).join("")}</div></div>` : ""}${answerKey.length ? `<div class="subsection"><h3>Gabarito liberado</h3><div class="compact-list">${answerKey.map(item => `<article class="compact-row"><div><strong>${escapeHtml(item.enunciado)}</strong><p><b>Resposta:</b> ${escapeHtml(item.resposta_correta || "—")}${item.explicacao ? `<br>${escapeHtml(item.explicacao)}` : ""}</p></div></article>`).join("")}</div></div>` : ""}</section>`;

            host.querySelector("[data-close-assessment]")?.addEventListener("click", () => { host.innerHTML = ""; });
            host.querySelectorAll("[data-submit-answer]").forEach(submit => submit.addEventListener("click", async () => {
                const questionId = Number(submit.dataset.submitAnswer);
                const question = questions.find(item => item.id === questionId);
                let resposta = "";
                if (String(question.tipo || "").toLowerCase().includes("objet")) {
                    resposta = host.querySelector(`input[name="question-${questionId}"]:checked`)?.value || "";
                } else {
                    resposta = host.querySelector(`[data-answer-text="${questionId}"]`)?.value?.trim() || "";
                }
                if (!resposta) return showToast("Informe uma resposta antes de enviar.", "error");
                submit.disabled = true;
                try {
                    const saved = await answerQuestion(questionId, { resposta, tempo_resposta: null });
                    answerMap.set(questionId, saved);
                    const card = host.querySelector(`[data-question-card="${questionId}"] .question-content`);
                    card.querySelector(".answer-options, .answer-textarea")?.remove();
                    submit.remove();
                    card.insertAdjacentHTML("beforeend", `<div class="answered-box"><strong>Resposta enviada</strong><p>${escapeHtml(saved.resposta)}</p></div>`);
                    showToast("Resposta registrada.");
                } catch (error) {
                    submit.disabled = false;
                    showToast(error.message || "Não foi possível enviar a resposta.", "error");
                }
            }));
        } catch (error) {
            host.innerHTML = `<div class="inline-alert inline-alert--error"><strong>Não foi possível abrir a avaliação.</strong><p>${escapeHtml(error.message || "Tente novamente.")}</p></div>`;
        }
    }));
}
