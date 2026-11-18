import { API_URL } from '../../config.js';
import { getUiPreferences, saveUiPreferences, resetUiPreferences } from '../../core/ui-preferences.js';
import { pageHeader, surface } from '../shared/page-ui.js';
import { showToast } from '../../components/toast.js';

export async function renderAdminSettings(container){
  const prefs = getUiPreferences();
  container.innerHTML = `${pageHeader('Configurações','Preferências locais de uso e informações do ambiente atual.')}${surface(`
    <div class="settings-sections">
      <section class="settings-panel"><div><span class="entity-card-kicker">Interface</span><h3>Preferências deste dispositivo</h3><p>Essas opções ficam salvas apenas neste navegador e não alteram dados institucionais.</p></div>
        <label class="setting-row"><span><strong>Menu mais compacto</strong><small>Reduz a largura visual da navegação lateral.</small></span><input type="checkbox" data-pref="compactSidebar" ${prefs.compactSidebar?'checked':''}></label>
        <label class="setting-row"><span><strong>Reduzir animações</strong><small>Diminui transições e movimentos automáticos.</small></span><input type="checkbox" data-pref="reducedMotion" ${prefs.reducedMotion?'checked':''}></label>
        <label class="setting-row"><span><strong>Tabelas compactas</strong><small>Exibe mais registros na tela ao mesmo tempo.</small></span><input type="checkbox" data-pref="denseTables" ${prefs.denseTables?'checked':''}></label>
        <div class="form-actions"><button class="mini-button" data-reset-prefs>Restaurar padrão</button></div>
      </section>
      <section class="settings-panel settings-panel--info"><div><span class="entity-card-kicker">Ambiente</span><h3>Diagnóstico rápido</h3></div><dl class="settings-dl"><div><dt>API</dt><dd>${API_URL}</dd></div><div><dt>Sessão</dt><dd>JWT / Bearer</dd></div><div><dt>Frontend</dt><dd>${location.origin}</dd></div></dl></section>
    </div>
  `)}`;
  container.querySelectorAll('[data-pref]').forEach(input => input.addEventListener('change',()=>{
    saveUiPreferences({ [input.dataset.pref]: input.checked });
    showToast('Preferência atualizada.','success');
  }));
  container.querySelector('[data-reset-prefs]')?.addEventListener('click',()=>{ resetUiPreferences(); showToast('Preferências restauradas.','success'); renderAdminSettings(container); });
}
