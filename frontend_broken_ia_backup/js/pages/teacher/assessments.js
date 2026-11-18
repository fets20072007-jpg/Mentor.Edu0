import { listAssessments } from "../../api/assessments.js";
import { deleteAssessment } from "../../api/teacher.js";
import { escapeHtml, formatDateTime } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "../shared/page-ui.js";
import { showToast } from "../../components/toast.js";

export async function renderTeacherAssessments(container, navigate) {
  const rows = await listAssessments();

  container.innerHTML = `
    ${pageHeader(
      "Minhas avaliações",
      "Avaliações vinculadas às suas disciplinas.",
      `<button class="mini-button mini-button--primary" data-new>Criar avaliação</button>`
    )}

    ${surface(
      rows.length
        ? `
          <div class="entity-grid">
            ${rows.map(a => `
              <article class="entity-card">
                <div class="entity-card-main">
                  <span class="entity-card-kicker">
                    ${escapeHtml(a.tipo)} · ${formatDateTime(a.data)}
                  </span>

                  <h3>${escapeHtml(a.titulo)}</h3>
                  <p>${escapeHtml(a.descricao || "")}</p>
                </div>

                <div class="entity-card-footer">
                  <div class="assessment-card-meta">
                    ${statusPill(
                      a.ativa ? "Ativa" : "Rascunho",
                      a.ativa ? "success" : "neutral"
                    )}
                    <span class="soft-label">
                      Valor: ${escapeHtml(a.valor)}
                    </span>
                  </div>

                  <button
                    type="button"
                    class="mini-button mini-button--danger"
                    data-delete-assessment="${a.id}"
                    data-title="${escapeHtml(a.titulo)}"
                  >
                    Excluir
                  </button>
                </div>
              </article>
            `).join("")}
          </div>
        `
        : emptyBlock(
            "Nenhuma avaliação",
            "Crie sua primeira avaliação para uma disciplina.",
            "clipboard"
          )
    )}
  `;

  container
    .querySelector("[data-new]")
    ?.addEventListener("click", () => navigate("assessment-create"));

  container
    .querySelectorAll("[data-delete-assessment]")
    .forEach(button => {
      button.addEventListener("click", async () => {
        const id = Number(button.dataset.deleteAssessment);
        const title = button.dataset.title || "esta avaliação";

        const confirmed = window.confirm(
          `Excluir "${title}"?\n\n` +
          "Essa ação é permanente e também removerá as questões, " +
          "respostas e notas vinculadas a esta avaliação."
        );

        if (!confirmed) return;

        button.disabled = true;

        try {
          await deleteAssessment(id);
          showToast("Avaliação excluída.", "success");
          await renderTeacherAssessments(container, navigate);
        } catch (error) {
          button.disabled = false;
          showToast(
            error.message || "Não foi possível excluir a avaliação.",
            "error"
          );
        }
      });
    });
}
