import { listSchedules } from '../../api/schedules.js';
import { listSubjects } from '../../api/subjects.js';
import { listClassrooms } from '../../api/classrooms.js';
import { listTeacherProfiles, createSchedule, deleteSchedule } from '../../api/admin.js';
import { escapeHtml } from '../../core/format.js';
import { pageHeader,surface,emptyBlock,statusPill } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

const DAYS=['Segunda','Terça','Quarta','Quinta','Sexta'];
const SLOTS=[
 {start:'07:00',end:'07:50'}, {start:'07:50',end:'08:40'},
 {label:'INTERVALO',start:'08:40',end:'08:50',break:true},
 {start:'08:50',end:'09:40'}, {start:'09:40',end:'10:30'},
 {label:'INTERVALO',start:'10:30',end:'10:50',break:true},
 {start:'10:50',end:'11:40'}, {start:'11:40',end:'12:30'},
 {label:'ALMOÇO',start:'12:30',end:'13:50',break:true},
 {start:'13:50',end:'14:40'}
];
const PALETTE={
 'Linguagens':'#dbeafe','Matemática':'#ede9fe','Ciências da Natureza':'#dcfce7','Ciências Humanas':'#fef3c7','Técnica / Curso':'#ffe4e6','Outras':'#e5e7eb'
};
const time=v=>String(v||'').slice(0,5);
function subjectFor(row,subs){return subs.find(s=>Number(s.id)===Number(row.subject_id))||subs.find(s=>String(s.nome)===String(row.disciplina));}
function rowClassId(row,subs){return Number(row.classroom_id||subjectFor(row,subs)?.classroom_id||0);}
function rowTeacherId(row,subs){return Number(row.teacher_id||subjectFor(row,subs)?.teacher_id||0);}
function lessonCell(row,subs){if(!row)return '<span style="color:#94a3b8">—</span>';const sub=subjectFor(row,subs);const bg=PALETTE[sub?.categoria||'Outras']||PALETTE.Outras;return `<div style="background:${bg};border-radius:8px;padding:7px 8px"><strong>${escapeHtml(row.disciplina||sub?.nome||'Disciplina')}</strong><small style="display:block;margin-top:3px">${escapeHtml(row.professor||'')}</small></div>`;}
function classroomGrid(classroom,rows,subs){
 const own=rows.filter(r=>rowClassId(r,subs)===Number(classroom.id)&&r.ativo!==false);
 return `<section style="margin:18px 0"><div class="section-heading"><h3>${escapeHtml(classroom.nome)} · ${escapeHtml(classroom.serie)}</h3><p>${escapeHtml(classroom.turno)} · Sala ${escapeHtml(classroom.sala)}</p></div><div class="data-table-wrap"><table class="data-table"><thead><tr><th>Horário</th>${DAYS.map(d=>`<th>${d}</th>`).join('')}</tr></thead><tbody>${SLOTS.map(slot=>slot.break?`<tr style="background:#fff59d"><td><strong>${slot.label}</strong><br><small>${slot.start}–${slot.end}</small></td><td colspan="5" style="text-align:center"><strong>${slot.label}</strong></td></tr>`:`<tr><td><strong>${slot.start}–${slot.end}</strong></td>${DAYS.map(day=>{const r=own.find(x=>x.dia_semana===day&&time(x.hora_inicio)===slot.start);return `<td>${lessonCell(r,subs)}</td>`}).join('')}</tr>`).join('')}</tbody></table></div></section>`;
}
function usedKey(day,start,id){return `${day}|${start}|${id}`;}
async function autoGenerate(rows,subs,classrooms){
 const activeSubs=subs.filter(s=>s.ativa!==false);const lessonSlots=SLOTS.filter(s=>!s.break);const usedClass=new Set(),usedTeacher=new Set();
 rows.filter(r=>r.ativo!==false).forEach(r=>{usedClass.add(usedKey(r.dia_semana,time(r.hora_inicio),rowClassId(r,subs)));usedTeacher.add(usedKey(r.dia_semana,time(r.hora_inicio),rowTeacherId(r,subs)));});
 const proposals=[];
 for(const classroom of classrooms){
   const classSubs=activeSubs.filter(s=>Number(s.classroom_id)===Number(classroom.id));
   for(const sub of classSubs){
     const target=Math.max(1,Math.round(Number(sub.carga_horaria||40)/40));
     const existing=rows.filter(r=>r.ativo!==false&&Number(r.subject_id)===Number(sub.id)).length;
     let need=Math.max(0,target-existing);
     for(const day of DAYS){for(const slot of lessonSlots){if(!need)break;const ck=usedKey(day,slot.start,classroom.id),tk=usedKey(day,slot.start,sub.teacher_id);if(usedClass.has(ck)||usedTeacher.has(tk))continue;proposals.push({subject_id:Number(sub.id),dia_semana:day,hora_inicio:slot.start,hora_fim:slot.end});usedClass.add(ck);usedTeacher.add(tk);need--; } if(!need)break;}
   }
 }
 if(!proposals.length) throw new Error('Não há novos horários para gerar com a configuração atual.');
 if(!confirm(`Gerar automaticamente ${proposals.length} horário(s) usando a carga horária e evitando conflitos de turma/professor?`))return;
 let ok=0,fail=0;for(const p of proposals){try{await createSchedule(p);ok++;}catch{fail++;}}
 showToast(`${ok} horário(s) gerado(s)${fail?` · ${fail} não puderam ser criados por conflito`:''}.`,fail?'error':'success');
}
export async function renderAdminSchedules(container){
 const [rows,subs,classrooms,teachers]=await Promise.all([listSchedules(),listSubjects(),listClassrooms(),listTeacherProfiles()]);
 container.innerHTML=`${pageHeader('Horários','Monte a grade semanal, filtre por turma/professor e gere cronogramas separados.')}${surface(`
 <div class="inline-alert"><strong>Horários predefinidos</strong><p>O gerador usa os horários do modelo institucional: 07:00–14:40, com intervalos e almoço destacados.</p></div>
 <form class="inline-form" data-form><h3 class="form-title">Novo horário</h3><div class="form-grid"><label>Disciplina<select name="subject_id" required><option value="">Selecione</option>${subs.map(s=>`<option value="${s.id}">${escapeHtml(s.nome)} · ${escapeHtml(classrooms.find(c=>Number(c.id)===Number(s.classroom_id))?.nome||`turma #${s.classroom_id}`)}</option>`).join('')}</select></label><label>Dia<select name="dia_semana">${DAYS.map(d=>`<option>${d}</option>`).join('')}</select></label><label>Horário<select name="slot" required>${SLOTS.filter(s=>!s.break).map(s=>`<option value="${s.start}|${s.end}">${s.start}–${s.end}</option>`).join('')}</select></label></div><div class="form-actions"><button type="button" class="mini-button" data-generate>Gerar automaticamente</button><button class="mini-button mini-button--primary">Adicionar horário</button></div></form>
 <div class="form-grid page-section-gap"><label>Turma<select data-class><option value="">Todas</option>${classrooms.map(c=>`<option value="${c.id}">${escapeHtml(c.nome)}</option>`).join('')}</select></label><label>Professor<select data-teacher><option value="">Todos</option>${teachers.filter(t=>t.ativo!==false).map(t=>`<option value="${t.id}">${escapeHtml(t.nome)}</option>`).join('')}</select></label><label>Pesquisar<input data-search placeholder="Disciplina, turma ou professor"></label></div>
 <div data-grids></div><div data-table></div>`)}`;
 const draw=()=>{const cid=container.querySelector('[data-class]').value,tid=container.querySelector('[data-teacher]').value,q=container.querySelector('[data-search]').value.toLowerCase().trim();const filtered=rows.filter(r=>r.ativo!==false&&(!cid||rowClassId(r,subs)===Number(cid))&&(!tid||rowTeacherId(r,subs)===Number(tid))&&(!q||[r.disciplina,r.turma,r.professor].join(' ').toLowerCase().includes(q)));const classes=cid?classrooms.filter(c=>Number(c.id)===Number(cid)):classrooms;container.querySelector('[data-grids]').innerHTML=classes.map(c=>classroomGrid(c,filtered,subs)).join('')||emptyBlock('Sem cronogramas','Cadastre disciplinas e horários para visualizar os quadros.','calendar');container.querySelector('[data-table]').innerHTML=filtered.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Dia</th><th>Horário</th><th>Disciplina</th><th>Turma</th><th>Professor</th><th></th></tr></thead><tbody>${filtered.map(r=>`<tr><td>${escapeHtml(r.dia_semana)}</td><td>${time(r.hora_inicio)}–${time(r.hora_fim)}</td><td>${escapeHtml(r.disciplina)}</td><td>${escapeHtml(r.turma)}</td><td>${escapeHtml(r.professor)}</td><td><button class="mini-button" data-delete="${r.id}">Desativar</button></td></tr>`).join('')}</tbody></table></div>`:'';container.querySelectorAll('[data-delete]').forEach(b=>b.addEventListener('click',async()=>{await deleteSchedule(Number(b.dataset.delete));showToast('Horário desativado.','success');await renderAdminSchedules(container);}));};
 draw(); container.querySelectorAll('[data-class],[data-teacher]').forEach(el=>el.addEventListener('change',draw));container.querySelector('[data-search]').addEventListener('input',draw);
 container.querySelector('[data-generate]').addEventListener('click',async()=>{try{await autoGenerate(rows,subs,classrooms);await renderAdminSchedules(container);}catch(error){showToast(error.message,'error');}});
 container.querySelector('[data-form]').addEventListener('submit',async e=>{e.preventDefault();const f=e.currentTarget;const [hora_inicio,hora_fim]=f.slot.value.split('|');try{await createSchedule({subject_id:Number(f.subject_id.value),dia_semana:f.dia_semana.value,hora_inicio,hora_fim});showToast('Horário adicionado.','success');await renderAdminSchedules(container);}catch(error){showToast(error.message||'Conflito de horário ou dados inválidos.','error');}});
}
