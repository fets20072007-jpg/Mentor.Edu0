import { getMyStudySessions, createStudySession, updateStudySession, deleteStudySession } from "../../api/study-sessions.js";
import { escapeHtml } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "../shared/page-ui.js";
import { showToast } from "../../components/toast.js";

function sessionForm() {
    return `<form class="inline-form" data-session-form hidden><div class="form-grid"><label>Matéria<input name="materia" required></label><label>Assunto<input name="assunto" required></label><label>Duração (min)<input name="duracao_minutos" type="number" min="1" required value="30"></label><label>Dificuldade sentida<select name="dificuldade_sentida"><option value="">Não informar</option><option value="1">1 - Muito baixa</option><option value="2">2</option><option value="3">3 - Média</option><option value="4">4</option><option value="5">5 - Muito alta</option></select></label><label>Data<input name="data_sessao" type="date"></label><label class="form-span-2">Observações<textarea name="observacoes" rows="3"></textarea></label></div><div class="form-actions"><button class="mini-button" type="button" data-cancel-session>Cancelar</button><button class="mini-button mini-button--primary" type="submit">Registrar sessão</button></div></form>`;
}

export async function renderStudentStudySessions(container) {
    const sessions = await getMyStudySessions();
    const render = current => {
        container.innerHTML = `${pageHeader("Sessões de estudo", "Registre o que estudou e acompanhe sua rotina.", `<button class="mini-button mini-button--primary" type="button" data-new-session>Nova sessão</button>`)}${sessionForm()}${surface(current.length ? `<div class="compact-list">${current.map(session => `<article class="compact-row compact-row--actions"><div><strong>${escapeHtml(session.materia)} · ${escapeHtml(session.assunto)}</strong><p>${escapeHtml(session.duracao_minutos)} min${session.data_sessao ? ` · ${escapeHtml(session.data_sessao)}` : ""}${session.dificuldade_sentida ? ` · dificuldade ${escapeHtml(session.dificuldade_sentida)}/5` : ""}</p>${session.observacoes ? `<p>${escapeHtml(session.observacoes)}</p>` : ""}</div><div class="row-actions">${statusPill(session.concluida ? "Concluída" : "Pendente", session.concluida ? "success" : "warning")}<button class="mini-button" type="button" data-toggle-session="${session.id}">${session.concluida ? "Reabrir" : "Concluir"}</button><button class="mini-button mini-button--danger" type="button" data-delete-session="${session.id}">Excluir</button></div></article>`).join("")}</div>` : emptyBlock("Nenhuma sessão registrada", "Registre sua primeira sessão de estudo para começar o acompanhamento.", "clock"))}`;
        bind(current);
    };
    const bind = current => {
        const form = container.querySelector("[data-session-form]");
        container.querySelector("[data-new-session]")?.addEventListener("click", () => { form.hidden = false; form.scrollIntoView({ behavior: "smooth", block: "center" }); });
        container.querySelector("[data-cancel-session]")?.addEventListener("click", () => { form.hidden = true; form.reset(); });
        form?.addEventListener("submit", async event => {
            event.preventDefault();
            const data = new FormData(form);
            const payload = {
                materia: String(data.get("materia") || "").trim(),
                assunto: String(data.get("assunto") || "").trim(),
                duracao_minutos: Number(data.get("duracao_minutos")),
                dificuldade_sentida: data.get("dificuldade_sentida") ? Number(data.get("dificuldade_sentida")) : null,
                concluida: false,
                data_sessao: data.get("data_sessao") || null,
                observacoes: String(data.get("observacoes") || "").trim() || null,
            };
            const submit = form.querySelector('button[type="submit"]'); submit.disabled = true;
            try { const saved = await createStudySession(payload); current.unshift(saved); showToast("Sessão registrada."); render(current); }
            catch (error) { submit.disabled = false; showToast(error.message || "Não foi possível registrar a sessão.", "error"); }
        });
        container.querySelectorAll("[data-toggle-session]").forEach(button => button.addEventListener("click", async () => {
            const id = Number(button.dataset.toggleSession); const item = current.find(session => session.id === id); if (!item) return;
            button.disabled = true;
            try { const saved = await updateStudySession(id, { concluida: !item.concluida }); const next = current.map(session => session.id === id ? saved : session); showToast(saved.concluida ? "Sessão concluída." : "Sessão reaberta."); render(next); }
            catch (error) { button.disabled = false; showToast(error.message || "Não foi possível atualizar a sessão.", "error"); }
        }));
        container.querySelectorAll("[data-delete-session]").forEach(button => button.addEventListener("click", async () => {
            if (!window.confirm("Excluir esta sessão de estudo?")) return;
            const id = Number(button.dataset.deleteSession); button.disabled = true;
            try { await deleteStudySession(id); showToast("Sessão excluída."); render(current.filter(item => item.id !== id)); }
            catch (error) { button.disabled = false; showToast(error.message || "Não foi possível excluir a sessão.", "error"); }
        }));
    };
    render([...sessions]);
}
