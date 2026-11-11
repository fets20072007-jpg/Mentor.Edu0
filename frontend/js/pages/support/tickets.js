import { getSupportTickets, updateTicketStatus } from '../../api/tickets.js';
import { listUsers } from '../../api/users.js';
import { escapeHtml, formatDateTime } from '../../core/format.js';
import { pageHeader, surface, emptyBlock, statusPill } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

const toneFor = status => {
  const s = String(status || '').toLowerCase();
  if (s.includes('resol')) return 'success';
  if (s.includes('análise') || s.includes('analise')) return 'warning';
  return 'neutral';
};

const priorityTone = value => {
  const p = String(value || '').toLowerCase();
  if (p === 'alta') return 'danger';
  if (p === 'media' || p === 'média') return 'warning';
  return 'neutral';
};

export async function renderSupportTickets(container){
  const [tickets, users] = await Promise.all([getSupportTickets(), listUsers()]);
  const names = new Map(users.map(u => [Number(u.id), u.nome || `Usuário #${u.id}`]));

  container.innerHTML = `${pageHeader('Chamados de suporte','Acompanhe solicitações, atualize o andamento e registre a solução.')}${surface(`
    <div class="support-toolbar">
      <label>Filtrar status<select data-ticket-filter><option value="todos">Todos</option><option value="Aberto">Abertos</option><option value="Em análise">Em análise</option><option value="Resolvido">Resolvidos</option></select></label>
      <label>Buscar<input data-ticket-search placeholder="Título, categoria ou solicitante"></label>
    </div>
    <div data-ticket-list>${tickets.length ? tickets.map(t => ticketCard(t, names)).join('') : emptyBlock('Nenhum chamado','Não há chamados registrados no momento.','message')}</div>
  `)}`;

  const apply = () => {
    const filter = container.querySelector('[data-ticket-filter]').value;
    const query = container.querySelector('[data-ticket-search]').value.trim().toLowerCase();
    container.querySelectorAll('[data-ticket-card]').forEach(card => {
      const okStatus = filter === 'todos' || card.dataset.status === filter;
      const okQuery = !query || card.dataset.search.includes(query);
      card.hidden = !(okStatus && okQuery);
    });
  };
  container.querySelector('[data-ticket-filter]')?.addEventListener('change', apply);
  container.querySelector('[data-ticket-search]')?.addEventListener('input', apply);

  container.querySelectorAll('[data-ticket-form]').forEach(form => form.addEventListener('submit', async e => {
    e.preventDefault();
    const id = Number(form.dataset.ticketForm);
    const status = form.status.value;
    const solucao = form.solucao.value.trim();
    if (status === 'Resolvido' && !solucao) {
      showToast('Informe a solução antes de concluir o chamado.','error');
      return;
    }
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    try {
      await updateTicketStatus(id,{status,solucao:solucao || null});
      showToast(`Chamado #${id} atualizado.`,'success');
      await renderSupportTickets(container);
    } finally { btn.disabled = false; }
  }));
}

function ticketCard(t, names){
  const requester = names.get(Number(t.requester_id)) || `Usuário #${t.requester_id}`;
  const search = `${t.titulo||''} ${t.categoria||''} ${requester}`.toLowerCase().replaceAll('"','&quot;');
  return `<article class="support-ticket" data-ticket-card data-status="${escapeHtml(t.status)}" data-search="${escapeHtml(search)}">
    <div class="support-ticket-head"><div><span class="support-ticket-id">#${t.id}</span><h3>${escapeHtml(t.titulo)}</h3><p>${escapeHtml(requester)} · ${formatDateTime(t.criado_em)}</p></div><div class="support-ticket-badges">${statusPill(t.prioridade,priorityTone(t.prioridade))}${statusPill(t.status,toneFor(t.status))}</div></div>
    <div class="support-ticket-body"><div><small>Categoria</small><strong>${escapeHtml(t.categoria || 'Sistema')}</strong></div><p>${escapeHtml(t.descricao)}</p></div>
    <form class="support-ticket-form" data-ticket-form="${t.id}">
      <label>Status<select name="status"><option ${t.status==='Aberto'?'selected':''}>Aberto</option><option ${t.status==='Em análise'?'selected':''}>Em análise</option><option ${t.status==='Resolvido'?'selected':''}>Resolvido</option></select></label>
      <label class="support-solution">Solução / retorno<textarea name="solucao" rows="2" placeholder="Registre o diagnóstico ou a solução aplicada...">${escapeHtml(t.solucao || '')}</textarea></label>
      <button class="mini-button mini-button--primary" type="submit">Salvar atendimento</button>
    </form>
  </article>`;
}
