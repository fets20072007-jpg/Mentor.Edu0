import { getTeacherClassrooms, getTeacherPendingAttendance } from '../../api/teacher.js';
import { listAssessments } from '../../api/assessments.js';
import { getPendingReviews } from '../../api/answers.js';
import { getMySchedule } from '../../api/schedules.js';
import { escapeHtml, formatDateTime } from '../../core/format.js';
import { pageHeader } from '../shared/page-ui.js';
import { focusGrid, bindFocusRoutes, startRotatingCard, safeArray, firstNonEmpty } from '../shared/dashboard-focus.js';
import { shortcutCard } from '../../components/card.js';

const weekdayNames=['domingo','segunda','terça','quarta','quinta','sexta','sábado'];
const norm=v=>String(v||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');


const teacherShortcuts = [
  { label: 'Minhas turmas', route: 'classrooms', icon: 'users' },
  { label: 'Avaliações', route: 'assessments', icon: 'clipboard' },
  { label: 'Banco de questões', route: 'question-bank', icon: 'school' },
  { label: 'Frequência', route: 'attendance', icon: 'calendar' },
  { label: 'Notas', route: 'grades', icon: 'chart' },
  { label: 'Desempenho', route: 'analytics', icon: 'activity' },
  { label: 'Biblioteca', route: 'library', icon: 'book' },
  { label: 'Horários', route: 'schedules', icon: 'calendar' },
  { label: 'Pendências', route: 'reviews', icon: 'help' }
];

function shortcutsSection() {
  return `<section class="dashboard-shortcuts-section"><div class="dashboard-shortcuts-heading"><span>Atalhos rápidos</span><p>Acesse rapidamente as áreas mais usadas.</p></div><section class="shortcut-grid">${teacherShortcuts.map(item => shortcutCard(item.label, item.route, item.icon)).join('')}</section></section>`;
}

function bindShortcutRoutes(container, navigate) {
  container.querySelectorAll('[data-route]').forEach(button => button.addEventListener('click', () => navigate(button.dataset.route)));
}

export async function renderTeacherDashboard(container,user,navigate){
 const [classrooms,assessments,pendingAttendance,reviews,schedules]=await Promise.all([
   getTeacherClassrooms().catch(()=>[]),listAssessments().catch(()=>[]),getTeacherPendingAttendance().catch(()=>[]),getPendingReviews().catch(()=>[]),getMySchedule().catch(()=>[])
 ]);
 const today=norm(weekdayNames[new Date().getDay()]);
 const todayRows=safeArray(schedules).filter(s=>norm(s.dia_semana).startsWith(today)).sort((a,b)=>String(a.hora_inicio||'').localeCompare(String(b.hora_inicio||'')));
 const classItems=todayRows.length?todayRows.map(s=>({kicker:'Aula de hoje',title:firstNonEmpty(s.disciplina,s.turma,'Turma'),value:String(s.hora_inicio||'').slice(0,5),hint:[s.turma,s.sala].filter(Boolean).join(' · ')})):safeArray(classrooms).length?safeArray(classrooms).map(c=>({kicker:'Turma vinculada',title:firstNonEmpty(c.nome,c.turma,`Turma #${c.id}`),value:firstNonEmpty(c.serie,''),hint:firstNonEmpty(c.turno,'Acesse Minhas turmas para detalhes.')})):[{kicker:'Agenda',title:'Nenhuma aula hoje',value:'—',hint:'Sua agenda diária aparecerá aqui.'}];
 const upcoming=safeArray(assessments).filter(a=>a.data&&new Date(a.data).getTime()>=Date.now()).sort((a,b)=>new Date(a.data)-new Date(b.data));
 const assessmentItems=upcoming.length?upcoming.map(a=>({kicker:'Próxima avaliação',title:a.titulo,value:formatDateTime(a.data),hint:a.descricao||'Avaliação programada.'})):[{kicker:'Avaliações',title:'Nenhuma prova próxima',value:'—',hint:'As próximas avaliações aparecerão aqui.'}];
 const pa=safeArray(pendingAttendance).length, pr=safeArray(reviews).length;
 const pendingItems=[
   {kicker:'Pendências',title:'Frequência para revisar',value:String(pa),hint:pa?'Existem faltas aguardando confirmação ou justificativa.':'Nenhuma pendência de frequência.'},
   {kicker:'Pendências',title:'Correções aguardando',value:String(pr),hint:pr?'Existem respostas que precisam de correção manual.':'Nenhuma correção pendente.'},
 ];
 container.innerHTML=`${pageHeader(`Olá, ${escapeHtml((user?.nome||'Professor').split(' ')[0])}`,'Acompanhe aulas, avaliações e pendências mais importantes.')}${focusGrid([
   {id:'teacher-classes',...classItems[0],iconName:'users',route:'classrooms'},
   {id:'teacher-assessments',...assessmentItems[0],iconName:'clipboard',route:'assessments'},
   {id:'teacher-pending',...pendingItems[0],iconName:'help',route:'reviews'},
 ])}${shortcutsSection()}`;
 bindFocusRoutes(container,navigate);
 bindShortcutRoutes(container,navigate); startRotatingCard(container,'teacher-classes',classItems); startRotatingCard(container,'teacher-assessments',assessmentItems); startRotatingCard(container,'teacher-pending',pendingItems);
}
