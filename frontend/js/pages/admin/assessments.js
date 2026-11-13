import {
  getAdminAssessments,
  getAdminSummary,
  getAdminClassrooms,
  getAdminTeachers
} from '../../api/admin.js';
import { escapeHtml, formatDateTime } from '../../core/format.js';
import {
  pageHeader,
  surface,
  emptyBlock,
  statusPill,
  metricCard
} from '../shared/page-ui.js';

const FIXED_TYPES = [
  'Prova',
  'Exercício',
  'Trabalho',
  'Atividade avaliativa'
];

export async function renderAdminAssessments(container) {
  const [rows, sum, classrooms, teachers] = await Promise.all([
    getAdminAssessments(),
    getAdminSummary(),
    getAdminClassrooms(),
    getAdminTeachers()
  ]);

  container.innerHTML = `
    ${pageHeader(
      'Avaliações',
      'Visão institucional com filtros por turma, professor, tipo e pesquisa.'
    )}

    <div class="metric-grid">
      ${metricCard('Avaliações', String(sum.total_avaliacoes), 'clipboard')}
      ${metricCard('Ativas', String(sum.avaliacoes_ativas), 'activity')}
      ${metricCard('Turmas', String(sum.total_turmas), 'users')}
    </div>

    ${surface(`
      <div class="admin-filter-panel">
        <label>
          <span>Turma</span>
          <select data-class>
            <option value="">Todas as turmas</option>
            ${classrooms.map(c => `
              <option value="${c.id}">${escapeHtml(c.nome)}</option>
            `).join('')}
          </select>
        </label>

        <label>
          <span>Professor</span>
          <select data-teacher>
            <option value="">Todos os professores</option>
            ${teachers.map(t => `
              <option value="${t.id}">${escapeHtml(t.nome)}</option>
            `).join('')}
          </select>
        </label>

        <label>
          <span>Tipo</span>
          <select data-type>
            <option value="">Todos os tipos</option>
            ${FIXED_TYPES.map(type => `
              <option value="${escapeHtml(type)}">${escapeHtml(type)}</option>
            `).join('')}
          </select>
        </label>

        <label class="admin-filter-search">
          <span>Pesquisar</span>
          <input
            data-search
            type="search"
            placeholder="Avaliação, turma, professor ou tipo"
          >
        </label>
      </div>

      <div data-assessment-list class="page-section-gap"></div>
    `)}
  `;

  const draw = () => {
    const classroomId = container.querySelector('[data-class]').value;
    const teacherId = container.querySelector('[data-teacher]').value;
    const type = container.querySelector('[data-type]').value;
    const search = container.querySelector('[data-search]').value
      .trim()
      .toLowerCase();

    const filtered = rows.filter(a => {
      const classroom = classrooms.find(
        c => Number(c.id) === Number(a.classroom_id)
      );
      const teacher = teachers.find(
        t => Number(t.id) === Number(a.teacher_id)
      );

      const haystack = [
        a.titulo,
        a.tipo,
        classroom?.nome,
        teacher?.nome
      ].join(' ').toLowerCase();

      return (
        (!classroomId || Number(a.classroom_id) === Number(classroomId)) &&
        (!teacherId || Number(a.teacher_id) === Number(teacherId)) &&
        (!type || String(a.tipo || '').toLowerCase() === type.toLowerCase()) &&
        (!search || haystack.includes(search))
      );
    });

    const target = container.querySelector('[data-assessment-list]');

    if (!filtered.length) {
      target.innerHTML = emptyBlock(
        'Nenhuma avaliação',
        'Nenhuma avaliação corresponde aos filtros selecionados.',
        'clipboard'
      );
      return;
    }

    target.innerHTML = `
      <div class="data-table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>Avaliação</th>
              <th>Tipo</th>
              <th>Turma</th>
              <th>Professor</th>
              <th>Valor</th>
              <th>Data</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${filtered.map(a => {
              const classroom = classrooms.find(
                c => Number(c.id) === Number(a.classroom_id)
              );
              const teacher = teachers.find(
                t => Number(t.id) === Number(a.teacher_id)
              );

              return `
                <tr>
                  <td><strong>${escapeHtml(a.titulo || '—')}</strong></td>
                  <td>${escapeHtml(a.tipo || '—')}</td>
                  <td>${escapeHtml(classroom?.nome || 'Turma não identificada')}</td>
                  <td>${escapeHtml(teacher?.nome || 'Professor não identificado')}</td>
                  <td>${a.valor ?? '—'}</td>
                  <td>${a.data ? formatDateTime(a.data) : '—'}</td>
                  <td>
                    ${statusPill(
                      a.ativa ? 'Ativa' : 'Rascunho',
                      a.ativa ? 'success' : 'neutral'
                    )}
                  </td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;
  };

  container.querySelector('[data-class]').addEventListener('change', draw);
  container.querySelector('[data-teacher]').addEventListener('change', draw);
  container.querySelector('[data-type]').addEventListener('change', draw);
  container.querySelector('[data-search]').addEventListener('input', draw);

  draw();
}

export async function renderAdminReports(container, navigate) {
  const sum = await getAdminSummary();

  container.innerHTML = `
    ${pageHeader(
      'Relatórios',
      'Escolha uma área para abrir o relatório detalhado.'
    )}

    <div class="admin-report-nav">
      <button class="admin-report-card" type="button" data-report-route="reports">
        <span class="admin-report-card__kicker">Institucional</span>
        <strong>Desempenho</strong>
        <p>Alunos, professores, turmas e indicadores gerais.</p>
        <span class="admin-report-card__action">Abrir relatório →</span>
      </button>

      <button class="admin-report-card" type="button" data-report-route="reports-attendance">
        <span class="admin-report-card__kicker">Acadêmico</span>
        <strong>Frequência</strong>
        <p>Estrutura das turmas, horários e visão de frequência.</p>
        <span class="admin-report-card__action">Abrir relatório →</span>
      </button>

      <button class="admin-report-card" type="button" data-report-route="reports-assessments">
        <span class="admin-report-card__kicker">Avaliações</span>
        <strong>Avaliações</strong>
        <p>Volume, tipos, calendário e próximas avaliações.</p>
        <span class="admin-report-card__action">Abrir relatório →</span>
      </button>

      <button class="admin-report-card" type="button" data-report-route="schedules">
        <span class="admin-report-card__kicker">Cronogramas</span>
        <strong>Horários</strong>
        <p>Abra os cronogramas por turma e professor.</p>
        <span class="admin-report-card__action">Abrir cronogramas →</span>
      </button>
    </div>

    <div class="metric-grid page-section-gap">
      ${metricCard('Alunos', String(sum.total_alunos), 'users')}
      ${metricCard('Professores', String(sum.total_professores), 'users')}
      ${metricCard('Turmas', String(sum.total_turmas), 'school')}
      ${metricCard('Avaliações', String(sum.total_avaliacoes), 'clipboard')}
    </div>
  `;

  container.querySelectorAll('[data-report-route]').forEach(button => {
    button.addEventListener('click', () => navigate(button.dataset.reportRoute));
  });
}
