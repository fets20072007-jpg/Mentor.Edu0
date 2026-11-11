import { icon } from "./icons.js";
export function emptyState(title, description, iconName = "grid") {
    return `<div class="empty-state">${icon(iconName, "placeholder-icon")}<div><strong>${title}</strong><p>${description}</p></div></div>`;
}
