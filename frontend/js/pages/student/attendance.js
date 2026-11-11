import { getMyAttendance, getMyAttendanceSummary, justifyAttendance } from "../../api/attendance.js";
import { getMySubjects } from "../../api/subjects.js";
import { escapeHtml, formatDateTime, formatPercent } from "../../core/format.js";
import { pageHeader, surface, metricCard, emptyBlock, statusPill } from "../shared/page-ui.js";
import { showToast } from "../../components/toast.js";

const labels = {
    presente: ["Presente", "success"],
    falta_justificada: ["Falta justificada", "info"],
    falta_nao_justificada: ["Falta não justificada", "danger"],
    falta_pendente: ["Justificativa pendente", "warning"],
};

export async function renderStudentAttendance(container) {
    const [records, summary, subjects] = await Promise.all([getMyAttendance(), getMyAttendanceSummary(), getMySubjects()]);
    const subjectMap = new Map(subjects.map(item => [item.id, item.nome]));

    const render = () => {
        container.innerHTML = `${pageHeader("Frequência", "Acompanhe presenças, faltas e justificativas.")}<div class="metric-grid metric-grid--wide">${metricCard("Presença", formatPercent(summary.percentual_presenca), "users")}${metricCard("Aulas registradas", String(summary.aulas_registradas), "calendar")}${metricCard("Faltas justificadas", String(summary.faltas_justificadas), "check")}${metricCard("Pendentes", String(summary.faltas_pendentes), "clock")}</div>${surface(records.length ? `<div class="timeline-list">${records.map(record => { const [label, tone] = labels[record.status] || [record.status, "neutral"]; return `<article class="timeline-row"><div class="timeline-marker"></div><div class="timeline-body"><div class="timeline-title"><div><strong>${escapeHtml(subjectMap.get(record.subject_id) || `Disciplina #${record.subject_id}`)}</strong><small>${formatDateTime(record.data)}</small></div>${statusPill(label, tone)}</div>${record.motivo ? `<p><strong>Motivo:</strong> ${escapeHtml(record.motivo)}</p>` : ""}${record.observacao ? `<p>${escapeHtml(record.observacao)}</p>` : ""}${record.status === "falta_pendente" ? `<button type="button" class="mini-button mini-button--primary" data-justify="${record.id}">Justificar falta</button>` : ""}</div></article>`; }).join("")}</div>` : emptyBlock("Sem registros de frequência", "Seus registros aparecerão aqui após as chamadas dos professores.", "calendar"))}`;

        container.querySelectorAll("[data-justify]").forEach(button => button.addEventListener("click", async () => {
            const reason = window.prompt("Informe o motivo da justificativa:");
            if (!reason?.trim()) return;
            const observation = window.prompt("Observação adicional (opcional):") || null;
            button.disabled = true;
            try {
                await justifyAttendance(Number(button.dataset.justify), { motivo: reason.trim(), arquivo: null, observacao: observation?.trim() || null });
                showToast("Justificativa enviada com sucesso.");
                await renderStudentAttendance(container);
            } catch (error) {
                showToast(error.message || "Não foi possível justificar a falta.", "error");
                button.disabled = false;
            }
        }));
    };
    render();
}
