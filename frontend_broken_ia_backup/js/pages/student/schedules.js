import { getMySchedule } from "../../api/schedules.js";
import { escapeHtml } from "../../core/format.js";
import { pageHeader, surface, emptyBlock } from "../shared/page-ui.js";

const order = ["segunda", "terça", "terca", "quarta", "quinta", "sexta", "sábado", "sabado", "domingo"];
const dayLabel = value => ({ segunda: "Segunda-feira", "segunda-feira": "Segunda-feira", terça: "Terça-feira", terca: "Terça-feira", "terça-feira": "Terça-feira", "terca-feira": "Terça-feira", quarta: "Quarta-feira", "quarta-feira": "Quarta-feira", quinta: "Quinta-feira", "quinta-feira": "Quinta-feira", sexta: "Sexta-feira", "sexta-feira": "Sexta-feira", sábado: "Sábado", sabado: "Sábado", domingo: "Domingo" }[String(value).toLowerCase()] || value);

export async function renderStudentSchedules(container) {
    const schedules = (await getMySchedule()).filter(item => item.ativo !== false);
    const grouped = schedules.reduce((acc, item) => { const key = String(item.dia_semana || "Outro").toLowerCase(); (acc[key] ||= []).push(item); return acc; }, {});
    const days = Object.keys(grouped).sort((a,b) => { const ai = order.findIndex(x => a.startsWith(x)); const bi = order.findIndex(x => b.startsWith(x)); return (ai < 0 ? 99 : ai) - (bi < 0 ? 99 : bi); });
    container.innerHTML = `${pageHeader("Horários", "Sua grade semanal conforme as disciplinas da turma.")}${surface(days.length ? `<div class="schedule-board">${days.map(day => `<section class="schedule-day"><h3>${escapeHtml(dayLabel(day))}</h3><div>${grouped[day].sort((a,b) => String(a.hora_inicio).localeCompare(String(b.hora_inicio))).map(item => `<article class="schedule-class"><time>${escapeHtml(String(item.hora_inicio).slice(0,5))}–${escapeHtml(String(item.hora_fim).slice(0,5))}</time><div><strong>${escapeHtml(item.disciplina)}</strong><p>${escapeHtml(item.professor)} · ${escapeHtml(item.turma)}</p></div></article>`).join("")}</div></section>`).join("")}</div>` : emptyBlock("Nenhum horário cadastrado", "A administração ainda não publicou horários para sua turma.", "calendar"))}`;
}
