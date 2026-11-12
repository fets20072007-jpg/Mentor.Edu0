import { getAdminStudents, getAdminTeachers, registerUser } from '../../api/admin.js';
import { listUsers } from '../../api/users.js';
import { listClassrooms } from '../../api/classrooms.js';
import { escapeHtml } from '../../core/format.js';
import { pageHeader, surface, emptyBlock, statusPill } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

const roleNorm = v => String(v || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const row = (u, extra='') => `<tr><td>${escapeHtml(u.nome||'—')}</td><td>${escapeHtml(u.email||'—')}</td><td>${extra}</td></tr>`;

function errorMessage(error, fallback = 'Não foi possível concluir o cadastro.') {
  return error?.message || error?.data?.detail || fallback;
}

export async function renderAdminStudents(container){
  const [rows, classrooms] = await Promise.all([getAdminStudents(), listClassrooms()]);
  container.innerHTML = `${pageHeader('Alunos','Cadastre e consulte os alunos da instituição.')}${surface(`
    <form class="inline-form" data-create-student><h3 class="form-title">Novo aluno</h3><div class="form-grid">
      <label>Nome<input name="nome" required></label><label>E-mail<input type="email" name="email" required></label>
      <label>Senha inicial<input type="password" name="senha" required minlength="6"></label><label>Série<input name="serie"></label>
      <label>Escola<input name="escola"></label><label>Turma<select name="classroom_id" required><option value="">Selecione uma turma</option>${classrooms.map(c=>`<option value="${c.id}">${escapeHtml(c.nome)} · ${escapeHtml(c.serie)}</option>`).join('')}</select></label>
    </div><div class="form-actions"><button class="mini-button mini-button--primary">Cadastrar aluno</button></div></form>
    ${rows.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Aluno</th><th>E-mail</th><th>Série / escola</th></tr></thead><tbody>${rows.map(u=>row(u,`${escapeHtml(u.serie||'—')} · ${escapeHtml(u.escola||'—')}`)).join('')}</tbody></table></div>`:emptyBlock('Nenhum aluno','Ainda não há alunos cadastrados.','users')}`)}`;

  container.querySelector('[data-create-student]')?.addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.currentTarget;
    const button = f.querySelector('button[type="submit"], button');
    try {
      if (button) button.disabled = true;
      await registerUser({
        nome: f.nome.value.trim(),
        email: f.email.value.trim(),
        senha: f.senha.value,
        tipo: 'aluno',
        serie: f.serie.value || null,
        escola: f.escola.value || null,
        classroom_id: f.classroom_id.value ? Number(f.classroom_id.value) : null
      });
      showToast('Aluno cadastrado.','success');
      await renderAdminStudents(container);
    } catch (error) {
      showToast(errorMessage(error, 'Não foi possível cadastrar o aluno.'), 'error');
    } finally {
      if (button) button.disabled = false;
    }
  });
}

export async function renderAdminTeachers(container){
  const rows = await getAdminTeachers();
  container.innerHTML = `${pageHeader('Professores','Cadastre e acompanhe professores ativos.')}${surface(`
    <form class="inline-form" data-create-teacher><h3 class="form-title">Novo professor</h3><div class="form-grid">
      <label>Nome<input name="nome" required></label><label>E-mail<input type="email" name="email" required></label>
      <label>Senha inicial<input type="password" name="senha" required minlength="6"></label><label>CPF<input name="cpf" required autocomplete="off" placeholder="Somente números ou com pontuação"></label>
      <label>Especialidade<input name="especialidade" required></label><label>Matrícula<input name="matricula" required></label>
      <label>Telefone<input name="telefone"></label><label>Carga horária<input type="number" name="carga_horaria" value="40" min="1"></label>
    </div><div class="form-actions"><button type="submit" class="mini-button mini-button--primary">Cadastrar professor</button></div></form>
    ${rows.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Professor</th><th>E-mail</th><th>Especialidade</th><th>Status</th></tr></thead><tbody>${rows.map(u=>`<tr><td>${escapeHtml(u.nome)}</td><td>${escapeHtml(u.email)}</td><td>${escapeHtml(u.especialidade||'—')}</td><td>${statusPill(u.ativo?'Ativo':'Inativo',u.ativo?'success':'neutral')}</td></tr>`).join('')}</tbody></table></div>`:emptyBlock('Nenhum professor','Ainda não há professores cadastrados.','users')}`)}`;

  container.querySelector('[data-create-teacher]')?.addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.currentTarget;
    const button = f.querySelector('button[type="submit"], button');
    try {
      if (button) button.disabled = true;
      await registerUser({
        nome: f.nome.value.trim(),
        email: f.email.value.trim(),
        senha: f.senha.value,
        tipo: 'professor',
        cpf: f.cpf.value.trim(),
        especialidade: f.especialidade.value.trim(),
        matricula: f.matricula.value.trim(),
        telefone: f.telefone.value.trim() || null,
        carga_horaria: Number(f.carga_horaria.value || 40)
      });
      showToast('Professor cadastrado.','success');
      await renderAdminTeachers(container);
    } catch (error) {
      showToast(errorMessage(error, 'Não foi possível cadastrar o professor.'), 'error');
    } finally {
      if (button) button.disabled = false;
    }
  });
}

async function renderRoleList(container, role, title, description){
  const users = (await listUsers()).filter(u=>roleNorm(u.tipo)===role);
  container.innerHTML = `${pageHeader(title,description)}${surface(users.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Nome</th><th>E-mail</th><th>Tipo</th></tr></thead><tbody>${users.map(u=>`<tr><td>${escapeHtml(u.nome)}</td><td>${escapeHtml(u.email)}</td><td>${statusPill(u.tipo,'neutral')}</td></tr>`).join('')}</tbody></table></div>`:emptyBlock('Nenhum usuário','Nenhum registro encontrado para este perfil.','users'))}`;
}

export const renderAdminUsers = c => renderRoleList(c,'administracao','Administração','Usuários com perfil administrativo. O cadastro de novos administradores é exclusivo do Suporte.');
export const renderSupportUsers = c => renderRoleList(c,'suporte','Suporte','Usuários responsáveis pelo suporte da plataforma.');
