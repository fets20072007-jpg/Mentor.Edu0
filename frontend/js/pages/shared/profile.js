import { getMe, updateMe, changeMyPassword } from "../../api/users.js";
import { setCachedUser } from "../../core/session.js";
import { escapeHtml } from "../../core/format.js";
import { pageHeader, surface } from "./page-ui.js";
import { showToast } from "../../components/toast.js";

const norm = value => String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();

export async function renderProfile(container) {
    let user = await getMe();
    const isTeacher = norm(user.tipo) === "professor";

    const render = () => {
        const teacherFields = `
          <label>Nome<input name="nome" value="${escapeHtml(user.nome || "")}" required></label>
          <label>E-mail<input name="email" type="email" value="${escapeHtml(user.email || "")}" required></label>
          <label>Escola<input name="escola" value="${escapeHtml(user.escola || "")}"></label>
          <label>Idade<input name="idade" type="number" min="1" value="${escapeHtml(user.idade ?? "")}"></label>
          <label class="form-span-2">Bio<textarea name="bio" rows="3">${escapeHtml(user.bio || "")}</textarea></label>`;

        const defaultFields = `
          <label>Nome<input name="nome" value="${escapeHtml(user.nome || "")}" required></label>
          <label>E-mail<input name="email" type="email" value="${escapeHtml(user.email || "")}" required></label>
          <label>Escola<input name="escola" value="${escapeHtml(user.escola || "")}"></label>
          <label>Série<input name="serie" value="${escapeHtml(user.serie || "")}"></label>
          <label>Idade<input name="idade" type="number" min="1" value="${escapeHtml(user.idade ?? "")}"></label>
          <label>Horas de estudo/dia<input name="horas_estudo" type="number" min="0" value="${escapeHtml(user.horas_estudo ?? "")}"></label>
          <label class="form-span-2">Bio<textarea name="bio" rows="3">${escapeHtml(user.bio || "")}</textarea></label>
          <label class="form-span-2">Objetivo<input name="objetivo" value="${escapeHtml(user.objetivo || "")}"></label>
          <label>Matérias favoritas<input name="materias_favoritas" value="${escapeHtml(user.materias_favoritas || "")}"></label>
          <label>Dificuldades<input name="dificuldades" value="${escapeHtml(user.dificuldades || "")}"></label>`;

        container.innerHTML = `
          ${pageHeader("Meu perfil", "Atualize as informações pessoais permitidas pela sua conta.")}
          ${surface(`
            <form class="profile-form" data-profile-form>
              <div class="form-grid">${isTeacher ? teacherFields : defaultFields}</div>
              <div class="form-actions">
                <span class="soft-label">Perfil: ${escapeHtml(user.tipo)}</span>
                <button class="mini-button mini-button--primary" type="submit">Salvar alterações</button>
              </div>
            </form>
          `)}
          ${surface(`
            <form class="profile-form" data-password-form>
              <h3 class="form-title">Mudar senha</h3>
              <div class="form-grid">
                <label>Senha atual<input type="password" name="senha_atual" required autocomplete="current-password"></label>
                <label>Nova senha<input type="password" name="nova_senha" required minlength="6" autocomplete="new-password"></label>
                <label>Confirmar nova senha<input type="password" name="confirmar_senha" required minlength="6" autocomplete="new-password"></label>
              </div>
              <div class="form-actions">
                <button class="mini-button mini-button--primary" type="submit">Alterar senha</button>
              </div>
            </form>
          `)}`;

        container.querySelector("[data-profile-form]")?.addEventListener("submit", async event => {
            event.preventDefault();
            const form = event.currentTarget;
            const data = new FormData(form);
            const button = form.querySelector('button[type="submit"]');
            button.disabled = true;
            const nullableNumber = name => data.get(name) === null || data.get(name) === "" ? null : Number(data.get(name));
            const nullableText = name => data.get(name) === null ? undefined : (String(data.get(name) || "").trim() || null);

            const payload = isTeacher
              ? {
                  nome: nullableText("nome"),
                  email: nullableText("email"),
                  escola: nullableText("escola"),
                  idade: nullableNumber("idade"),
                  bio: nullableText("bio")
                }
              : {
                  nome: nullableText("nome"), email: nullableText("email"),
                  escola: nullableText("escola"), serie: nullableText("serie"),
                  idade: nullableNumber("idade"), horas_estudo: nullableNumber("horas_estudo"),
                  bio: nullableText("bio"), objetivo: nullableText("objetivo"),
                  materias_favoritas: nullableText("materias_favoritas"),
                  dificuldades: nullableText("dificuldades")
                };

            try {
                user = await updateMe(payload);
                setCachedUser(user);
                showToast("Perfil atualizado.","success");
                render();
            } catch (error) {
                button.disabled = false;
                showToast(error.message || "Não foi possível atualizar o perfil.", "error");
            }
        });

        container.querySelector("[data-password-form]")?.addEventListener("submit", async event => {
            event.preventDefault();
            const form = event.currentTarget;
            const data = new FormData(form);
            const atual = String(data.get("senha_atual") || "");
            const nova = String(data.get("nova_senha") || "");
            const confirmar = String(data.get("confirmar_senha") || "");

            if (nova !== confirmar) {
                showToast("A confirmação da nova senha não confere.","error");
                return;
            }
            try {
                await changeMyPassword({ senha_atual: atual, nova_senha: nova });
                form.reset();
                showToast("Senha alterada com sucesso.","success");
            } catch (error) {
                showToast(error.message || "Não foi possível alterar a senha.","error");
            }
        });
    };
    render();
}
