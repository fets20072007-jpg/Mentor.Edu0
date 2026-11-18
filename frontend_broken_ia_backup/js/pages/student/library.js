import { listBooks } from "../../api/library.js";
import { getMySubjects } from "../../api/subjects.js";
import { escapeHtml, safeExternalUrl } from "../../core/format.js";
import { pageHeader, surface, emptyBlock } from "../shared/page-ui.js";

export async function renderStudentLibrary(container) {
    const [books, subjects] = await Promise.all([listBooks(), getMySubjects()]);
    const subjectNames = new Set(subjects.map(item => item.nome));
    const renderBooks = filter => {
        const normalized = String(filter || "").trim().toLowerCase();
        const visible = normalized ? books.filter(book => String(book.disciplina || "").toLowerCase() === normalized) : books;
        const root = container.querySelector("[data-library-results]");
        if (!root) return;
        root.innerHTML = visible.length ? `<div class="entity-grid">${visible.map(book => `<article class="entity-card book-card"><div class="book-cover-placeholder"><span>${escapeHtml((book.titulo || "L").slice(0,1).toUpperCase())}</span></div><div class="entity-card-main"><span class="entity-card-kicker">${escapeHtml(book.disciplina)}</span><h3>${escapeHtml(book.titulo)}</h3><p>${escapeHtml(book.autor)}${book.ano ? ` · ${escapeHtml(book.ano)}` : ""}</p><p>${escapeHtml(book.descricao || "")}</p></div><div class="entity-card-footer"><span class="soft-label">${escapeHtml(book.quantidade_capitulos)} capítulos</span>${safeExternalUrl(book.pdf_url) ? `<a class="mini-button mini-button--primary" href="${escapeHtml(safeExternalUrl(book.pdf_url))}" target="_blank" rel="noopener noreferrer">Abrir</a>` : `<span class="soft-label">Sem PDF</span>`}</div></article>`).join("")}</div>` : emptyBlock("Nenhum livro encontrado", "Não há livros cadastrados para este filtro.", "book");
    };

    container.innerHTML = `${pageHeader("Biblioteca", "Explore os materiais institucionais disponíveis.")}<div class="filter-bar"><label>Disciplina<select data-library-filter><option value="">Todas</option>${[...subjectNames].sort().map(name => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join("")}</select></label></div>${surface(`<div data-library-results></div>`)}`;
    container.querySelector("[data-library-filter]")?.addEventListener("change", event => renderBooks(event.target.value));
    renderBooks("");
}
