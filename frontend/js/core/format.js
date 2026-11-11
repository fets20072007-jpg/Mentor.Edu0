export function escapeHtml(value = "") {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

export function formatDate(value, options = {}) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return escapeHtml(value);
    return new Intl.DateTimeFormat("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        ...options,
    }).format(date);
}

export function formatDateTime(value) {
    return formatDate(value, { hour: "2-digit", minute: "2-digit" });
}

export function formatNumber(value, digits = 1) {
    const number = Number(value);
    if (!Number.isFinite(number)) return "—";
    return new Intl.NumberFormat("pt-BR", {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
    }).format(number);
}

export function formatPercent(value, digits = 1) {
    const number = Number(value);
    if (!Number.isFinite(number)) return "—";
    return `${formatNumber(number, digits)}%`;
}

export function firstName(name = "") {
    return String(name).trim().split(/\s+/)[0] || "Aluno";
}

export function normalizeStatus(value = "") {
    return String(value || "").trim().toLowerCase().replaceAll("_", " ");
}

export function safeExternalUrl(value) {
    if (!value) return "";
    try {
        const url = new URL(String(value), window.location.href);
        if (!["http:", "https:"].includes(url.protocol)) return "";
        return url.href;
    } catch {
        return "";
    }
}
