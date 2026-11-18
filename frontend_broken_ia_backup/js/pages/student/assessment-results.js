import { getMyAssessmentHistory, getMyAssessmentSummary, getMySubjectAssessmentSummary } from "../../api/assessments.js";
import { getMySubjects } from "../../api/subjects.js";
import { escapeHtml, formatNumber, formatPercent } from "../../core/format.js";
import { pageHeader, surface, metricCard, emptyBlock } from "../shared/page-ui.js";

export async function renderStudentAssessmentResults(container) {
    const [history, summary, bySubject, subjects] = await Promise.all([
        getMyAssessmentHistory(),
        getMyAssessmentSummary().catch(() => null),
        getMySubjectAssessmentSummary().catch(() => []),
        getMySubjects(),
    ]);
    const subjectMap = new Map(subjects.map(item => [item.id, item.nome]));
    const summaryMetrics = summary ? `<div class="metric-grid">${metricCard("Avaliações", String(summary.avaliacoes_realizadas ?? history.length), "clipboard")}${metricCard("Média", summary.media_geral != null ? formatNumber(summary.media_geral, 1) : "—", "chart")}${metricCard("Desempenho", summary.percentual_medio != null ? formatPercent(summary.percentual_medio) : escapeHtml(summary.status_geral || "—"), "activity")}</div>` : "";
    container.innerHTML = `${pageHeader("Resultados das avaliações", "Uma visão simples do seu desempenho por avaliação e disciplina.")}${summaryMetrics}${surface(bySubject.length ? `<div class="entity-grid">${bySubject.map(item => `<article class="entity-card"><div class="entity-card-main"><span class="entity-card-kicker">Disciplina</span><h3>${escapeHtml(subjectMap.get(item.subject_id) || `Disciplina #${item.subject_id}`)}</h3><p>${item.media != null ? `Média ${formatNumber(item.media, 1)}` : ""}${item.percentual_medio != null ? ` · ${formatPercent(item.percentual_medio)}` : ""}</p></div></article>`).join("")}</div>` : history.length ? `<div class="compact-list">${history.map(item => `<article class="compact-row"><div><strong>${escapeHtml(item.titulo)}</strong><p>${formatNumber(item.nota_final, 1)} · ${formatPercent(item.percentual)}</p></div><span class="soft-label">${escapeHtml(item.status_desempenho)}</span></article>`).join("")}</div>` : emptyBlock("Sem resultados liberados", "Assim que os resultados forem liberados, eles aparecerão nesta página.", "chart"))}`;
}
