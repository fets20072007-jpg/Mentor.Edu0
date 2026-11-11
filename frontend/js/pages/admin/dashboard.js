import { getAdminSummary, getAdminAssessments, getAdminClassrooms } from '../../api/admin.js';
import { getAdminStudents, getAdminTeachers } from '../../api/admin.js';
import { escapeHtml, formatDateTime } from '../../core/format.js';
import { pageHeader } from '../shared/page-ui.js';
import { focusGrid, bindFocusRoutes, startRotatingCard, safeArray, firstNonEmpty } from '../shared/dashboard-focus.js';
import { shortcutCard } from '../../components/card.js';


const adminShortcuts = [
  { label: 'Usuários', route: 'users', icon: 'users' },
  { label: 'Turmas', route: 'classrooms', icon: 'school' },
  { label: 'Disciplinas', route: 'subjects', icon: 'book' },
  { label: 'Matrículas', route: 'enrollments', icon: 'check' },
  { label: 'Avaliações', route: 'assessments', icon: 'clipboard' },
  { label: 'Relatórios', route: 'reports', icon: 'chart' },
  { label: 'Pendências', route: 'pending', icon: 'help' },
  { label: 'Ações rápidas', route: 'quick-actions', icon: 'activity' }
];

function shortcutsSection() {
  return `<section class="dashboard-shortcuts-section"><div class="dashboard-shortcuts-heading"><span>Atalhos rápidos</span><p>Acesse rapidamente as áreas mais usadas.</p></div><section class="shortcut-grid">${adminShortcuts.map(item => shortcutCard(item.label, item.route, item.icon)).join('')}</section></section>`;
}

function bindShortcutRoutes(container, navigate) {
  container.querySelectorAll('[data-route]').forEach(button => button.addEventListener('click', () => navigate(button.dataset.route)));
}

export async function renderAdminDashboard(container,user,navigate){
 const [summary,assessments,classrooms,students,teachers]=await Promise.all([
  getAdminSummary().catch(()=>({})),getAdminAssessments().catch(()=>[]),getAdminClassrooms().catch(()=>[]),getAdminStudents().catch(()=>[]),getAdminTeachers().catch(()=>[])
 ]);
 const peopleItems=[
  {kicker:'Comunidade',title:'Alunos cadastrados',value:String(firstNonEmpty(summary?.alunos,summary?.students,safeArray(students).length)),hint:'Contas de estudantes ativas ou cadastradas.'},
  {kicker:'Comunidade',title:'Professores cadastrados',value:String(firstNonEmpty(summary?.professores,summary?.teachers,safeArray(teachers).length)),hint:'Docentes registrados na plataforma.'},
 ];
 const structureItems=safeArray(classrooms).length?safeArray(classrooms).map(c=>({kicker:'Estrutura escolar',title:firstNonEmpty(c.nome,`Turma #${c.id}`),value:firstNonEmpty(c.serie,''),hint:[c.turno,c.sala?`Sala ${c.sala}`:''].filter(Boolean).join(' · ')})):[{kicker:'Estrutura escolar',title:'Nenhuma turma cadastrada',value:'0',hint:'Crie turmas para organizar alunos e disciplinas.'}];
 const upcoming=safeArray(assessments).filter(a=>a.data&&new Date(a.data).getTime()>=Date.now()).sort((a,b)=>new Date(a.data)-new Date(b.data));
 const assessmentItems=upcoming.length?upcoming.map(a=>({kicker:'Calendário acadêmico',title:a.titulo,value:formatDateTime(a.data),hint:a.descricao||'Avaliação programada na instituição.'})):[{kicker:'Calendário acadêmico',title:'Nenhuma avaliação próxima',value:'—',hint:'As próximas avaliações aparecerão aqui.'}];
 container.innerHTML=`${pageHeader(`Olá, ${escapeHtml((user?.nome||'Administração').split(' ')[0])}`,'Visão rápida da instituição: pessoas, turmas e calendário.')}${focusGrid([
  {id:'admin-people',...peopleItems[0],iconName:'users',route:'users'},
  {id:'admin-structure',...structureItems[0],iconName:'school',route:'classrooms'},
  {id:'admin-assessments',...assessmentItems[0],iconName:'clipboard',route:'assessments'},
 ])}${shortcutsSection()}`;
 bindFocusRoutes(container,navigate);
 bindShortcutRoutes(container,navigate); startRotatingCard(container,'admin-people',peopleItems); startRotatingCard(container,'admin-structure',structureItems); startRotatingCard(container,'admin-assessments',assessmentItems);
}
