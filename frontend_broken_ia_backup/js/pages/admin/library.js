import { listBooks, listBookChapters } from '../../api/library.js';
import { escapeHtml, safeExternalUrl } from '../../core/format.js';
import { pageHeader, surface, emptyBlock, metricCard } from '../shared/page-ui.js';

function bookCard(book){
  const url = safeExternalUrl(book.pdf_url);
  return `<article class="entity-card library-admin-card">
    <div class="entity-card-main"><span class="entity-card-kicker">${escapeHtml(book.disciplina || 'Biblioteca')}</span><h3>${escapeHtml(book.titulo)}</h3><p>${escapeHtml(book.autor || 'Autor não informado')}${book.ano ? ` · ${book.ano}` : ''}</p><p>${escapeHtml(book.descricao || 'Sem descrição cadastrada.')}</p></div>
    <div class="entity-card-footer"><span class="soft-label">${Number(book.quantidade_capitulos || 0)} capítulos</span>${url ? `<a class="mini-button" href="${escapeHtml(url)}" target="_blank" rel="noopener">Abrir PDF</a>` : '<span class="soft-label">Sem PDF</span>'}</div>
  </article>`;
}

export async function renderAdminLibraryBooks(container){
  const books = await listBooks();
  const subjects = new Set(books.map(b => b.disciplina).filter(Boolean));
  container.innerHTML = `${pageHeader('Biblioteca institucional','Consulte o acervo organizado pelo Suporte. A Administração acompanha a disponibilidade dos materiais.')}
    <div class="metric-grid">${metricCard('Livros', String(books.length), 'book')}${metricCard('Disciplinas', String(subjects.size), 'school')}${metricCard('Com PDF', String(books.filter(b=>safeExternalUrl(b.pdf_url)).length), 'file')}</div>
    ${surface(books.length ? `<div class="entity-grid">${books.map(bookCard).join('')}</div>` : emptyBlock('Biblioteca vazia','O Suporte ainda não cadastrou livros institucionais.','book'))}`;
}

export async function renderAdminLibraryChapters(container){
  const books = await listBooks();
  container.innerHTML = `${pageHeader('Capítulos da biblioteca','Consulte a estrutura dos livros institucionais sem alterar o acervo.')}${surface(books.length ? `<div class="filter-bar"><label>Livro<select data-admin-book><option value="">Selecione um livro</option>${books.map(b=>`<option value="${b.id}">${escapeHtml(b.titulo)} · ${escapeHtml(b.disciplina || 'Sem disciplina')}</option>`).join('')}</select></label></div><div data-admin-chapters>${emptyBlock('Selecione um livro','Os capítulos cadastrados aparecerão aqui.','file')}</div>` : emptyBlock('Nenhum livro','Não há livros disponíveis para consulta.','book'))}`;
  const select = container.querySelector('[data-admin-book]');
  const host = container.querySelector('[data-admin-chapters]');
  select?.addEventListener('change', async () => {
    if (!select.value) { host.innerHTML = emptyBlock('Selecione um livro','Os capítulos cadastrados aparecerão aqui.','file'); return; }
    const rows = await listBookChapters(Number(select.value));
    host.innerHTML = rows.length ? `<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Nº</th><th>Capítulo</th><th>Páginas</th><th>Descrição</th></tr></thead><tbody>${rows.map(c=>`<tr><td>${c.numero}</td><td><strong>${escapeHtml(c.titulo)}</strong></td><td>${c.pagina_inicio}–${c.pagina_fim}</td><td>${escapeHtml(c.descricao || '—')}</td></tr>`).join('')}</tbody></table></div>` : emptyBlock('Sem capítulos','Este livro ainda não possui capítulos cadastrados.','file');
  });
}

export async function renderAdminLibraryContent(container){
  const books = await listBooks();
  const chapterLists = await Promise.all(books.map(async b => { try { return await listBookChapters(b.id); } catch { return []; } }));
  const chapters = chapterLists.reduce((sum, rows) => sum + rows.length, 0);
  const disciplines = [...new Set(books.map(b=>b.disciplina).filter(Boolean))].sort();
  container.innerHTML = `${pageHeader('Conteúdos da biblioteca','Visão geral do acervo disponível aos usuários da plataforma.')}
    <div class="metric-grid">${metricCard('Livros',String(books.length),'book')}${metricCard('Capítulos',String(chapters),'file')}${metricCard('Áreas',String(disciplines.length),'school')}</div>
    ${surface(disciplines.length ? `<div class="content-catalog">${disciplines.map(name=>{const items=books.filter(b=>b.disciplina===name);return `<article class="catalog-row"><div><span class="entity-card-kicker">Disciplina</span><h3>${escapeHtml(name)}</h3><p>${items.length} ${items.length===1?'livro disponível':'livros disponíveis'}</p></div><div class="catalog-tags">${items.slice(0,4).map(b=>`<span class="soft-label">${escapeHtml(b.titulo)}</span>`).join('')}${items.length>4?`<span class="soft-label">+${items.length-4}</span>`:''}</div></article>`;}).join('')}</div>` : emptyBlock('Sem conteúdos','O acervo ainda não possui disciplinas cadastradas.','book'))}`;
}
