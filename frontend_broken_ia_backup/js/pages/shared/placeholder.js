import { icon } from "../../components/icons.js";
export function renderPlaceholder(container, title, description = "Esta tela será conectada ao backend na próxima etapa do frontend.", iconName = "grid") {
    container.innerHTML = `<section class="page-head"><h2>${title}</h2><p>Mentor.Edu</p></section><section class="placeholder-panel"><div><span class="placeholder-icon">${icon(iconName)}</span><h2>${title}</h2><p>${description}</p></div></section>`;
}
