const KEY = 'mentor_ui_preferences';
const DEFAULTS = Object.freeze({ compactSidebar: false, reducedMotion: false, denseTables: false });

export function getUiPreferences(){
  try { return { ...DEFAULTS, ...(JSON.parse(localStorage.getItem(KEY) || '{}') || {}) }; }
  catch { return { ...DEFAULTS }; }
}

export function saveUiPreferences(next){
  const prefs = { ...getUiPreferences(), ...next };
  localStorage.setItem(KEY, JSON.stringify(prefs));
  applyUiPreferences(prefs);
  return prefs;
}

export function resetUiPreferences(){
  localStorage.removeItem(KEY);
  applyUiPreferences(DEFAULTS);
  return { ...DEFAULTS };
}

export function applyUiPreferences(prefs = getUiPreferences()){
  document.body.classList.toggle('pref-compact-sidebar', Boolean(prefs.compactSidebar));
  document.body.classList.toggle('pref-reduced-motion', Boolean(prefs.reducedMotion));
  document.body.classList.toggle('pref-dense-tables', Boolean(prefs.denseTables));
}
