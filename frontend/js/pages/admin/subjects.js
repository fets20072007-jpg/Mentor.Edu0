import { listSubjects } from '../../api/subjects.js';
import { listClassrooms } from '../../api/classrooms.js';
import {
  listTeacherProfiles,
  createSubject,
  updateSubject,
  setSubjectActive
} from '../../api/admin.js';
import { escapeHtml } from '../../core/format.js';
import { pageHeader, surface, emptyBlock, statusPill } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

const CATEGORIES = [
  'Ciências da Natureza',
  'Ciências Humanas',
  'Matemática',
  'Linguagens',
  'Técnica / Curso',
  'Outras'
];

function classroomLabel(classroom) {
  if (!classroom) return 'Turma não encontrada';
  return [classroom.nome, classroom.serie].filter(Boolean).join(' · ');
}

export async function renderAdminSubjects(container) {
  const [subs, cls, teachers] = await Promise.all([
    listSubjects(),
    listClassrooms(),
    listTeacherProfiles()
  ]);

  let editingId = null;

  container.innerHTML = `
    ${pageHeader(
      'Disciplinas',
      'Cadastre, edite ou desfaça disciplinas vinculadas a turmas e professores.'
    )}

    ${surface(`
      <form class="inline-form subject-editor" data-form>
        <div class="subject-editor-heading">
          <div>
            <h3 class="form-title" data-form-title>Nova disciplina</h3>
            <p data-form-subtitle>Cadastre uma nova disciplina.</p>
          </div>

          <button type="button" class="mini-button" data-cancel-edit style="display:none">
            Cancelar edição
          </button>
        </div>

        <div class="form-grid">
          <label>
            Nome
            <input name="nome" required>
          </label>

          <label>
            Área / tipo
            <select name="categoria" required>
              ${CATEGORIES.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('')}
            </select>
          </label>

          <label>
            Carga horária
            <input type="number" name="carga_horaria" value="80" min="1" required>
          </label>

          <label>
            Turma
            <select name="classroom_id" required>
              <option value="">Selecione</option>
              ${cls.map(c => `
                <option value="${c.id}">
                  ${escapeHtml(classroomLabel(c))}
                </option>
              `).join('')}
            </select>
          </label>

          <label>
            Professor
            <select name="teacher_id" required>
              <option value="">Selecione</option>
              ${teachers.filter(t => t.ativo).map(t => `
                <option value="${t.id}">
                  ${escapeHtml(t.nome)} · ${escapeHtml(t.especialidade || 'Professor')}
                </option>
              `).join('')}
            </select>
          </label>

          <label class="form-span-2">
            Descrição
            <input name="descricao">
          </label>
        </div>

        <div class="form-actions">
          <button class="mini-button mini-button--primary" data-submit>
            Criar disciplina
          </button>
        </div>
      </form>

      ${
        subs.length
          ? `
            <div class="data-table-wrap subject-table-wrap">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Disciplina</th>
                    <th>Área</th>
                    <th>Turma</th>
                    <th>Professor</th>
                    <th>Carga</th>
                    <th>Status</th>
                    <th>Ações</th>
                  </tr>
                </thead>

                <tbody>
                  ${subs.map(s => {
                    const classroom = cls.find(c => Number(c.id) === Number(s.classroom_id));
                    const teacher = teachers.find(t => Number(t.id) === Number(s.teacher_id));

                    return `
                      <tr class="${s.ativa ? '' : 'subject-row--inactive'}">
                        <td>
                          <strong>${escapeHtml(s.nome)}</strong>
                          ${
                            s.descricao
                              ? `<small class="subject-description">${escapeHtml(s.descricao)}</small>`
                              : ''
                          }
                        </td>

                        <td>${escapeHtml(s.categoria || 'Outras')}</td>

                        <td>
                          ${escapeHtml(
                            classroom
                              ? classroomLabel(classroom)
                              : `Turma #${s.classroom_id}`
                          )}
                        </td>

                        <td>
                          ${escapeHtml(
                            teacher?.nome || `Professor #${s.teacher_id}`
                          )}
                        </td>

                        <td>${Number(s.carga_horaria || 0)}h</td>

                        <td>
                          ${statusPill(
                            s.ativa ? 'Ativa' : 'Inativa',
                            s.ativa ? 'success' : 'neutral'
                          )}
                        </td>

                        <td>
                          <div class="subject-row-actions">
                            <button type="button" class="mini-button subject-action-button" data-edit="${s.id}">
                              Editar
                            </button>

                            ${
                              s.ativa
                                ? `
                                  <button type="button" class="mini-button mini-button--danger subject-action-button" data-disable="${s.id}">
                                    Desfazer
                                  </button>
                                `
                                : `
                                  <button type="button" class="mini-button subject-action-button" data-enable="${s.id}">
                                    Reativar
                                  </button>
                                `
                            }
                          </div>
                        </td>
                      </tr>
                    `;
                  }).join('')}
                </tbody>
              </table>
            </div>
          `
          : emptyBlock('Nenhuma disciplina', 'Cadastre a primeira disciplina.', 'book')
      }
    `)}
  `;

  const form = container.querySelector('[data-form]');
  const formTitle = form.querySelector('[data-form-title]');
  const formSubtitle = form.querySelector('[data-form-subtitle]');
  const submitButton = form.querySelector('[data-submit]');
  const cancelButton = form.querySelector('[data-cancel-edit]');

  function resetForm() {
    editingId = null;
    form.reset();
    form.carga_horaria.value = '80';
    form.categoria.value = 'Outras';
    formTitle.textContent = 'Nova disciplina';
    formSubtitle.textContent = 'Cadastre uma nova disciplina.';
    submitButton.textContent = 'Criar disciplina';
    cancelButton.style.display = 'none';
  }

  function startEdit(subject) {
    editingId = Number(subject.id);

    form.nome.value = subject.nome || '';
    form.categoria.value = subject.categoria || 'Outras';
    form.carga_horaria.value = Number(subject.carga_horaria || 80);
    form.classroom_id.value = String(subject.classroom_id || '');
    form.teacher_id.value = String(subject.teacher_id || '');
    form.descricao.value = subject.descricao || '';

    formTitle.textContent = `Editar disciplina — ${subject.nome}`;
    formSubtitle.textContent = 'Altere os dados e salve.';
    submitButton.textContent = 'Salvar alterações';
    cancelButton.style.display = '';

    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  cancelButton.addEventListener('click', resetForm);

  form.addEventListener('submit', async event => {
    event.preventDefault();

    const payload = {
      nome: form.nome.value.trim(),
      categoria: form.categoria.value,
      carga_horaria: Number(form.carga_horaria.value || 80),
      descricao: form.descricao.value.trim() || null,
      teacher_id: Number(form.teacher_id.value),
      classroom_id: Number(form.classroom_id.value)
    };

    submitButton.disabled = true;

    try {
      if (editingId) {
        await updateSubject(editingId, payload);
        showToast('Disciplina atualizada.', 'success');
      } else {
        await createSubject(payload);
        showToast('Disciplina criada.', 'success');
      }

      await renderAdminSubjects(container);
    } catch (error) {
      submitButton.disabled = false;
      showToast(
        error.message ||
        (editingId
          ? 'Não foi possível atualizar a disciplina.'
          : 'Não foi possível criar a disciplina.'),
        'error'
      );
    }
  });

  container.querySelectorAll('[data-edit]').forEach(button => {
    button.addEventListener('click', () => {
      const id = Number(button.dataset.edit);
      const subject = subs.find(s => Number(s.id) === id);
      if (subject) startEdit(subject);
    });
  });

  container.querySelectorAll('[data-disable]').forEach(button => {
    button.addEventListener('click', async () => {
      const id = Number(button.dataset.disable);
      const subject = subs.find(s => Number(s.id) === id);
      if (!subject) return;

      const confirmed = window.confirm(
        `Desfazer o cadastro de "${subject.nome}"?\n\n` +
        'A disciplina ficará inativa e deixará de aparecer para professor e alunos. ' +
        'Nada será apagado definitivamente e você poderá reativá-la depois.'
      );

      if (!confirmed) return;

      button.disabled = true;

      try {
        await setSubjectActive(id, false);
        showToast('Disciplina desativada. Você pode reativá-la depois.', 'success');
        await renderAdminSubjects(container);
      } catch (error) {
        button.disabled = false;
        showToast(
          error.message || 'Não foi possível desfazer o cadastro.',
          'error'
        );
      }
    });
  });

  container.querySelectorAll('[data-enable]').forEach(button => {
    button.addEventListener('click', async () => {
      const id = Number(button.dataset.enable);
      button.disabled = true;

      try {
        await setSubjectActive(id, true);
        showToast('Disciplina reativada.', 'success');
        await renderAdminSubjects(container);
      } catch (error) {
        button.disabled = false;
        showToast(
          error.message || 'Não foi possível reativar a disciplina.',
          'error'
        );
      }
    });
  });
}
