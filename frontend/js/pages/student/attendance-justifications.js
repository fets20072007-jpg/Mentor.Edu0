import { getMyAttendance, justifyAttendance } from "../../api/attendance.js";
import { getMySubjects } from "../../api/subjects.js";
import { uploadFile } from "../../api/uploads.js";
import { escapeHtml, formatDateTime } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "../shared/page-ui.js";
import { showToast } from "../../components/toast.js";

function stateInfo(item) {
  const review = String(item.justificativa_status || "").toLowerCase();
  if (review === "solicitada") return { label: "Aguardando análise", tone: "warning" };
  if (review === "aceita" || item.status === "falta_justificada") return { label: "Justificada", tone: "success" };
  if (review === "rejeitada") return { label: "Justificativa rejeitada", tone: "danger" };
  if (item.status === "falta_pendente") return { label: "Pendente", tone: "warning" };
  return { label: "Não justificada", tone: "danger" };
}

export async function renderStudentAttendanceJustifications(container, navigate) {
  const [records, subjects] = await Promise.all([getMyAttendance(), getMySubjects()]);
  const subjectMap = new Map(subjects.map(i => [i.id, i.nome]));
  const absences = records.filter(i => i.status !== "presente");

  container.innerHTML = `${pageHeader(
    "Justificativas",
    "Envie a documentação para análise. A falta só será justificada após aprovação do professor.",
    `<button class="mini-button" data-go-attendance>Ir para frequência</button>`
  )}${surface(absences.length ? `<div class="justification-list">${absences.map(item => {
    const state = stateInfo(item);
    const awaiting = String(item.justificativa_status || "").toLowerCase() === "solicitada";
    const canSubmit = item.status === "falta_pendente" && !awaiting;
    return `<article class="justification-card">
      <header><div><h3>${escapeHtml(subjectMap.get(item.subject_id) || `Disciplina #${item.subject_id}`)}</h3><p>${formatDateTime(item.data)}</p></div>${statusPill(state.label, state.tone)}</header>
      ${awaiting ? `<div class="info-banner info-banner--warning"><strong>Solicitação enviada.</strong><span>O professor ainda precisa analisar seu motivo e o documento anexado.</span></div>` : ""}
      ${item.motivo ? `<p><b>Motivo enviado:</b> ${escapeHtml(item.motivo)}</p>` : ""}
      ${item.arquivo ? `<a class="file-chip" href="${escapeHtml(item.arquivo)}" target="_blank" rel="noopener">Abrir documento enviado</a>` : ""}
      ${item.observacao ? `<p><b>Observação:</b> ${escapeHtml(item.observacao)}</p>` : ""}
      ${canSubmit ? `<form data-justify="${item.id}" class="inline-form justification-form">
        <label>Motivo<textarea name="motivo" rows="3" required placeholder="Explique o motivo da ausência"></textarea></label>
        <label>Anexo <small>(PDF recomendado, também aceita imagem ou documento)</small><input name="arquivo" type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"></label>
        <label>Observação opcional<input name="observacao" placeholder="Informação adicional"></label>
        <button class="mini-button mini-button--primary" type="submit">Enviar para análise</button>
      </form>` : ""}
    </article>`;
  }).join("")}</div>` : emptyBlock("Nenhuma falta registrada", "Não há justificativas para acompanhar neste momento.", "check"))}`;

  container.querySelector("[data-go-attendance]")?.addEventListener("click", () => navigate("attendance"));
  container.querySelectorAll("[data-justify]").forEach(form => form.addEventListener("submit", async e => {
    e.preventDefault();
    const fd = new FormData(form);
    const btn = form.querySelector("button");
    btn.disabled = true;
    try {
      let arquivo = null;
      const file = fd.get("arquivo");
      if (file instanceof File && file.size) arquivo = (await uploadFile(file)).arquivo;
      await justifyAttendance(Number(form.dataset.justify), {
        motivo: String(fd.get("motivo") || "").trim(),
        arquivo,
        observacao: String(fd.get("observacao") || "").trim() || null,
      });
      showToast("Solicitação enviada. Aguarde a análise do professor.", "success");
      await renderStudentAttendanceJustifications(container, navigate);
    } catch (err) {
      btn.disabled = false;
      showToast(err.message || "Não foi possível enviar.", "error");
    }
  }));
}
