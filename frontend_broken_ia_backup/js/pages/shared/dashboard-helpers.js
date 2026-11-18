import { shortcutCard } from "../../components/card.js";

export function dashboardShell({ title, message = "", shortcuts = [] }) {
    return `<section class="welcome-strip"><div><h2>${title}</h2>${message ? `<p>${message}</p>` : ""}</div><div class="hero-illustration" aria-hidden="true"><span class="hero-books"></span><span class="hero-cap"></span></div></section><section class="shortcut-grid">${shortcuts.map(item => shortcutCard(item.label, item.route, item.icon)).join("")}</section>`;
}

export function bindDashboardShortcuts(container, navigate) {
    container.querySelectorAll("[data-route]").forEach(button => button.addEventListener("click", () => navigate(button.dataset.route)));
}

export async function optional(promise, fallback) {
    try { return await promise; } catch { return fallback; }
}
