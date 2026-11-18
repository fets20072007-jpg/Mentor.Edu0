import { getAdminStudents, getAdminTeachers, registerUser } from '../../api/admin.js';
import { listUsers } from '../../api/users.js';
import { listClassrooms } from '../../api/classrooms.js';
import { escapeHtml } from '../../core/format.js';
import { pageHeader, surface, emptyBlock, statusPill } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

const roleNorm = v => String(v || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const row = (u, extra='') => `<tr><td>${escapeHtml(u.nome||'—')}</td><td>${escapeHtml(u.email||'—')}</td><td>${extra}</td></tr>`;
const errorMessage = (error, fallback='Não foi possível concluir o cadastro.') => error?.data?.detail || error?.message || fallback;

function inferredSchool(rows){
  return rows.find(u=>String(u.escola||'').trim())?.escola || localStorage.getItem('mentor_school_name') || 'Escola da instituição';
}

export async function renderAdminStudents(container){
  const [rows, classrooms] = await Promise.all([getAdminStudents(), listClassrooms()]);
  const school = inferredSchool(rows);
  container.innerHTML = `${pageHeader('Alunos','Cadastre estudantes com identificação e contatos institucionais.')}${surface(`
    <form class="inline-form" data-create-student>
      <h3 class="form-title">Novo aluno</h3>
      <div class="form-grid">
        <label>Nome<input name="nome" required></label>
        <label>E-mail<input type="email" name="email" required></label>
        <label>Senha inicial<input type="password" name="senha" required minlength="6"></label>
        <label>CPF <small>(opcional)</small><input name="cpf" placeholder="000.000.000-00"></label>
        <label>Matrícula<input name="matricula" placeholder="Matrícula institucional"></label>
        <label>Escola<input name="escola" value="${escapeHtml(school)}"></label>
        <label>Contato 1<input name="contato1" placeholder="Telefone principal"></label>
        <label>Contato 2<input name="contato2" placeholder="Telefone alternativo"></label>
        <label>Turma<select name="classroom_id" required><option value="">Selecione uma turma</option>${classrooms.map(c=>`<option value="${c.id}">${escapeHtml(c.nome)} · ${escapeHtml(c.serie)}</option>`).join('')}</select></label>
      </div>
      <div class="form-actions"><button class="mini-button mini-button--primary">Cadastrar aluno</button></div>
    </form>
    ${rows.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Aluno</th><th>E-mail</th><th>Matrícula</th><th>Turma</th><th>Contatos</th></tr></thead><tbody>${rows.map(u=>`<tr><td>${escapeHtml(u.nome||'—')}</td><td>${escapeHtml(u.email||'—')}</td><td>${escapeHtml(u.matricula||'—')}</td><td>${escapeHtml(classrooms.find(c=>Number(c.id)===Number(u.classroom_id))?.nome||'—')}</td><td>${escapeHtml([u.contato1,u.contato2].filter(Boolean).join(' / ')||'—')}</td></tr>`).join('')}</tbody></table></div>`:emptyBlock('Nenhum aluno','Ainda não há alunos cadastrados.','users')}`)}`;

  container.querySelector('[data-create-student]')?.addEventListener('submit', async e => {
    e.preventDefault(); const f=e.currentTarget; const button=f.querySelector('button');
    try{
      button.disabled=true;
      const cls=classrooms.find(c=>Number(c.id)===Number(f.classroom_id.value));
      await registerUser({
        nome:f.nome.value.trim(), email:f.email.value.trim(), senha:f.senha.value, tipo:'aluno',
        cpf:f.cpf.value.trim()||null, matricula:f.matricula.value.trim()||null,
        escola:f.escola.value.trim()||school, serie:cls?.serie||null,
        contato1:f.contato1.value.trim()||null, contato2:f.contato2.value.trim()||null,
        classroom_id:Number(f.classroom_id.value)
      });
      localStorage.setItem('mentor_school_name', f.escola.value.trim()||school);
      showToast('Aluno cadastrado.','success'); await renderAdminStudents(container);
    }catch(error){ showToast(errorMessage(error),'error'); button.disabled=false; }
  });
}

export async function renderAdminTeachers(container){
  const rows=await getAdminTeachers();
  container.innerHTML=`${pageHeader('Professores','Cadastre e acompanhe professores ativos.')}${surface(`
    <form class="inline-form" data-create-teacher><h3 class="form-title">Novo professor</h3><div class="form-grid">
      <label>Nome<input name="nome" required></label><label>E-mail<input type="email" name="email" required></label>
      <label>Senha inicial<input type="password" name="senha" required minlength="6"></label><label>CPF <small>(opcional)</small><input name="cpf" placeholder="000.000.000-00"></label>
      <label>Especialidade<input name="especialidade" required></label><label>Matrícula<input name="matricula" required></label>
      <label>Contato 1<input name="telefone"></label><label>Contato 2<input name="contato2"></label>
      <label>Carga horária<input type="number" name="carga_horaria" value="40" min="1"></label>
    </div><div class="form-actions"><button type="submit" class="mini-button mini-button--primary">Cadastrar professor</button></div></form>
    ${rows.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Professor</th><th>E-mail</th><th>Especialidade</th><th>Matrícula</th><th>Status</th></tr></thead><tbody>${rows.map(u=>`<tr><td>${escapeHtml(u.nome)}</td><td>${escapeHtml(u.email)}</td><td>${escapeHtml(u.especialidade||'—')}</td><td>${escapeHtml(u.matricula||'—')}</td><td>${statusPill(u.ativo?'Ativo':'Inativo',u.ativo?'success':'neutral')}</td></tr>`).join('')}</tbody></table></div>`:emptyBlock('Nenhum professor','Ainda não há professores cadastrados.','users')}`)}`;
  container.querySelector('[data-create-teacher]')?.addEventListener('submit', async e=>{
    e.preventDefault(); const f=e.currentTarget; const button=f.querySelector('button');
    try{
      button.disabled=true;
      await registerUser({nome:f.nome.value.trim(),email:f.email.value.trim(),senha:f.senha.value,tipo:'professor',cpf:f.cpf.value.trim()||null,especialidade:f.especialidade.value.trim(),matricula:f.matricula.value.trim(),telefone:f.telefone.value.trim()||null,contato1:f.telefone.value.trim()||null,contato2:f.contato2.value.trim()||null,carga_horaria:Number(f.carga_horaria.value||40)});
      showToast('Professor cadastrado.','success'); await renderAdminTeachers(container);
    }catch(error){showToast(errorMessage(error,'Não foi possível cadastrar o professor.'),'error');button.disabled=false;}
  });
}

async function renderRoleList(container,role,title,description){
 const users=(await listUsers()).filter(u=>roleNorm(u.tipo)===role);
 container.innerHTML=`${pageHeader(title,description)}${surface(users.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Nome</th><th>E-mail</th><th>Tipo</th><th>Contato</th></tr></thead><tbody>${users.map(u=>`<tr><td>${escapeHtml(u.nome)}</td><td>${escapeHtml(u.email)}</td><td>${statusPill(u.tipo,'neutral')}</td><td>${escapeHtml(u.contato1||u.contato2||'—')}</td></tr>`).join('')}</tbody></table></div>`:emptyBlock('Nenhum usuário','Nenhum registro encontrado para este perfil.','users'))}`;
}
export const renderAdminUsers=c=>renderRoleList(c,'administracao','Administração','Usuários com perfil administrativo. O cadastro de novos administradores é exclusivo do Suporte.');
export const renderSupportUsers=c=>renderRoleList(c,'suporte','Suporte','Usuários responsáveis pelo suporte da plataforma.');
