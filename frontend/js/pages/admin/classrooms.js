import { listClassrooms } from '../../api/classrooms.js';
import {
  getAdminStudents,
  getClassroomTeachers,
  createClassroom,
  setClassroomDt
} from '../../api/admin.js';
import { getClassroomEnrollments } from '../../api/enrollments.js';
import { escapeHtml } from '../../core/format.js';
import {
  pageHeader,
  surface,
  emptyBlock,
  statusPill
} from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

export async function renderAdminClassrooms(container){
  const [rows, students] = await Promise.all([
    listClassrooms(),
    getAdminStudents()
  ]);

  const details = await Promise.all(
    rows.map(async classroom => {
      const [teachers, enrollments] = await Promise.all([
        getClassroomTeachers(classroom.id).catch(() => []),
        getClassroomEnrollments(classroom.id).catch(() => [])
      ]);

      const activeEnrollments = enrollments.filter(e => e.ativo !== false);

      const enrolledStudents = activeEnrollments
        .map(enrollment => {
          const student = students.find(
            s => Number(s.id) === Number(enrollment.user_id)
          );

          return student
            ? {
                ...student,
                enrollment_id: enrollment.id,
                enrollment_date: enrollment.data_matricula
              }
            : null;
        })
        .filter(Boolean);

      return {
        classroom,
        teachers,
        students: enrolledStudents
      };
    })
  );

  container.innerHTML = `
    ${pageHeader(
      'Turmas',
      'Crie turmas e abra cada uma para visualizar alunos e professores vinculados.'
    )}

    ${surface(`
      <form class="inline-form" data-form>
        <h3 class="form-title">Nova turma</h3>

        <div class="form-grid">
          <label>
            Nome
            <input name="nome" required placeholder="3º A">
          </label>

          <label>
            Série
            <input name="serie" required placeholder="3º ano">
          </label>

          <label>
            Turno
            <select name="turno">
              <option>Manhã</option>
              <option>Tarde</option>
              <option>Noite</option>
              <option>Integral</option>
            </select>
          </label>

          <label>
            Sala
            <input name="sala" required>
          </label>

          <label>
            Ano
            <input
              type="number"
              name="ano"
              value="${new Date().getFullYear()}"
              required
            >
          </label>

          <label>
            Capacidade
            <input
              type="number"
              name="capacidade"
              value="40"
              min="1"
            >
          </label>
        </div>

        <div class="form-actions">
          <button class="mini-button mini-button--primary">
            Criar turma
          </button>
        </div>
      </form>

      ${
        details.length
          ? `
            <div class="entity-grid">
              ${details.map(({ classroom, teachers, students }) => `
                <article class="entity-card">
                  <div class="entity-card-main">
                    <span class="entity-card-kicker">
                      ${escapeHtml(classroom.turno)} · ${classroom.ano}
                    </span>

                    <h3>${escapeHtml(classroom.nome)}</h3>

                    <p>
                      ${escapeHtml(classroom.serie)}
                      · Sala ${escapeHtml(classroom.sala)}
                      · capacidade ${classroom.capacidade}
                    </p>

                    <p>
                      <strong>${students.length}</strong> aluno(s)
                      ·
                      <strong>${teachers.length}</strong> professor(es)
                    </p>
                  </div>

                  <div class="entity-card-footer">
                    <button
                      class="mini-button"
                      data-class-detail="${classroom.id}"
                      data-view="students"
                    >
                      Alunos
                    </button>

                    <button
                      class="mini-button"
                      data-class-detail="${classroom.id}"
                      data-view="teachers"
                    >
                      Professores
                    </button>

                    ${statusPill(
                      classroom.ativa ? 'Ativa' : 'Inativa',
                      classroom.ativa ? 'success' : 'neutral'
                    )}
                  </div>
                </article>
              `).join('')}
            </div>

            <div data-detail class="page-section-gap"></div>
          `
          : emptyBlock(
              'Nenhuma turma',
              'Crie a primeira turma para começar.',
              'users'
            )
      }
    `)}
  `;

  container.querySelector('[data-form]')?.addEventListener(
    'submit',
    async event => {
      event.preventDefault();

      const form = event.currentTarget;

      try {
        await createClassroom({
          nome: form.nome.value,
          serie: form.serie.value,
          turno: form.turno.value,
          sala: form.sala.value,
          ano: Number(form.ano.value),
          capacidade: Number(form.capacidade.value || 40)
        });

        showToast('Turma criada.', 'success');
        await renderAdminClassrooms(container);
      } catch (error) {
        showToast(
          error.message || 'Não foi possível criar a turma.',
          'error'
        );
      }
    }
  );

  container.querySelectorAll('[data-class-detail]').forEach(button => {
    button.addEventListener('click', () => {
      const item = details.find(
        entry =>
          Number(entry.classroom.id) ===
          Number(button.dataset.classDetail)
      );

      const target = container.querySelector('[data-detail]');

      if (!item || !target) return;

      if (button.dataset.view === 'students') {
        target.innerHTML = surface(`
          <div class="section-heading">
            <h3>
              ${escapeHtml(item.classroom.nome)} · Alunos
            </h3>
            <p>Estudantes com matrícula ativa nesta turma.</p>
          </div>

          ${
            item.students.length
              ? `
                <div class="data-table-wrap">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>Aluno</th>
                        <th>E-mail</th>
                        <th>Matrícula</th>
                        <th>Contato</th>
                        <th>Data da matrícula</th>
                      </tr>
                    </thead>

                    <tbody>
                      ${item.students.map(student => `
                        <tr>
                          <td>
                            <strong>
                              ${escapeHtml(student.nome || '—')}
                            </strong>
                          </td>

                          <td>
                            ${escapeHtml(student.email || '—')}
                          </td>

                          <td>
                            ${escapeHtml(student.matricula || '—')}
                          </td>

                          <td>
                            ${escapeHtml(
                              student.contato1 ||
                              student.contato2 ||
                              student.telefone ||
                              '—'
                            )}
                          </td>

                          <td>
                            ${
                              student.enrollment_date
                                ? new Date(
                                    student.enrollment_date
                                  ).toLocaleString('pt-BR')
                                : '—'
                            }
                          </td>
                        </tr>
                      `).join('')}
                    </tbody>
                  </table>
                </div>
              `
              : emptyBlock(
                  'Nenhum aluno',
                  'Esta turma ainda não possui matrículas ativas.',
                  'users'
                )
          }
        `);
      } else {
        target.innerHTML = surface(`
          <div class="section-heading">
            <h3>
              ${escapeHtml(item.classroom.nome)} · Professores
            </h3>
            <p>Docentes que lecionam nesta turma.</p>
          </div>

          ${
            item.teachers.length
              ? `
                <div class="data-table-wrap">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>Professor</th>
                        <th>Disciplinas</th>
                        <th>DT</th>
                      </tr>
                    </thead>

                    <tbody>
                      ${item.teachers.map(teacher => `
                        <tr>
                          <td>${escapeHtml(teacher.nome || '—')}</td>
                          <td>
                            ${escapeHtml(
                              (teacher.disciplinas || []).join(', ') || '—'
                            )}
                          </td>
                          <td>${teacher.is_dt ? 'Sim' : 'Não'}</td>
                        </tr>
                      `).join('')}
                    </tbody>
                  </table>
                </div>
              `
              : emptyBlock(
                  'Nenhum professor',
                  'Ainda não existem professores vinculados por disciplinas.',
                  'users'
                )
          }
        `);
      }

      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    });
  });
}

export async function renderAdminDt(container){
  const classrooms = await listClassrooms();

  const cards = await Promise.all(
    classrooms.map(async c => ({
      c,
      teachers: await getClassroomTeachers(c.id).catch(() => [])
    }))
  );

  container.innerHTML = `
    ${pageHeader(
      'Diretores de turma',
      'Defina o DT entre os professores que já lecionam em cada turma.'
    )}

    ${surface(
      cards.length
        ? `
          <div class="entity-grid">
            ${cards.map(({ c, teachers }) => `
              <article class="entity-card">
                <div class="entity-card-main">
                  <span class="entity-card-kicker">
                    ${escapeHtml(c.serie)} · ${escapeHtml(c.turno)}
                  </span>

                  <h3>${escapeHtml(c.nome)}</h3>

                  <label class="admin-control">
                    Diretor de turma

                    <select data-dt="${c.id}">
                      <option value="">Sem DT</option>

                      ${teachers.map(t => `
                        <option
                          value="${t.teacher_id}"
                          ${t.is_dt ? 'selected' : ''}
                        >
                          ${escapeHtml(t.nome)}
                          ${
                            t.disciplinas?.length
                              ? ` · ${escapeHtml(
                                  t.disciplinas.join(', ')
                                )}`
                              : ''
                          }
                        </option>
                      `).join('')}
                    </select>
                  </label>
                </div>

                <div class="entity-card-footer">
                  <button
                    class="mini-button mini-button--primary"
                    data-save-dt="${c.id}"
                  >
                    Salvar DT
                  </button>
                </div>
              </article>
            `).join('')}
          </div>
        `
        : emptyBlock(
            'Nenhuma turma',
            'Não existem turmas disponíveis.',
            'users'
          )
    )}
  `;

  container.querySelectorAll('[data-save-dt]').forEach(button => {
    button.addEventListener('click', async () => {
      const id = Number(button.dataset.saveDt);
      const select = container.querySelector(`[data-dt="${id}"]`);

      try {
        await setClassroomDt(
          id,
          select.value ? Number(select.value) : null
        );

        showToast(
          'Diretor de turma atualizado.',
          'success'
        );
      } catch (error) {
        showToast(
          error.message || 'Não foi possível definir o DT.',
          'error'
        );
      }
    });
  });
}
