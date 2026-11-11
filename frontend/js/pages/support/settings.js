import { API_URL } from '../../config.js';
import { getUiPreferences, saveUiPreferences, resetUiPreferences } from '../../core/ui-preferences.js';
import { pageHeader, surface } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

export async function renderSupportSettings(container){
  const prefs=getUiPreferences();
  container.innerHTML = `${pageHeader('Configurações de suporte','Preferências deste dispositivo e informações úteis para diagnóstico.')}${surface(`
    <div class="settings-sections">
      <section class="settings-panel"><div><span class="entity-card-kicker">Interface</span><h3>Preferências locais</h3><p>Não alteram permissões nem dados pedagógicos.</p></div>
        <label class="setting-row"><span><strong>Menu mais compacto</strong><small>Reduz a navegação lateral.</small></span><input type="checkbox" data-pref="compactSidebar" ${prefs.compactSidebar?'checked':''}></label>
        <label class="setting-row"><span><strong>Reduzir animações</strong><small>Melhora conforto e desempenho em dispositivos modestos.</small></span><input type="checkbox" data-pref="reducedMotion" ${prefs.reducedMotion?'checked':''}></label>
        <label class="setting-row"><span><strong>Tabelas compactas</strong><small>Mostra mais registros por tela.</small></span><input type="checkbox" data-pref="denseTables" ${prefs.denseTables?'checked':''}></label>
        <div class="form-actions"><button class="mini-button" data-reset-prefs>Restaurar padrão</button></div>
      </section>
      <section class="settings-panel settings-panel--info"><div><span class="entity-card-kicker">Diagnóstico</span><h3>Ambiente atual</h3></div><dl class="settings-dl"><div><dt>Backend</dt><dd>${API_URL}</dd></div><div><dt>Sessão</dt><dd>JWT / Bearer</dd></div><div><dt>Escopo</dt><dd>Chamados, usuários e biblioteca</dd></div></dl></section>
    </div>`)}`;
  container.querySelectorAll('[data-pref]').forEach(input=>input.addEventListener('change',()=>{saveUiPreferences({[input.dataset.pref]:input.checked});showToast('Preferência atualizada.','success');}));
  container.querySelector('[data-reset-prefs]')?.addEventListener('click',()=>{resetUiPreferences();showToast('Preferências restauradas.','success');renderSupportSettings(container);});
}
