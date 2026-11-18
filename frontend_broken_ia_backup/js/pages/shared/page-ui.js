import { escapeHtml } from "../../core/format.js";
import { icon } from "../../components/icons.js";

export function pageHeader(title, description = "", actions = "") {
    return `<header class="content-head"><div><h2>${escapeHtml(title)}</h2>${description ? `<p>${escapeHtml(description)}</p>` : ""}</div>${actions ? `<div class="content-head-actions">${actions}</div>` : ""}</header>`;
}

export function surface(content, extraClass = "") {
    return `<section class="content-surface ${extraClass}">${content}</section>`;
}

export function metricCard(label, value, iconName = "chart", hint = "") {
    return `<article class="metric-card"><span class="metric-card-icon">${icon(iconName)}</span><div><small>${escapeHtml(label)}</small><strong>${escapeHtml(value)}</strong>${hint ? `<p>${escapeHtml(hint)}</p>` : ""}</div></article>`;
}

export function statusPill(label, tone = "neutral") {
    return `<span class="status-pill status-pill--${tone}">${escapeHtml(label)}</span>`;
}

export function actionButton(label, action, { kind = "ghost", disabled = false, attrs = "" } = {}) {
    return `<button type="button" class="mini-button mini-button--${kind}" data-action="${escapeHtml(action)}" ${disabled ? "disabled" : ""} ${attrs}>${escapeHtml(label)}</button>`;
}

export function emptyBlock(title, description, iconName = "grid") {
    return `<div class="inline-empty">${icon(iconName, "inline-empty-icon")}<strong>${escapeHtml(title)}</strong><p>${escapeHtml(description)}</p></div>`;
}

export function errorBlock(message) {
    return `<div class="inline-alert inline-alert--error"><strong>Não foi possível carregar esta área.</strong><p>${escapeHtml(message || "Tente novamente em instantes.")}</p></div>`;
}
