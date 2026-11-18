import {
  createTicket,
  getMyTickets,
  getTicketRecipients,
  getTicketInbox,
  respondToTicket,
} from "../../api/tickets.js";
import { escapeHtml, formatDateTime } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "./page-ui.js";
import { showToast } from "../../components/toast.js";

function recipientOptions(rows, profile) {
  const filtered = rows.filter(item => String(item.perfil || "").toLowerCase() === String(profile || "").toLowerCase());
  if (!filtered.length) return `<option value="">Nenhum destinatário disponível</option>`;
  return `<option value="">Selecione a pessoa</option>${filtered.map(item => `
    <option value="${Number(item.user_id)}">${escapeHtml(item.nome)}${item.detalhe ? ` — ${escapeHtml(item.detalhe)}` : ""}</option>
  `).join("")}`;
}

function ticketForm(recipients) {
  return `<form class="inline-form ticket-create-form" data-ticket-form hidden>
    <div class="form-grid">
      <label>Título<input name="titulo" required></label>
      <label>Perfil do destinatário
        <select name="destinatario_perfil" data-recipient-profile required>
          <option value="">Selecione</option>
          <option>Professor</option>
          <option>Suporte</option>
          <option>Administração</option>
        </select>
      </label>
      <label class="form-span-2">Destinatário específico
        <select name="destinatario_user_id" data-recipient-user required disabled>
          <option value="">Escolha primeiro o perfil</option>
        </select>
        <small data-recipient-hint>Ao escolher Professor, aparecem somente os professores que lecionam para você.</small>
      </label>
      <label>Categoria
        <select name="categoria"><option>Sistema</option><option>Acesso</option><option>Cadastro</option><option>Pedagógico</option><option>Outro</option></select>
      </label>
      <label>Prioridade
        <select name="prioridade"><option>Baixa</option><option value="Media" selected>Média</option><option>Alta</option></select>
      </label>
      <label class="form-span-2">Descrição<textarea name="descricao" rows="4" required></textarea></label>
    </div>
    <div class="form-actions">
      <button type="button" class="mini-button" data-cancel-ticket>Cancelar</button>
      <button class="mini-button mini-button--primary">Abrir chamado</button>
    </div>
  </form>`;
}

function sentList(rows) {
  if (!rows.length) return emptyBlock("Nenhum chamado enviado", "Abra um chamado quando precisar de ajuda.", "message");
  return `<div class="compact-list">${rows.map(i => `<article class="compact-row">
    <div>
      <strong>${escapeHtml(i.titulo)}</strong>
      <p>${escapeHtml(i.descricao)}</p>
      <small>Para: ${escapeHtml(i.destinatario_nome || i.destinatario_perfil || "Suporte")} · ${escapeHtml(i.categoria)} · ${escapeHtml(i.prioridade)} · ${formatDateTime(i.criado_em)}</small>
      ${i.solucao ? `<p><b>Resposta/Solução:</b> ${escapeHtml(i.solucao)}</p>` : ""}
    </div>
    ${statusPill(i.status, /resolv/i.test(i.status) ? "success" : "warning")}
  </article>`).join("")}</div>`;
}

function inboxList(rows) {
  if (!rows.length) return "";
  return `${pageHeader("Chamados recebidos", "Solicitações direcionadas especificamente a você.")}${surface(`<div class="compact-list">${rows.map(i => `<article class="compact-row incoming-ticket" data-incoming-ticket="${i.id}">
    <div>
      <strong>${escapeHtml(i.titulo)}</strong>
      <p>${escapeHtml(i.descricao)}</p>
      <small>${escapeHtml(i.categoria)} · ${escapeHtml(i.prioridade)} · ${formatDateTime(i.criado_em)}</small>
      ${i.solucao ? `<p><b>Resposta:</b> ${escapeHtml(i.solucao)}</p>` : ""}
      ${!(/resolv/i.test(i.status)) ? `<form class="inline-form compact-response-form" data-ticket-response="${i.id}">
        <label>Status<select name="status"><option>Em análise</option><option>Resolvido</option></select></label>
        <label>Resposta/Solução<textarea name="solucao" rows="2" placeholder="Escreva a orientação ou solução"></textarea></label>
        <button class="mini-button mini-button--primary">Atualizar chamado</button>
      </form>` : ""}
    </div>
    ${statusPill(i.status, /resolv/i.test(i.status) ? "success" : "warning")}
  </article>`).join("")}</div>`)}`;
}

export async function renderMyTickets(container) {
  const [tickets, recipients, inbox] = await Promise.all([
    getMyTickets().catch(() => []),
    getTicketRecipients().catch(() => []),
    getTicketInbox().catch(() => []),
  ]);

  const render = (sent, received) => {
    container.innerHTML = `${pageHeader(
      "Chamados",
      "Escolha o perfil e a pessoa exata que deve receber sua solicitação.",
      `<button class="mini-button mini-button--primary" data-new-ticket>Novo chamado</button>`
    )}${ticketForm(recipients)}${surface(sentList(sent))}${inboxList(received)}`;
    bind(sent, received);
  };

  const bind = (sent, received) => {
    const form = container.querySelector("[data-ticket-form]");
    const profile = form?.querySelector("[data-recipient-profile]");
    const userSelect = form?.querySelector("[data-recipient-user]");

    container.querySelector("[data-new-ticket]")?.addEventListener("click", () => form.hidden = false);
    container.querySelector("[data-cancel-ticket]")?.addEventListener("click", () => form.hidden = true);

    profile?.addEventListener("change", () => {
      userSelect.disabled = !profile.value;
      userSelect.innerHTML = profile.value ? recipientOptions(recipients, profile.value) : `<option value="">Escolha primeiro o perfil</option>`;
    });

    form?.addEventListener("submit", async e => {
      e.preventDefault();
      const d = new FormData(form);
      const recipientId = Number(d.get("destinatario_user_id"));
      if (!recipientId) {
        showToast("Selecione o destinatário específico.", "error");
        return;
      }
      try {
        const saved = await createTicket({
          titulo: String(d.get("titulo")).trim(),
          descricao: String(d.get("descricao")).trim(),
          categoria: String(d.get("categoria")),
          prioridade: String(d.get("prioridade")),
          destinatario_perfil: String(d.get("destinatario_perfil")),
          destinatario_user_id: recipientId,
        });
        sent.unshift(saved);
        showToast("Chamado enviado ao destinatário selecionado.", "success");
        render(sent, received);
      } catch (err) {
        showToast(err.message || "Não foi possível abrir o chamado.", "error");
      }
    });

    container.querySelectorAll("[data-ticket-response]").forEach(responseForm => {
      responseForm.addEventListener("submit", async e => {
        e.preventDefault();
        const d = new FormData(responseForm);
        const id = Number(responseForm.dataset.ticketResponse);
        try {
          const updated = await respondToTicket(id, {
            status: String(d.get("status")),
            solucao: String(d.get("solucao") || "").trim() || null,
          });
          const idx = received.findIndex(item => Number(item.id) === id);
          if (idx >= 0) received[idx] = updated;
          showToast("Chamado atualizado.", "success");
          render(sent, received);
        } catch (err) {
          showToast(err.message || "Não foi possível atualizar o chamado.", "error");
        }
      });
    });
  };

  render([...tickets], [...inbox]);
}
