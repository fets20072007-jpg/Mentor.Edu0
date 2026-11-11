import { getMyGrades } from '../../api/grades.js';
import { getMySchedule } from '../../api/schedules.js';
import { listAssessments } from '../../api/assessments.js';
import { getMySubjects } from '../../api/subjects.js';
import { escapeHtml, formatDateTime, formatNumber } from '../../core/format.js';
import { pageHeader } from '../shared/page-ui.js';
import { focusGrid, bindFocusRoutes, startRotatingCard, safeArray, firstNonEmpty } from '../shared/dashboard-focus.js';
import { shortcutCard } from '../../components/card.js';
const weekdayNames=['domingo','segunda','terça','quarta','quinta','sexta','sábado'];
const norm=v=>String(v||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
function todaysClasses(rows){const today=norm(weekdayNames[new Date().getDay()]);return safeArray(rows).filter(i=>norm(i.dia_semana).startsWith(today)).sort((a,b)=>String(a.hora_inicio||'').localeCompare(String(b.hora_inicio||'')))}
const shortcuts=[{label:'Disciplinas',route:'subjects',icon:'book'},{label:'Avaliações',route:'assessments',icon:'clipboard'},{label:'Notas',route:'grades',icon:'chart'},{label:'Frequência',route:'attendance',icon:'users'},{label:'Biblioteca',route:'library',icon:'book'},{label:'Horários',route:'schedules',icon:'calendar'}];
function shortcutsSection(){return `<section class="dashboard-shortcuts-section"><div class="dashboard-shortcuts-heading"><span>Atalhos rápidos</span><p>Acesse rapidamente as áreas mais usadas.</p></div><section class="shortcut-grid">${shortcuts.map(i=>shortcutCard(i.label,i.route,i.icon)).join('')}</section></section>`}
function average(items){const v=items.map(x=>Number(x)).filter(Number.isFinite);return v.length?v.reduce((a,b)=>a+b,0)/v.length:null}
export async function renderStudentDashboard(container,user,navigate){
 const [grades,schedules,assessments,subjects]=await Promise.all([getMyGrades().catch(()=>[]),getMySchedule().catch(()=>[]),listAssessments().catch(()=>[]),getMySubjects().catch(()=>[])]);
 const subjectMap=new Map(subjects.map(s=>[s.id,s]));const assessmentMap=new Map(assessments.map(a=>[a.id,a]));
 const gradePairs=grades.map(g=>{const a=assessmentMap.get(g.assessment_id);const s=a?subjectMap.get(a.subject_id):null;return {grade:g,subject:s}}).filter(x=>x.subject&&Number.isFinite(Number(x.grade.nota)));
 const overall=average(gradePairs.map(x=>x.grade.nota));const cats={};gradePairs.forEach(x=>{const c=x.subject.categoria||'Outras';(cats[c]??=[]).push(x.grade.nota)});
 const notes=[{kicker:'Média geral',title:'Todas as disciplinas',value:overall===null?'—':formatNumber(overall,1),hint:'Média simples das notas já lançadas.'},...Object.entries(cats).map(([c,v])=>({kicker:'Área de conhecimento',title:c,value:formatNumber(average(v),1),hint:'Média das disciplinas classificadas nesta área.'}))];
 const today=todaysClasses(schedules);const classes=today.length?today.map(i=>({kicker:'Aula de hoje',title:firstNonEmpty(i.disciplina,'Disciplina'),value:String(i.hora_inicio||'').slice(0,5),hint:[i.professor,i.turma].filter(Boolean).join(' · ')})):[{kicker:'Aulas de hoje',title:'Nenhuma aula cadastrada',value:'—',hint:'Consulte sua grade semanal em Horários.'}];
 const next=assessments.filter(a=>a.data&&new Date(a.data).getTime()>=Date.now()).sort((a,b)=>new Date(a.data)-new Date(b.data));const examItems=next.length?next.map(a=>({kicker:subjectMap.get(a.subject_id)?.nome||'Próxima avaliação',title:a.titulo,value:formatDateTime(a.data),hint:a.descricao||'Confira os detalhes e o prazo.'})):[{kicker:'Avaliações',title:'Nenhuma avaliação próxima',value:'—',hint:'Novas avaliações aparecerão aqui.'}];
 container.innerHTML=`${pageHeader(`Olá, ${escapeHtml((user?.nome||'Aluno').split(' ')[0])}`,'O essencial do seu dia, sem excesso de informação.')}${focusGrid([{id:'student-grades',...notes[0],iconName:'chart',route:'grades'},{id:'student-classes',...classes[0],iconName:'calendar',route:'schedules'},{id:'student-assessments',...examItems[0],iconName:'clipboard',route:'assessments'}])}${shortcutsSection()}`;bindFocusRoutes(container,navigate);container.querySelectorAll('[data-route]').forEach(b=>b.addEventListener('click',()=>navigate(b.dataset.route)));startRotatingCard(container,'student-grades',notes);startRotatingCard(container,'student-classes',classes);startRotatingCard(container,'student-assessments',examItems);
}
