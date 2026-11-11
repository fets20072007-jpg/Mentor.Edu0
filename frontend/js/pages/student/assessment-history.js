import { getMyAssessmentHistory } from "../../api/assessments.js";
import { getMySubjects } from "../../api/subjects.js";
import { escapeHtml, formatNumber, formatPercent } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "../shared/page-ui.js";

export async function renderStudentAssessmentHistory(container) {
    const [history, subjects] = await Promise.all([getMyAssessmentHistory(), getMySubjects()]);
    const subjectMap = new Map(subjects.map(item => [item.id, item.nome]));
    container.innerHTML = `${pageHeader("Histórico de avaliações", "Resultados consolidados das avaliações já concluídas.")}${surface(history.length ? `<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Avaliação</th><th>Disciplina</th><th>Tipo</th><th>Nota</th><th>Percentual</th><th>Desempenho</th></tr></thead><tbody>${history.map(item => { const status = String(item.status_desempenho || ""); const tone = /excel|bom|alto|satisf/i.test(status) ? "success" : /aten|médio|medio|regular/i.test(status) ? "warning" : /baixo|insuf/i.test(status) ? "danger" : "neutral"; return `<tr><td><strong>${escapeHtml(item.titulo)}</strong></td><td>${escapeHtml(subjectMap.get(item.subject_id) || `#${item.subject_id}`)}</td><td>${escapeHtml(item.tipo)}</td><td>${formatNumber(item.nota_final, 1)}</td><td>${formatPercent(item.percentual)}</td><td>${statusPill(status || "—", tone)}</td></tr>`; }).join("")}</tbody></table></div>` : emptyBlock("Histórico ainda vazio", "Resultados concluídos aparecerão aqui após a liberação pelo professor.", "clipboard"))}`;
}
