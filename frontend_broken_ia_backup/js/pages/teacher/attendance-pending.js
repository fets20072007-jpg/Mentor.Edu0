import {
  getTeacherPendingAttendance,
  getTeacherClassrooms,
  updateAttendance,
  reviewAttendanceJustification,
} from "../../api/teacher.js";
import { getMySubjects } from "../../api/subjects.js";
import { escapeHtml, formatDateTime } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "../shared/page-ui.js";
import { showToast } from "../../components/toast.js";

export async function renderTeacherAttendancePending(container) {
  const [rows, classrooms, subjects] = await Promise.all([
    getTeacherPendingAttendance(),
    getTeacherClassrooms(),
    getMySubjects(),
  ]);

  const studentMap = new Map();
  const classroomMap = new Map(classrooms.map(c => [Number(c.classroom_id), c.turma]));
  classrooms.forEach(c => (c.alunos || []).forEach(a => studentMap.set(Number(a.id), a.nome)));
  const subjectMap = new Map(subjects.map(s => [Number(s.id), s.nome]));

  container.innerHTML = `${pageHeader(
    "Pendências de frequência",
    "Analise as solicitações enviadas pelos alunos antes de justificar uma falta."
  )}${surface(rows.length ? `<div class="data-table-wrap"><table class="data-table">
    <thead><tr><th>Data</th><th>Aluno</th><th>Turma</th><th>Disciplina</th><th>Situação</th><th>Motivo</th><th>Documento</th><th>Ações</th></tr></thead>
    <tbody>${rows.map(r => {
      const requested = String(r.justificativa_status || "").toLowerCase() === "solicitada";
      return `<tr>
        <td>${formatDateTime(r.data)}</td>
        <td>${escapeHtml(studentMap.get(Number(r.student_id)) || `Aluno #${r.student_id}`)}</td>
        <td>${escapeHtml(classroomMap.get(Number(r.classroom_id)) || `Turma #${r.classroom_id}`)}</td>
        <td>${escapeHtml(subjectMap.get(Number(r.subject_id)) || `Disciplina #${r.subject_id}`)}</td>
        <td>${requested ? statusPill("Solicitação recebida", "warning") : statusPill("Falta pendente", "warning")}</td>
        <td>${r.motivo ? escapeHtml(r.motivo) : "—"}</td>
        <td>${r.arquivo ? `<a class="file-chip" href="${escapeHtml(r.arquivo)}" target="_blank" rel="noopener" download>Abrir / baixar</a>` : "—"}</td>
        <td><div class="row-actions">
          ${requested ? `<button class="mini-button mini-button--primary" data-accept="${r.id}">Aceitar e justificar</button><button class="mini-button mini-button--danger" data-reject="${r.id}">Rejeitar</button>` : `<button class="mini-button" data-confirm="${r.id}">Confirmar falta sem justificativa</button>`}
        </div></td>
      </tr>`;
    }).join("")}</tbody>
  </table></div>` : emptyBlock("Sem pendências", "Nenhuma falta ou solicitação aguardando análise.", "calendar"))}`;

  container.querySelectorAll("[data-confirm]").forEach(b => b.addEventListener("click", async () => {
    try {
      await updateAttendance(Number(b.dataset.confirm), {
        status: "falta_nao_justificada",
        justificada: false,
        motivo: null,
        arquivo: null,
        observacao: "Falta confirmada pelo professor.",
      });
      showToast("Falta confirmada como não justificada.", "success");
      await renderTeacherAttendancePending(container);
    } catch (e) {
      showToast(e.message || "Não foi possível atualizar.", "error");
    }
  }));

  container.querySelectorAll("[data-accept]").forEach(b => b.addEventListener("click", async () => {
    try {
      await reviewAttendanceJustification(Number(b.dataset.accept), { decisao: "aceitar" });
      showToast("Justificativa aceita. A falta agora está justificada.", "success");
      await renderTeacherAttendancePending(container);
    } catch (e) {
      showToast(e.message || "Não foi possível aceitar.", "error");
    }
  }));

  container.querySelectorAll("[data-reject]").forEach(b => b.addEventListener("click", async () => {
    const observacao = window.prompt("Motivo da rejeição (opcional):", "");
    try {
      await reviewAttendanceJustification(Number(b.dataset.reject), { decisao: "rejeitar", observacao: observacao || null });
      showToast("Justificativa rejeitada. A falta ficou como não justificada.", "success");
      await renderTeacherAttendancePending(container);
    } catch (e) {
      showToast(e.message || "Não foi possível rejeitar.", "error");
    }
  }));
}
