import { getMyGrades } from "../../api/grades.js";
import { listAssessments } from "../../api/assessments.js";
import { getMySubjects } from "../../api/subjects.js";
import { escapeHtml, formatNumber } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "../shared/page-ui.js";

function assessmentGroup(title='') {
  const t=String(title).toLowerCase();
  if (/prova|avalia|teste|simulado/.test(t)) return 'Provas';
  if (/trabalho|semin|projeto/.test(t)) return 'Trabalhos';
  if (/exerc|lista/.test(t)) return 'Exercícios';
  return 'Atividades com pontos';
}

export async function renderStudentGrades(container) {
  const [grades, assessments, subjects] = await Promise.all([getMyGrades(), listAssessments(), getMySubjects()]);
  const assessmentMap = new Map(assessments.map(a=>[a.id,a]));
  const bySubject = new Map(subjects.map(s=>[s.id,{subject:s,items:[]} ]));
  grades.forEach(g=>{ const a=assessmentMap.get(g.assessment_id); if(!a) return; if(!bySubject.has(a.subject_id)) return; bySubject.get(a.subject_id).items.push({...g,assessment:a}); });
  const rows=[...bySubject.values()];
  container.innerHTML = `${pageHeader('Notas','Abra uma disciplina para ver provas, trabalhos, atividades e exercícios.')}${rows.length?`<div class="subject-grade-grid">${rows.map(({subject,items})=>{const vals=items.map(i=>Number(i.nota)).filter(Number.isFinite);const avg=vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:null;const groups=Object.groupBy?Object.groupBy(items,i=>assessmentGroup(i.assessment?.titulo)):items.reduce((o,i)=>((o[assessmentGroup(i.assessment?.titulo)]??=[]).push(i),o),{});return `<details class="subject-grade-card"><summary><div><span class="entity-card-kicker">${escapeHtml(subject.categoria||'Outras')}</span><h3>${escapeHtml(subject.nome)}</h3></div><div class="subject-grade-average"><small>Média</small><strong>${avg===null?'—':formatNumber(avg,1)}</strong></div></summary><div class="subject-grade-groups">${Object.entries(groups).map(([label,list])=>`<section><h4>${escapeHtml(label)}</h4>${list.length?`<div class="compact-list">${list.map(i=>{const n=Number(i.nota);const tone=n>=7?'success':n>=5?'warning':'danger';return `<article class="compact-row"><div><strong>${escapeHtml(i.assessment?.titulo||'Atividade')}</strong><p>${escapeHtml(i.observacao||'Sem observação')}</p></div>${statusPill(formatNumber(n,1),tone)}</article>`}).join('')}</div>`:'<p class="muted">Nenhum registro.</p>'}</section>`).join('')}</div></details>`}).join('')}</div>`:surface(emptyBlock('Nenhuma disciplina encontrada','As disciplinas da sua turma aparecerão aqui.','book'))}`;
}
