import { getPendingTicketCount, getSupportTickets } from '../../api/tickets.js';
import { listUsers } from '../../api/users.js';
import { listBooks } from '../../api/library.js';
import { escapeHtml } from '../../core/format.js';
import { pageHeader } from '../shared/page-ui.js';
import { focusGrid, bindFocusRoutes, startRotatingCard, safeArray } from '../shared/dashboard-focus.js';
import { shortcutCard } from '../../components/card.js';


const supportShortcuts = [
  { label: 'Chamados', route: 'tickets', icon: 'message' },
  { label: 'Usuários', route: 'users', icon: 'users' },
  { label: 'Professores', route: 'teachers', icon: 'user' },
  { label: 'Biblioteca', route: 'library-books', icon: 'book' },
  { label: 'Capítulos', route: 'library-chapters', icon: 'book' },
  { label: 'Configurações', route: 'settings', icon: 'settings' }
];

function shortcutsSection() {
  return `<section class="dashboard-shortcuts-section"><div class="dashboard-shortcuts-heading"><span>Atalhos rápidos</span><p>Acesse rapidamente as áreas mais usadas.</p></div><section class="shortcut-grid">${supportShortcuts.map(item => shortcutCard(item.label, item.route, item.icon)).join('')}</section></section>`;
}

function bindShortcutRoutes(container, navigate) {
  container.querySelectorAll('[data-route]').forEach(button => button.addEventListener('click', () => navigate(button.dataset.route)));
}

export async function renderSupportDashboard(container,user,navigate){
 const [pendingResult,tickets,users,books]=await Promise.all([
  getPendingTicketCount().catch(()=>({pendentes:0})),getSupportTickets().catch(()=>[]),listUsers().catch(()=>[]),listBooks().catch(()=>[])
 ]);
 const pending=Number(pendingResult?.pendentes||0);
 const recent=safeArray(tickets).slice(0,6);
 const ticketItems=recent.length?recent.map(t=>({kicker:'Chamados',title:t.titulo||`Chamado #${t.id}`,value:String(t.status||'Aberto').replaceAll('_',' '),hint:`Prioridade: ${t.prioridade||'normal'}`})):[{kicker:'Chamados',title:'Nenhum chamado recente',value:String(pending),hint:'A central está sem novos chamados.'}];
 const userItems=[
  {kicker:'Diretório',title:'Usuários cadastrados',value:String(safeArray(users).length),hint:'Contas disponíveis para consulta operacional.'},
  {kicker:'Diretório',title:'Professores cadastrados',value:String(safeArray(users).filter(u=>String(u.tipo||'').toLowerCase()==='professor').length),hint:'Docentes visíveis ao suporte.'},
 ];
 const libraryItems=[{kicker:'Biblioteca',title:'Livros cadastrados',value:String(safeArray(books).length),hint:'Estrutura institucional disponível para manutenção.'}];
 container.innerHTML=`${pageHeader(`Olá, ${escapeHtml((user?.nome||'Suporte').split(' ')[0])}`,'O essencial para atendimento e manutenção operacional.')}${focusGrid([
  {id:'support-tickets',...ticketItems[0],iconName:'message',route:'tickets'},
  {id:'support-users',...userItems[0],iconName:'users',route:'users'},
  {id:'support-library',...libraryItems[0],iconName:'book',route:'library-books'},
 ])}${shortcutsSection()}`;
 bindFocusRoutes(container,navigate);
 bindShortcutRoutes(container,navigate); startRotatingCard(container,'support-tickets',ticketItems); startRotatingCard(container,'support-users',userItems);
}
