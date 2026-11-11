export function loadingMarkup(label = "Carregando...") {
    return `<div class="page-loading" aria-live="polite"><span class="spinner" aria-hidden="true"></span><p>${label}</p></div>`;
}
