import { listClassrooms } from '../../api/classrooms.js';
import { getClassroomTeachers, createClassroom, setClassroomDt } from '../../api/admin.js';
import { getClassroomEnrollments } from '../../api/enrollments.js';
import { listUsers } from '../../api/users.js';
import { escapeHtml } from '../../core/format.js';
import { pageHeader, surface, emptyBlock, statusPill } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

const roleNorm = v => String(v || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();

export async function renderAdminClassrooms(container){
  const [rows, allUsers] = await Promise.all([listClassrooms(), listUsers()]);
  const students = allUsers.filter(u => roleNorm(u.tipo) === 'aluno');

  const details = await Promise.all(rows.map(async classroom => {
    const [teachers, enrollments] = await Promise.all([
      getClassroomTeachers(classroom.id).catch(() => []),
      getClassroomEnrollments(classroom.id).catch(() => [])
    ]);

    const enrolledStudents = enrollments
      .filter(e => e.ativo !== false)
      .map(enrollment => ({
        enrollment,
        student: students.find(u => Number(u.id) === Number(enrollment.user_id)) || null
      }));

    return { classroom, teachers, enrolledStudents };
  }));

  container.innerHTML = `${pageHeader('Turmas','Crie turmas e abra cada uma para visualizar alunos e professores vinculados.')}${surface(`
    <form class="inline-form" data-form>
      <h3 class="form-title">Nova turma</h3>
      <div class="form-grid">
        <label>Nome<input name="nome" required placeholder="3º A"></label>
        <label>Série<input name="serie" required placeholder="3º ano"></label>
        <label>Turno<select name="turno"><option>Manhã</option><option>Tarde</option><option>Noite</option><option>Integral</option></select></label>
        <label>Sala<input name="sala" required></label>
        <label>Ano<input type="number" name="ano" value="${new Date().getFullYear()}" required></label>
        <label>Capacidade<input type="number" name="capacidade" value="40" min="1"></label>
      </div>
      <div class="form-actions"><button class="mini-button mini-button--primary">Criar turma</button></div>
    </form>

    ${details.length ? `<div class="entity-grid">
      ${details.map(({classroom,teachers,enrolledStudents}) => `
        <article class="entity-card">
          <div class="entity-card-main">
            <span class="entity-card-kicker">${escapeHtml(classroom.turno)} · ${classroom.ano}</span>
            <h3>${escapeHtml(classroom.nome)}</h3>
            <p>${escapeHtml(classroom.serie)} · Sala ${escapeHtml(classroom.sala)} · capacidade ${classroom.capacidade}</p>
            <p><strong>${enrolledStudents.length}</strong> aluno(s) · <strong>${teachers.length}</strong> professor(es)</p>
          </div>
          <div class="entity-card-footer">
            <button class="mini-button" data-class-detail="${classroom.id}" data-view="students">Alunos</button>
            <button class="mini-button" data-class-detail="${classroom.id}" data-view="teachers">Professores</button>
            ${statusPill(classroom.ativa?'Ativa':'Inativa', classroom.ativa?'success':'neutral')}
          </div>
        </article>`).join('')}
    </div><div data-detail class="page-section-gap"></div>` : emptyBlock('Nenhuma turma','Crie a primeira turma para começar.','users')}
  `)}`;

  container.querySelector('[data-form]')?.addEventListener('submit', async e => {
    e.preventDefault();
    const f = e.currentTarget;
    try {
      await createClassroom({
        nome:f.nome.value, serie:f.serie.value, turno:f.turno.value,
        sala:f.sala.value, ano:Number(f.ano.value),
        capacidade:Number(f.capacidade.value||40)
      });
      showToast('Turma criada.','success');
      await renderAdminClassrooms(container);
    } catch(error) {
      showToast(error.message||'Não foi possível criar a turma.','error');
    }
  });

  container.querySelectorAll('[data-class-detail]').forEach(btn => btn.addEventListener('click', () => {
    const item = details.find(x => Number(x.classroom.id) === Number(btn.dataset.classDetail));
    const target = container.querySelector('[data-detail]');
    if (!item || !target) return;

    if (btn.dataset.view === 'students') {
      target.innerHTML = surface(`
        <div class="section-heading">
          <h3>${escapeHtml(item.classroom.nome)} · Alunos</h3>
          <p>Estudantes com matrícula ativa nesta turma.</p>
        </div>
        ${item.enrolledStudents.length ? `
          <div class="data-table-wrap">
            <table class="data-table">
              <thead><tr><th>Aluno</th><th>E-mail</th><th>Matrícula</th><th>Contato</th><th>Data da matrícula</th></tr></thead>
              <tbody>
                ${item.enrolledStudents.map(({enrollment,student}) => `
                  <tr>
                    <td><strong>${escapeHtml(student?.nome || `Aluno #${enrollment.user_id}`)}</strong></td>
                    <td>${escapeHtml(student?.email || '—')}</td>
                    <td>${escapeHtml(student?.matricula || '—')}</td>
                    <td>${escapeHtml(student?.contato1 || student?.contato2 || student?.telefone || '—')}</td>
                    <td>${enrollment.data_matricula ? new Date(enrollment.data_matricula).toLocaleString('pt-BR') : '—'}</td>
                  </tr>`).join('')}
              </tbody>
            </table>
          </div>` : emptyBlock('Nenhum aluno','Esta turma ainda não possui matrículas ativas.','users')}
      `);
    } else {
      target.innerHTML = surface(`
        <div class="section-heading">
          <h3>${escapeHtml(item.classroom.nome)} · Professores</h3>
          <p>Docentes que lecionam nesta turma.</p>
        </div>
        ${item.teachers.length ? `
          <div class="data-table-wrap">
            <table class="data-table">
              <thead><tr><th>Professor</th><th>Disciplinas</th><th>DT</th></tr></thead>
              <tbody>${item.teachers.map(t=>`
                <tr>
                  <td>${escapeHtml(t.nome||'—')}</td>
                  <td>${escapeHtml((t.disciplinas||[]).join(', ')||'—')}</td>
                  <td>${t.is_dt?'Sim':'Não'}</td>
                </tr>`).join('')}</tbody>
            </table>
          </div>` : emptyBlock('Nenhum professor','Ainda não existem professores vinculados por disciplinas.','users')}
      `);
    }

    target.scrollIntoView({behavior:'smooth', block:'start'});
  }));
}

export async function renderAdminDt(container){
  const classrooms = await listClassrooms();
  const cards = await Promise.all(classrooms.map(async c=>({c,teachers:await getClassroomTeachers(c.id).catch(()=>[])})));

  container.innerHTML = `${pageHeader('Diretores de turma','Defina o DT entre os professores que já lecionam em cada turma.')}${surface(cards.length ? `
    <div class="entity-grid">
      ${cards.map(({c,teachers})=>`
        <article class="entity-card">
          <div class="entity-card-main">
            <span class="entity-card-kicker">${escapeHtml(c.serie)} · ${escapeHtml(c.turno)}</span>
            <h3>${escapeHtml(c.nome)}</h3>
            <label class="admin-control">Diretor de turma
              <select data-dt="${c.id}">
                <option value="">Sem DT</option>
                ${teachers.map(t=>`<option value="${t.teacher_id}" ${t.is_dt?'selected':''}>${escapeHtml(t.nome)}${t.disciplinas?.length?` · ${escapeHtml(t.disciplinas.join(', '))}`:''}</option>`).join('')}
              </select>
            </label>
          </div>
          <div class="entity-card-footer">
            <button class="mini-button mini-button--primary" data-save-dt="${c.id}">Salvar DT</button>
          </div>
        </article>`).join('')}
    </div>` : emptyBlock('Nenhuma turma','Não existem turmas disponíveis.','users'))}`;

  container.querySelectorAll('[data-save-dt]').forEach(btn=>btn.addEventListener('click',async()=>{
    const id=Number(btn.dataset.saveDt);
    const select=container.querySelector(`[data-dt="${id}"]`);
    try {
      await setClassroomDt(id, select.value ? Number(select.value) : null);
      showToast('Diretor de turma atualizado.','success');
    } catch(error) {
      showToast(error.message||'Não foi possível definir o DT.','error');
    }
  }));
}
