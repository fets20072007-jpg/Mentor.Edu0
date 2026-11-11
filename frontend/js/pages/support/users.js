import { listUsers } from '../../api/users.js';
import { escapeHtml } from '../../core/format.js';
import { pageHeader, surface, emptyBlock, statusPill } from '../shared/page-ui.js';

const norm = v => String(v || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();

export async function renderSupportUsers(container){ return renderDirectory(container, null, 'Usuários', 'Consulte contas para auxiliar no atendimento. Dados pedagógicos não são exibidos.'); }
export async function renderSupportTeachers(container){ return renderDirectory(container, 'professor', 'Professores', 'Consulte professores cadastrados para apoio operacional.'); }

async function renderDirectory(container, role, title, description){
  const all = await listUsers();
  const users = role ? all.filter(u => norm(u.tipo) === role) : all;
  container.innerHTML = `${pageHeader(title,description)}${surface(`
    <div class="support-toolbar"><label>Buscar<input data-user-search placeholder="Nome, e-mail, matrícula ou perfil"></label>${!role?`<label>Perfil<select data-user-role><option value="todos">Todos</option><option value="aluno">Aluno</option><option value="professor">Professor</option><option value="administracao">Administração</option><option value="suporte">Suporte</option></select></label>`:''}</div>
    ${users.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Nome</th><th>E-mail</th><th>Perfil</th><th>Matrícula</th><th>Status</th></tr></thead><tbody>${users.map(u=>`<tr data-user-row data-role="${escapeHtml(norm(u.tipo))}" data-search="${escapeHtml(`${u.nome||''} ${u.email||''} ${u.matricula||''} ${u.tipo||''}`.toLowerCase())}"><td>${escapeHtml(u.nome||'—')}</td><td>${escapeHtml(u.email||'—')}</td><td>${statusPill(u.tipo||'—','neutral')}</td><td>${escapeHtml(u.matricula||'—')}</td><td>${statusPill(u.ativo===false?'Inativo':'Ativo',u.ativo===false?'neutral':'success')}</td></tr>`).join('')}</tbody></table></div>`:emptyBlock('Nenhum usuário','Nenhum registro encontrado.','users')}
  `)}`;
  const apply=()=>{const q=container.querySelector('[data-user-search]')?.value.trim().toLowerCase()||'';const r=container.querySelector('[data-user-role]')?.value||'todos';container.querySelectorAll('[data-user-row]').forEach(row=>row.hidden=!( (!q||row.dataset.search.includes(q)) && (r==='todos'||row.dataset.role===r) ));};
  container.querySelector('[data-user-search]')?.addEventListener('input',apply);container.querySelector('[data-user-role]')?.addEventListener('change',apply);
}
