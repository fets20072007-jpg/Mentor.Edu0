import { getMyAcademicRecord } from "../../api/academic-record.js";
import { escapeHtml, formatNumber, formatPercent } from "../../core/format.js";
import { pageHeader, surface, metricCard, emptyBlock, statusPill } from "../shared/page-ui.js";

export async function renderStudentRecord(container) {
    const record = await getMyAcademicRecord();
    const subjects = record.disciplinas || [];
    const average = subjects.length ? subjects.reduce((sum, item) => sum + Number(item.media || 0), 0) / subjects.length : 0;
    const attendance = subjects.length ? subjects.reduce((sum, item) => sum + Number(item.frequencia || 0), 0) / subjects.length : 0;
    container.innerHTML = `${pageHeader("Histórico acadêmico", `${record.aluno || "Aluno"} · ${record.turma || "Turma não informada"}`)}<div class="metric-grid">${metricCard("Média geral", subjects.length ? formatNumber(average, 1) : "—", "chart")}${metricCard("Frequência média", subjects.length ? formatPercent(attendance) : "—", "calendar")}${metricCard("Disciplinas", String(subjects.length), "book")}</div>${surface(subjects.length ? `<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Disciplina</th><th>Média</th><th>Frequência</th><th>Situação</th></tr></thead><tbody>${subjects.map(item => { const situation = String(item.situacao || ""); const tone = /aprov|satisf|regular/i.test(situation) ? "success" : /recuper|aten/i.test(situation) ? "warning" : /reprov|insuf/i.test(situation) ? "danger" : "neutral"; return `<tr><td><strong>${escapeHtml(item.disciplina)}</strong></td><td>${formatNumber(item.media, 1)}</td><td>${formatPercent(item.frequencia)}</td><td>${statusPill(situation || "—", tone)}</td></tr>`; }).join("")}</tbody></table></div>` : emptyBlock("Histórico ainda vazio", "Ainda não há dados acadêmicos consolidados para exibir.", "school"))}`;
}
