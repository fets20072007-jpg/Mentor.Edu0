import { getTeacherClassrooms,getClassroomAttendanceSummary } from "../../api/teacher.js";
import { escapeHtml } from "../../core/format.js";
import { pageHeader,surface,emptyBlock } from "../shared/page-ui.js";

function metric(label, value, suffix = "") {
  return `<div class="card" style="padding:18px;min-width:160px">
    <div style="font-size:13px;color:var(--text-muted,#64748b);margin-bottom:6px">${escapeHtml(label)}</div>
    <strong style="font-size:26px">${escapeHtml(String(value ?? 0))}${suffix}</strong>
  </div>`;
}

function renderSummary(data) {
  const total = data.registros ?? 0;
  return `
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin-bottom:18px">
      ${metric("Registros", total)}
      ${metric("Presenças", data.presencas)}
      ${metric("Faltas justificadas", data.faltas_justificadas)}
      ${metric("Não justificadas", data.faltas_nao_justificadas)}
      ${metric("Pendentes", data.faltas_pendentes)}
      ${metric("Presença", data.percentual_presenca, "%")}
    </div>
    <div class="data-table-wrap">
      <table class="data-table">
        <thead><tr><th>Indicador</th><th>Quantidade</th></tr></thead>
        <tbody>
          <tr><td>Aulas/registros contabilizados</td><td>${total}</td></tr>
          <tr><td>Presenças</td><td>${data.presencas ?? 0}</td></tr>
          <tr><td>Faltas justificadas</td><td>${data.faltas_justificadas ?? 0}</td></tr>
          <tr><td>Faltas não justificadas</td><td>${data.faltas_nao_justificadas ?? 0}</td></tr>
          <tr><td>Faltas aguardando análise</td><td>${data.faltas_pendentes ?? 0}</td></tr>
          <tr><td>Percentual de presença</td><td><strong>${data.percentual_presenca ?? 0}%</strong></td></tr>
        </tbody>
      </table>
    </div>`;
}

export async function renderTeacherAttendanceSummary(container){
  const cls=await getTeacherClassrooms();
  container.innerHTML=`${pageHeader("Resumo de frequência","Consulte os indicadores de frequência por turma.")}${surface(`
    <label>Turma<select data-class><option value="">Selecione</option>${cls.map(c=>`<option value="${c.classroom_id}">${escapeHtml(c.turma)}</option>`).join('')}</select></label>
    <div data-result class="page-section-gap">${emptyBlock("Selecione uma turma","O resumo aparecerá aqui de forma organizada.","calendar")}</div>
  `)}`;
  container.querySelector('[data-class]').addEventListener('change',async e=>{
    const r=container.querySelector('[data-result]');
    if(!e.target.value){
      r.innerHTML=emptyBlock("Selecione uma turma","O resumo aparecerá aqui de forma organizada.","calendar");
      return;
    }
    const data=await getClassroomAttendanceSummary(e.target.value);
    r.innerHTML=renderSummary(data);
  });
}
