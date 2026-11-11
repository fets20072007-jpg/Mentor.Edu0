import { escapeHtml } from '../../core/format.js';
import { icon } from '../../components/icons.js';

export function focusCard({ id, kicker='', title='—', value='', hint='', iconName='activity', route='' }) {
  return `<article class="dashboard-focus-card" data-focus-card="${escapeHtml(id)}" ${route ? `data-focus-route="${escapeHtml(route)}"` : ''}>
    <div class="dashboard-focus-top"><span class="dashboard-focus-icon">${icon(iconName)}</span><small data-focus-kicker>${escapeHtml(kicker)}</small></div>
    <h3 data-focus-title>${escapeHtml(title)}</h3>
    ${value ? `<strong data-focus-value>${escapeHtml(value)}</strong>` : '<strong data-focus-value></strong>'}
    <p data-focus-hint>${escapeHtml(hint)}</p>
    ${route ? '<span class="dashboard-focus-link">Ver detalhes →</span>' : ''}
  </article>`;
}

export function focusGrid(cards) {
  return `<section class="dashboard-focus-grid">${cards.map(focusCard).join('')}</section>`;
}

export function bindFocusRoutes(container, navigate) {
  container.querySelectorAll('[data-focus-route]').forEach(card => {
    card.addEventListener('click', () => navigate(card.dataset.focusRoute));
    card.addEventListener('keydown', event => {
      if ((event.key === 'Enter' || event.key === ' ') && card.dataset.focusRoute) navigate(card.dataset.focusRoute);
    });
    card.tabIndex = 0;
    card.setAttribute('role', 'button');
  });
}

export function startRotatingCard(container, cardId, items = [], intervalMs = 60000) {
  if (!items.length) return;
  const card = container.querySelector(`[data-focus-card="${cardId}"]`);
  if (!card) return;
  let index = Math.floor(Date.now() / intervalMs) % items.length;

  const paint = () => {
    if (!document.body.contains(card)) return false;
    const item = items[index % items.length] || {};
    const kicker = card.querySelector('[data-focus-kicker]');
    const title = card.querySelector('[data-focus-title]');
    const value = card.querySelector('[data-focus-value]');
    const hint = card.querySelector('[data-focus-hint]');
    if (kicker) kicker.textContent = item.kicker || '';
    if (title) title.textContent = item.title || '—';
    if (value) value.textContent = item.value || '';
    if (hint) hint.textContent = item.hint || '';
    card.classList.add('is-changing');
    setTimeout(() => card.classList.remove('is-changing'), 240);
    return true;
  };

  paint();
  const timer = setInterval(() => {
    if (!document.body.contains(card)) return clearInterval(timer);
    index = (index + 1) % items.length;
    paint();
  }, intervalMs);
}

export function safeArray(value) { return Array.isArray(value) ? value : []; }
export function firstNonEmpty(...values) { return values.find(v => v !== undefined && v !== null && String(v).trim() !== '') ?? ''; }
