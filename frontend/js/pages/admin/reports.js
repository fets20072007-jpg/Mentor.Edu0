import { getAdminSummary, getAdminStudents, getAdminTeachers, getAdminClassrooms, getAdminAssessments } from '../../api/admin.js';
import { listSchedules } from '../../api/schedules.js';
import { escapeHtml, formatDateTime } from '../../core/format.js';
import { pageHeader, surface, emptyBlock, metricCard, statusPill } from '../shared/page-ui.js';

export async function renderAdminPerformanceReport(container){
  const [sum, students, teachers, classrooms] = await Promise.all([getAdminSummary(),getAdminStudents(),getAdminTeachers(),getAdminClassrooms()]);
  container.innerHTML = `${pageHeader('Relatório de desempenho','Resumo operacional para apoiar a revisão institucional dos dados acadêmicos.')}
    <div class="metric-grid metric-grid--wide">${metricCard('Alunos',String(sum.total_alunos),'users')}${metricCard('Professores',String(sum.total_professores),'users')}${metricCard('Turmas',String(sum.total_turmas),'school')}${metricCard('Avaliações',String(sum.total_avaliacoes),'clipboard')}</div>
    ${surface(`<div class="report-split"><section><div class="section-heading"><h3>Distribuição institucional</h3><p>Cadastros atualmente disponíveis no sistema.</p></div><div class="report-bars"><div><span>Alunos</span><strong>${students.length}</strong></div><div><span>Professores ativos</span><strong>${teachers.filter(t=>t.ativo).length}</strong></div><div><span>Turmas ativas</span><strong>${classrooms.filter(c=>c.ativa!==false).length}</strong></div></div></section><section><div class="section-heading"><h3>Leitura do painel</h3><p>Os dados apresentados vêm dos módulos administrativos já disponíveis. Indicadores pedagógicos detalhados permanecem nos painéis de Professor.</p></div><div class="inline-alert"><strong>Escopo institucional</strong><p>Use este resumo para conferir estrutura e volume de cadastros antes da revisão final de UX.</p></div></section></div>`)}`;
}

export async function renderAdminAttendanceReport(container){
  const [classrooms, schedules] = await Promise.all([getAdminClassrooms(), listSchedules()]);
  const active = schedules.filter(s=>s.ativo!==false);
  container.innerHTML = `${pageHeader('Relatório de frequência','Visão estrutural das turmas e horários que sustentam o registro de frequência.')}
    <div class="metric-grid">${metricCard('Turmas',String(classrooms.length),'users')}${metricCard('Horários ativos',String(active.length),'calendar')}${metricCard('Turnos',String(new Set(classrooms.map(c=>c.turno).filter(Boolean)).size),'activity')}</div>
    ${surface(classrooms.length ? `<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Turma</th><th>Série</th><th>Turno</th><th>Sala</th><th>Horários</th><th>Status</th></tr></thead><tbody>${classrooms.map(c=>`<tr><td><strong>${escapeHtml(c.nome)}</strong></td><td>${escapeHtml(c.serie||'—')}</td><td>${escapeHtml(c.turno||'—')}</td><td>${escapeHtml(c.sala||'—')}</td><td>${active.filter(s=>String(s.turma||'').includes(c.nome)).length}</td><td>${statusPill(c.ativa===false?'Inativa':'Ativa',c.ativa===false?'neutral':'success')}</td></tr>`).join('')}</tbody></table></div>` : emptyBlock('Sem turmas','Não existem turmas para consolidar.','users'))}`;
}

export async function renderAdminAssessmentReport(container){
  const rows = await getAdminAssessments();
  const now = Date.now();
  const future = rows.filter(a=>a.data && new Date(a.data).getTime()>=now);
  const types = new Map(); rows.forEach(a=>types.set(a.tipo || 'Não informado',(types.get(a.tipo || 'Não informado')||0)+1));
  container.innerHTML = `${pageHeader('Relatório de avaliações','Acompanhe volume, calendário e tipos de avaliações cadastradas.')}
    <div class="metric-grid">${metricCard('Total',String(rows.length),'clipboard')}${metricCard('Próximas',String(future.length),'calendar')}${metricCard('Tipos',String(types.size),'activity')}</div>
    ${surface(rows.length ? `<div class="report-split"><section><div class="section-heading"><h3>Por tipo</h3></div><div class="report-bars">${[...types.entries()].map(([name,total])=>`<div><span>${escapeHtml(name)}</span><strong>${total}</strong></div>`).join('')}</div></section><section><div class="section-heading"><h3>Próximas avaliações</h3></div>${future.length?`<div class="compact-list">${future.slice(0,6).map(a=>`<div class="compact-row"><div><strong>${escapeHtml(a.titulo)}</strong><p>${escapeHtml(a.tipo||'Avaliação')} · turma #${a.classroom_id}</p></div><small>${formatDateTime(a.data)}</small></div>`).join('')}</div>`:emptyBlock('Nenhuma próxima avaliação','O calendário não possui avaliações futuras.','calendar')}</section></div>` : emptyBlock('Sem avaliações','Ainda não existem avaliações cadastradas.','clipboard'))}`;
}
