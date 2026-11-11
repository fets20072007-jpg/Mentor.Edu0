import { getMe, updateMe } from "../../api/users.js";
import { setCachedUser } from "../../core/session.js";
import { escapeHtml } from "../../core/format.js";
import { pageHeader, surface } from "./page-ui.js";
import { showToast } from "../../components/toast.js";

export async function renderProfile(container) {
    let user = await getMe();
    const render = () => {
        container.innerHTML = `${pageHeader("Meu perfil", "Atualize as informações pessoais permitidas pela sua conta.")}${surface(`<form class="profile-form" data-profile-form><div class="form-grid"><label>Nome<input name="nome" value="${escapeHtml(user.nome || "")}" required></label><label>E-mail<input name="email" type="email" value="${escapeHtml(user.email || "")}" required></label><label>Escola<input name="escola" value="${escapeHtml(user.escola || "")}"></label><label>Série<input name="serie" value="${escapeHtml(user.serie || "")}"></label><label>Idade<input name="idade" type="number" min="1" value="${escapeHtml(user.idade ?? "")}"></label><label>Horas de estudo/dia<input name="horas_estudo" type="number" min="0" value="${escapeHtml(user.horas_estudo ?? "")}"></label><label class="form-span-2">Bio<textarea name="bio" rows="3">${escapeHtml(user.bio || "")}</textarea></label><label class="form-span-2">Objetivo<input name="objetivo" value="${escapeHtml(user.objetivo || "")}"></label><label>Matérias favoritas<input name="materias_favoritas" value="${escapeHtml(user.materias_favoritas || "")}"></label><label>Dificuldades<input name="dificuldades" value="${escapeHtml(user.dificuldades || "")}"></label></div><div class="form-actions"><span class="soft-label">Perfil: ${escapeHtml(user.tipo)}</span><button class="mini-button mini-button--primary" type="submit">Salvar alterações</button></div></form>`)}`;
        container.querySelector("[data-profile-form]")?.addEventListener("submit", async event => {
            event.preventDefault(); const form = event.currentTarget; const data = new FormData(form); const button = form.querySelector('button[type="submit"]'); button.disabled = true;
            const nullableNumber = name => data.get(name) === "" ? null : Number(data.get(name));
            const nullableText = name => String(data.get(name) || "").trim() || null;
            const payload = { nome: nullableText("nome"), email: nullableText("email"), escola: nullableText("escola"), serie: nullableText("serie"), idade: nullableNumber("idade"), horas_estudo: nullableNumber("horas_estudo"), bio: nullableText("bio"), objetivo: nullableText("objetivo"), materias_favoritas: nullableText("materias_favoritas"), dificuldades: nullableText("dificuldades") };
            try { user = await updateMe(payload); setCachedUser(user); showToast("Perfil atualizado."); render(); }
            catch (error) { button.disabled = false; showToast(error.message || "Não foi possível atualizar o perfil.", "error"); }
        });
    };
    render();
}
