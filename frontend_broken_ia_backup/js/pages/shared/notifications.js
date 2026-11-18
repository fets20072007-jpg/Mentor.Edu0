import { getNotifications, markAllRead, markRead } from "../../api/notifications.js";
import { escapeHtml, formatDateTime } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "./page-ui.js";
import { showToast } from "../../components/toast.js";

export async function renderNotifications(container) {
    const notifications = await getNotifications();
    const render = current => {
        container.innerHTML = `${pageHeader("Notificações", "Avisos e atualizações da sua conta.", current.some(item => !item.lida) ? `<button type="button" class="mini-button mini-button--primary" data-read-all>Marcar todas como lidas</button>` : "")}${surface(current.length ? `<div class="compact-list">${current.map(item => `<article class="compact-row notification-row ${item.lida ? "is-read" : ""}"><div><strong>${escapeHtml(item.titulo)}</strong><p>${escapeHtml(item.mensagem)}</p><small>${formatDateTime(item.criado_em)}</small></div><div class="row-actions">${statusPill(item.lida ? "Lida" : "Nova", item.lida ? "neutral" : "info")}${!item.lida ? `<button type="button" class="mini-button" data-read-notification="${item.id}">Marcar como lida</button>` : ""}</div></article>`).join("")}</div>` : emptyBlock("Sem notificações", "Você não possui notificações neste momento.", "bell"))}`;
        bind(current);
    };
    const bind = current => {
        container.querySelector("[data-read-all]")?.addEventListener("click", async button => {
            button.disabled = true;
            try { await markAllRead(); showToast("Notificações marcadas como lidas."); render(current.map(item => ({ ...item, lida: true }))); }
            catch (error) { button.disabled = false; showToast(error.message || "Não foi possível atualizar as notificações.", "error"); }
        });
        container.querySelectorAll("[data-read-notification]").forEach(button => button.addEventListener("click", async () => {
            const id = Number(button.dataset.readNotification); button.disabled = true;
            try { const saved = await markRead(id); render(current.map(item => item.id === id ? saved : item)); }
            catch (error) { button.disabled = false; showToast(error.message || "Não foi possível atualizar a notificação.", "error"); }
        }));
    };
    render([...notifications]);
}
