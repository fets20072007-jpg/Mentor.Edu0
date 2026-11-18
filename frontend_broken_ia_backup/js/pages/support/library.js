import { listBooks, createBook, listBookChapters, createBookChapter } from '../../api/library.js';
import { escapeHtml, safeExternalUrl } from '../../core/format.js';
import { pageHeader, surface, emptyBlock } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

export async function renderSupportBooks(container){
  const books = await listBooks();
  container.innerHTML = `${pageHeader('Livros institucionais','Cadastre e organize a estrutura base da biblioteca digital.')}${surface(`
    <form class="inline-form" data-book-form><h3 class="form-title">Novo livro</h3><div class="form-grid">
      <label>Título<input name="titulo" required></label><label>Disciplina<input name="disciplina" required></label>
      <label>Autor<input name="autor" required></label><label>Editora<input name="editora"></label>
      <label>Ano<input name="ano" type="number" min="1000" max="2100"></label><label>Quantidade de capítulos<input name="quantidade_capitulos" type="number" min="0" value="0"></label>
      <label class="form-span-2">URL do PDF<input name="pdf_url" type="url" placeholder="https://..."></label><label class="form-span-2">Descrição<textarea name="descricao" rows="3"></textarea></label>
    </div><div class="form-actions"><button class="mini-button mini-button--primary">Cadastrar livro</button></div></form>
    ${books.length?`<div class="entity-grid">${books.map(bookCard).join('')}</div>`:emptyBlock('Biblioteca vazia','Cadastre o primeiro livro institucional.','book')}
  `)}`;
  container.querySelector('[data-book-form]')?.addEventListener('submit',async e=>{e.preventDefault();const f=e.currentTarget;await createBook({titulo:f.titulo.value.trim(),disciplina:f.disciplina.value.trim(),autor:f.autor.value.trim(),editora:f.editora.value.trim()||null,ano:f.ano.value?Number(f.ano.value):null,quantidade_capitulos:Number(f.quantidade_capitulos.value||0),pdf_url:f.pdf_url.value.trim()||null,descricao:f.descricao.value.trim()||null});showToast('Livro cadastrado.','success');await renderSupportBooks(container);});
}

function bookCard(b){ const url=safeExternalUrl(b.pdf_url); return `<article class="entity-card"><div class="entity-card-icon">${escapeHtml((b.titulo||'L')[0])}</div><div class="entity-card-body"><span>${escapeHtml(b.disciplina||'Biblioteca')}</span><h3>${escapeHtml(b.titulo)}</h3><p>${escapeHtml(b.autor||'—')}${b.ano?` · ${b.ano}`:''}</p><small>${escapeHtml(b.descricao||'Sem descrição.')}</small></div><div class="entity-card-footer"><strong>${Number(b.quantidade_capitulos||0)} capítulos</strong>${url?`<a class="mini-button mini-button--ghost" href="${escapeHtml(url)}" target="_blank" rel="noopener">Abrir PDF</a>`:''}</div></article>`; }

export async function renderSupportChapters(container){
  const books = await listBooks();
  container.innerHTML = `${pageHeader('Capítulos','Selecione um livro para consultar e cadastrar capítulos.')}${surface(`
    ${books.length?`<div class="attendance-filter-card"><label>Livro<select data-book-select><option value="">Selecione</option>${books.map(b=>`<option value="${b.id}">${escapeHtml(b.titulo)} · ${escapeHtml(b.disciplina)}</option>`).join('')}</select></label></div><div data-chapter-host>${emptyBlock('Selecione um livro','Os capítulos cadastrados aparecerão aqui.','file')}</div>`:emptyBlock('Nenhum livro','Cadastre um livro antes de adicionar capítulos.','book')}
  `)}`;
  container.querySelector('[data-book-select]')?.addEventListener('change',async e=>loadBookChapters(container,Number(e.target.value)));
}

async function loadBookChapters(container,bookId){
  const host=container.querySelector('[data-chapter-host]'); if(!bookId){host.innerHTML=emptyBlock('Selecione um livro','Os capítulos cadastrados aparecerão aqui.','file');return;}
  const chapters=await listBookChapters(bookId);
  host.innerHTML=`<form class="inline-form" data-chapter-form><h3 class="form-title">Novo capítulo</h3><div class="form-grid"><label>Título<input name="titulo" required></label><label>Número<input name="numero" type="number" min="1" required></label><label>Página inicial<input name="pagina_inicio" type="number" min="1" required></label><label>Página final<input name="pagina_fim" type="number" min="1" required></label><label class="form-span-2">Descrição<textarea name="descricao" rows="2"></textarea></label></div><div class="form-actions"><button class="mini-button mini-button--primary">Adicionar capítulo</button></div></form>${chapters.length?`<div class="data-table-wrap"><table class="data-table"><thead><tr><th>Nº</th><th>Capítulo</th><th>Páginas</th><th>Descrição</th></tr></thead><tbody>${chapters.map(c=>`<tr><td>${c.numero}</td><td>${escapeHtml(c.titulo)}</td><td>${c.pagina_inicio}–${c.pagina_fim}</td><td>${escapeHtml(c.descricao||'—')}</td></tr>`).join('')}</tbody></table></div>`:emptyBlock('Sem capítulos','Este livro ainda não possui capítulos.','file')}`;
  host.querySelector('[data-chapter-form]')?.addEventListener('submit',async e=>{e.preventDefault();const f=e.currentTarget;const inicio=Number(f.pagina_inicio.value),fim=Number(f.pagina_fim.value);if(fim<inicio){showToast('A página final deve ser maior ou igual à inicial.','error');return;}await createBookChapter(bookId,{titulo:f.titulo.value.trim(),numero:Number(f.numero.value),pagina_inicio:inicio,pagina_fim:fim,descricao:f.descricao.value.trim()||null});showToast('Capítulo cadastrado.','success');await loadBookChapters(container,bookId);});
}
