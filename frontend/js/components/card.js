import { icon } from "./icons.js";

export function shortcutCard(label, route, iconName = "grid") {
    return `<article class="shortcut-card"><span class="shortcut-icon">${icon(iconName)}</span><strong>${label}</strong><button class="shortcut-action" type="button" data-route="${route}" aria-label="Abrir ${label}">Ver</button></article>`;
}
