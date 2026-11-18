import { getMe, updateMe } from "../../api/users.js";
import { setCachedUser } from "../../core/session.js";
import { escapeHtml } from "../../core/format.js";
import { pageHeader, surface } from "./page-ui.js";
import { showToast } from "../../components/toast.js";

const norm = value => String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const nullableNumber = (data, name) => {
  const value = data.get(name);
  return value === null || value === "" ? null : Number(value);
};
const nullableText = (data, name) => {
  const value = data.get(name);
  return value === null ? undefined : (String(value || "").trim() || null);
};

export async function renderProfile(container) {
  let user = await getMe();
  const isAdmin = norm(user.tipo).includes("administr");

  const render = () => {
    if (isAdmin) {
      container.innerHTML = `
        ${pageHeader("Meu perfil","Gerencie seus dados pessoais e institucionais.")}
        <div class="admin-profile-shell">
          ${surface(`
            <div class="admin-profile-head">
              <div class="admin-profile-avatar">${escapeHtml((user.nome || "A").slice(0,2).toUpperCase())}</div>
              <div>
                <span class="admin-profile-eyebrow">Perfil institucional</span>
                <h3>${escapeHtml(user.nome || "Administrador")}</h3>
                <p>${escapeHtml(user.email || "")}</p>
              </div>
              <span class="admin-role-chip">Administração</span>
            </div>

            <form class="profile-form admin-profile-form" data-profile-form>
              <div class="admin-form-section">
                <div class="admin-section-title">
                  <h4>Informações pessoais</h4>
                  <p>Dados básicos da sua conta institucional.</p>
                </div>

                <div class="form-grid admin-profile-grid">
                  <label><span>Nome</span><input name="nome" value="${escapeHtml(user.nome || "")}" required></label>
                  <label><span>E-mail institucional</span><input name="email" type="email" value="${escapeHtml(user.email || "")}" required></label>
                  <label><span>Escola / instituição</span><input name="escola" value="${escapeHtml(user.escola || "")}" placeholder="Nome da instituição"></label>
                  <label><span>Idade</span><input name="idade" type="number" min="1" value="${escapeHtml(user.idade ?? "")}" placeholder="Opcional"></label>
                  <label class="form-span-2"><span>Bio / apresentação</span><textarea name="bio" rows="4" placeholder="Uma breve apresentação institucional.">${escapeHtml(user.bio || "")}</textarea></label>
                </div>
              </div>

              <div class="admin-profile-footer">
                <div class="admin-account-info">
                  <span>Tipo de conta</span>
                  <strong>Administração</strong>
                </div>
                <button class="mini-button mini-button--primary admin-save-button" type="submit">Salvar alterações</button>
              </div>
            </form>
          `)}
        </div>
      `;

      container.querySelector("[data-profile-form]")?.addEventListener("submit", async event => {
        event.preventDefault();
        const form = event.currentTarget;
        const data = new FormData(form);
        const button = form.querySelector('button[type="submit"]');
        button.disabled = true;
        try {
          user = await updateMe({
            nome: nullableText(data, "nome"),
            email: nullableText(data, "email"),
            escola: nullableText(data, "escola"),
            idade: nullableNumber(data, "idade"),
            bio: nullableText(data, "bio")
          });
          setCachedUser(user);
          showToast("Perfil administrativo atualizado.", "success");
          render();
        } catch (error) {
          button.disabled = false;
          showToast(error.message || "Não foi possível atualizar o perfil.", "error");
        }
      });
      return;
    }

    container.innerHTML = `${pageHeader("Meu perfil","Atualize as informações pessoais permitidas pela sua conta.")}${surface(`
      <form class="profile-form" data-profile-form>
        <div class="form-grid">
          <label>Nome<input name="nome" value="${escapeHtml(user.nome || "")}" required></label>
          <label>E-mail<input name="email" type="email" value="${escapeHtml(user.email || "")}" required></label>
          <label>Escola<input name="escola" value="${escapeHtml(user.escola || "")}"></label>
          <label>Série<input name="serie" value="${escapeHtml(user.serie || "")}"></label>
          <label>Idade<input name="idade" type="number" min="1" value="${escapeHtml(user.idade ?? "")}"></label>
          <label>Horas de estudo/dia<input name="horas_estudo" type="number" min="0" value="${escapeHtml(user.horas_estudo ?? "")}"></label>
          <label class="form-span-2">Bio<textarea name="bio" rows="3">${escapeHtml(user.bio || "")}</textarea></label>
          <label class="form-span-2">Objetivo<input name="objetivo" value="${escapeHtml(user.objetivo || "")}"></label>
          <label>Matérias favoritas<input name="materias_favoritas" value="${escapeHtml(user.materias_favoritas || "")}"></label>
          <label>Dificuldades<input name="dificuldades" value="${escapeHtml(user.dificuldades || "")}"></label>
        </div>
        <div class="form-actions"><span class="soft-label">Perfil: ${escapeHtml(user.tipo)}</span><button class="mini-button mini-button--primary" type="submit">Salvar alterações</button></div>
      </form>
    `)}`;

    container.querySelector("[data-profile-form]")?.addEventListener("submit", async event => {
      event.preventDefault();
      const form = event.currentTarget;
      const data = new FormData(form);
      const button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      try {
        user = await updateMe({
          nome: nullableText(data, "nome"),
          email: nullableText(data, "email"),
          escola: nullableText(data, "escola"),
          serie: nullableText(data, "serie"),
          idade: nullableNumber(data, "idade"),
          horas_estudo: nullableNumber(data, "horas_estudo"),
          bio: nullableText(data, "bio"),
          objetivo: nullableText(data, "objetivo"),
          materias_favoritas: nullableText(data, "materias_favoritas"),
          dificuldades: nullableText(data, "dificuldades")
        });
        setCachedUser(user);
        showToast("Perfil atualizado.", "success");
        render();
      } catch (error) {
        button.disabled = false;
        showToast(error.message || "Não foi possível atualizar o perfil.", "error");
      }
    });
  };

  render();
}
