import {
  getAdminSummary,
  getAdminStudents,
  getAdminTeachers,
  getAdminClassrooms,
  getAdminAssessments
} from '../../api/admin.js';
import { listSchedules } from '../../api/schedules.js';
import { escapeHtml, formatDateTime } from '../../core/format.js';
import {
  pageHeader,
  surface,
  emptyBlock,
  metricCard,
  statusPill
} from '../shared/page-ui.js';

function reportBack(navigate) {
  return `
    <div class="report-toolbar">
      <button type="button" class="mini-button" data-report-home>
        ← Voltar aos relatórios
      </button>
    </div>
  `;
}

function bindBack(container, navigate) {
  container.querySelector('[data-report-home]')
    ?.addEventListener('click', () => navigate('reports'));
}

export async function renderAdminPerformanceReport(container, navigate) {
  const [sum, students, teachers, classrooms] = await Promise.all([
    getAdminSummary(),
    getAdminStudents(),
    getAdminTeachers(),
    getAdminClassrooms()
  ]);

  container.innerHTML = `
    ${pageHeader(
      'Relatório de desempenho',
      'Resumo operacional da estrutura institucional.'
    )}

    ${reportBack(navigate)}

    <div class="metric-grid metric-grid--wide">
      ${metricCard('Alunos', String(sum.total_alunos), 'users')}
      ${metricCard('Professores', String(sum.total_professores), 'users')}
      ${metricCard('Turmas', String(sum.total_turmas), 'school')}
      ${metricCard('Avaliações', String(sum.total_avaliacoes), 'clipboard')}
    </div>

    ${surface(`
      <div class="report-split">
        <section>
          <div class="section-heading">
            <h3>Distribuição institucional</h3>
            <p>Cadastros disponíveis atualmente.</p>
          </div>

          <div class="report-bars">
            <div><span>Alunos</span><strong>${students.length}</strong></div>
            <div>
              <span>Professores ativos</span>
              <strong>${teachers.filter(t => t.ativo).length}</strong>
            </div>
            <div>
              <span>Turmas ativas</span>
              <strong>${classrooms.filter(c => c.ativa !== false).length}</strong>
            </div>
          </div>
        </section>

        <section>
          <div class="section-heading">
            <h3>Próximos relatórios</h3>
            <p>Use os atalhos abaixo para navegar.</p>
          </div>

          <div class="report-inline-actions">
            <button class="mini-button" data-go="reports-attendance">
              Frequência
            </button>
            <button class="mini-button" data-go="reports-assessments">
              Avaliações
            </button>
            <button class="mini-button" data-go="schedules">
              Cronogramas
            </button>
          </div>
        </section>
      </div>
    `)}
  `;

  bindBack(container, navigate);
  container.querySelectorAll('[data-go]').forEach(button => {
    button.addEventListener('click', () => navigate(button.dataset.go));
  });
}

export async function renderAdminAttendanceReport(container, navigate) {
  const [classrooms, schedules] = await Promise.all([
    getAdminClassrooms(),
    listSchedules()
  ]);

  const active = schedules.filter(s => s.ativo !== false);

  container.innerHTML = `
    ${pageHeader(
      'Relatório de frequência',
      'Estrutura das turmas e horários vinculados.'
    )}

    ${reportBack(navigate)}

    <div class="metric-grid">
      ${metricCard('Turmas', String(classrooms.length), 'users')}
      ${metricCard('Horários ativos', String(active.length), 'calendar')}
      ${metricCard(
        'Turnos',
        String(new Set(classrooms.map(c => c.turno).filter(Boolean)).size),
        'activity'
      )}
    </div>

    ${surface(
      classrooms.length
        ? `
          <div class="data-table-wrap">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Turma</th>
                  <th>Série</th>
                  <th>Turno</th>
                  <th>Sala</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                ${classrooms.map(c => `
                  <tr>
                    <td><strong>${escapeHtml(c.nome)}</strong></td>
                    <td>${escapeHtml(c.serie || '—')}</td>
                    <td>${escapeHtml(c.turno || '—')}</td>
                    <td>${escapeHtml(c.sala || '—')}</td>
                    <td>
                      ${statusPill(
                        c.ativa === false ? 'Inativa' : 'Ativa',
                        c.ativa === false ? 'neutral' : 'success'
                      )}
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `
        : emptyBlock(
            'Sem turmas',
            'Não existem turmas para consolidar.',
            'users'
          )
    )}

    <div class="report-bottom-action">
      <button class="mini-button mini-button--primary" data-go-schedules>
        Abrir cronogramas e horários
      </button>
    </div>
  `;

  bindBack(container, navigate);
  container.querySelector('[data-go-schedules]')
    ?.addEventListener('click', () => navigate('schedules'));
}

export async function renderAdminAssessmentReport(container, navigate) {
  const [rows, classrooms, teachers] = await Promise.all([
    getAdminAssessments(),
    getAdminClassrooms(),
    getAdminTeachers()
  ]);

  const now = Date.now();
  const future = rows
    .filter(a => a.data && new Date(a.data).getTime() >= now)
    .sort((a, b) => new Date(a.data) - new Date(b.data));

  const fixedTypes = [
    'Prova',
    'Exercício',
    'Trabalho',
    'Atividade avaliativa'
  ];

  container.innerHTML = `
    ${pageHeader(
      'Relatório de avaliações',
      'Volume, calendário e tipos de avaliações cadastradas.'
    )}

    ${reportBack(navigate)}

    <div class="metric-grid">
      ${metricCard('Total', String(rows.length), 'clipboard')}
      ${metricCard('Próximas', String(future.length), 'calendar')}
      ${metricCard(
        'Tipos utilizados',
        String(new Set(rows.map(a => a.tipo).filter(Boolean)).size),
        'activity'
      )}
    </div>

    ${surface(`
      <div class="report-split">
        <section>
          <div class="section-heading">
            <h3>Por tipo</h3>
            <p>Os quatro tipos disponíveis no Mentor Edu.</p>
          </div>

          <div class="report-bars">
            ${fixedTypes.map(type => `
              <div>
                <span>${escapeHtml(type)}</span>
                <strong>
                  ${rows.filter(a =>
                    String(a.tipo || '').toLowerCase() === type.toLowerCase()
                  ).length}
                </strong>
              </div>
            `).join('')}
          </div>
        </section>

        <section>
          <div class="section-heading">
            <h3>Próximas avaliações</h3>
          </div>

          ${
            future.length
              ? future.slice(0, 8).map(a => {
                  const classroom = classrooms.find(
                    c => Number(c.id) === Number(a.classroom_id)
                  );
                  const teacher = teachers.find(
                    t => Number(t.id) === Number(a.teacher_id)
                  );

                  return `
                    <div class="report-next-item">
                      <strong>${escapeHtml(a.titulo)}</strong>
                      <span>
                        ${escapeHtml(a.tipo || '—')} ·
                        ${escapeHtml(classroom?.nome || 'Turma')} ·
                        ${escapeHtml(teacher?.nome || 'Professor')}
                      </span>
                      <small>${formatDateTime(a.data)}</small>
                    </div>
                  `;
                }).join('')
              : '<p class="muted-text">Nenhuma avaliação futura.</p>'
          }
        </section>
      </div>
    `)}

    <div class="report-bottom-action">
      <button class="mini-button mini-button--primary" data-open-assessments>
        Abrir todas as avaliações
      </button>
    </div>
  `;

  bindBack(container, navigate);
  container.querySelector('[data-open-assessments]')
    ?.addEventListener('click', () => navigate('assessments'));
}
