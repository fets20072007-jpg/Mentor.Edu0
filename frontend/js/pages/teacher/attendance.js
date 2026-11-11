import { getTeacherClassrooms, registerAttendance } from '../../api/teacher.js';
import { getMySubjects } from '../../api/subjects.js';
import { escapeHtml } from '../../core/format.js';
import { pageHeader, surface, emptyBlock } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

export async function renderTeacherAttendance(container){
  const [classrooms, subjects] = await Promise.all([getTeacherClassrooms(), getMySubjects()]);
  container.innerHTML = `${pageHeader('Registrar frequência','Selecione turma e disciplina para carregar toda a lista de alunos.')}${surface(`
    <div class="attendance-filter-card"><div class="form-grid">
      <label>Turma<select data-classroom><option value="">Selecione</option>${classrooms.map(c=>`<option value="${c.classroom_id}">${escapeHtml(c.turma)} · ${escapeHtml(c.serie||'')}</option>`).join('')}</select></label>
      <label>Disciplina<select data-subject disabled><option value="">Selecione a turma</option></select></label>
    </div></div>
    <div class="inline-alert attendance-info"><strong>Importante:</strong><p>Todos os alunos iniciam como <b>Presente</b>. Ao marcar <b>Falta</b>, será criada uma pendência para confirmação ou justificativa.</p></div>
    <div data-roster>${emptyBlock('Selecione uma turma','A lista completa de alunos aparecerá aqui.','users')}</div>
  `)}`;
  const classroomSelect=container.querySelector('[data-classroom]');
  const subjectSelect=container.querySelector('[data-subject]');
  const roster=container.querySelector('[data-roster]');
  const updateSubjects=()=>{
    const id=Number(classroomSelect.value); const list=subjects.filter(s=>Number(s.classroom_id)===id);
    subjectSelect.disabled=!id; subjectSelect.innerHTML=`<option value="">Selecione</option>${list.map(s=>`<option value="${s.id}">${escapeHtml(s.nome)}</option>`).join('')}`;
    renderRoster();
  };
  const renderRoster=()=>{
    const c=classrooms.find(x=>Number(x.classroom_id)===Number(classroomSelect.value));
    if(!c){roster.innerHTML=emptyBlock('Selecione uma turma','A lista completa de alunos aparecerá aqui.','users');return;}
    const students=c.alunos||[];
    if(!students.length){roster.innerHTML=emptyBlock('Turma sem alunos','Não há alunos ativos nesta turma.','users');return;}
    roster.innerHTML=`<form data-attendance-form><div class="data-table-wrap"><table class="data-table attendance-roster"><thead><tr><th>Nº</th><th>Aluno</th><th>Status</th><th>Observação</th><th>Situação</th></tr></thead><tbody>${students.map((a,i)=>`<tr data-student-row data-student-id="${a.id}"><td>${String(i+1).padStart(2,'0')}</td><td><strong>${escapeHtml(a.nome)}</strong></td><td><select name="status_${a.id}" data-status><option value="Presente">Presente</option><option value="Falta">Falta</option><option value="Atraso">Atraso</option></select></td><td><input name="obs_${a.id}" placeholder="Opcional"></td><td><span class="attendance-row-state is-present">Presente</span></td></tr>`).join('')}</tbody></table></div><div class="form-actions"><button class="mini-button mini-button--primary">Salvar frequência</button></div></form>`;
    roster.querySelectorAll('[data-status]').forEach(sel=>sel.addEventListener('change',()=>{const row=sel.closest('[data-student-row]');const state=row.querySelector('.attendance-row-state');const v=sel.value;state.textContent=v==='Falta'?'Pendência será gerada':v;state.className=`attendance-row-state ${v==='Falta'?'is-absence':v==='Atraso'?'is-delay':'is-present'}`;}));
    roster.querySelector('[data-attendance-form]').addEventListener('submit',async e=>{
      e.preventDefault(); if(!subjectSelect.value){showToast('Selecione a disciplina.','error');return;}
      const button=e.currentTarget.querySelector('button');button.disabled=true;button.textContent='Salvando...';
      try{
        for(const row of roster.querySelectorAll('[data-student-row]')){
          const id=Number(row.dataset.studentId);const status=row.querySelector('[data-status]').value;const obs=row.querySelector(`input[name="obs_${id}"]`).value||null;
          await registerAttendance({student_id:id,classroom_id:Number(classroomSelect.value),subject_id:Number(subjectSelect.value),status,justificada:false,observacao:obs});
        }
        showToast('Frequência da turma registrada.','success');
      }catch(err){showToast(err.message||'Não foi possível salvar a frequência.','error');}
      finally{button.disabled=false;button.textContent='Salvar frequência';}
    });
  };
  classroomSelect.addEventListener('change',updateSubjects); subjectSelect.addEventListener('change',renderRoster);
}
