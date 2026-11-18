from pathlib import Path
import re

ROOT = Path('.')
FRONT = ROOT / 'frontend'
JS = FRONT / 'mentor-ai-student.js'

if not FRONT.exists():
    raise SystemExit('Pasta frontend não encontrada.')
if not JS.exists():
    raise SystemExit('mentor-ai-student.js não encontrado. Aplique o frontend IA V1 primeiro.')

text = JS.read_text(encoding='utf-8-sig', errors='strict')
backup = JS.with_name('mentor-ai-student.js.backup_fix_v1_1')
if not backup.exists():
    backup.write_text(text, encoding='utf-8')

old = """  function looksLikeStudentDashboard(){
    const body = normalize(document.body?.innerText || \"\");
    const studentSignals = [\"disciplinas\",\"avaliacoes\",\"notas\",\"frequencia\",\"biblioteca\",\"horarios\"];
    const count = studentSignals.filter(x => body.includes(x)).length;
    return count >= 3;
  }

  function shouldMount(){
    const role = detectRole();
    if(role === \"teacher\" || role === \"admin\") return false;
    if(role === \"student\") return true;
    return looksLikeStudentDashboard();
  }
"""

new = """  function isLoginPage(){
    const body = normalize(document.body?.innerText || \"\");
    const hasPassword = !!document.querySelector('input[type=\"password\"]');
    const hasEmail = !!document.querySelector('input[type=\"email\"]');
    const loginWords =
      body.includes(\"entre na sua conta\") ||
      body.includes(\"bem-vindo ao mentor\") ||
      body.includes(\"seu e-mail institucional\");

    const signals = [
      \"inicio\",\"disciplinas\",\"avaliacoes\",\"notas\",\"frequencia\",
      \"historico academico\",\"plano de estudos\",\"biblioteca\",
      \"horarios\",\"notificacoes\",\"chamados\",\"perfil\"
    ];
    const count = signals.filter(x => body.includes(x)).length;
    return (hasPassword && (hasEmail || loginWords)) && count < 4;
  }

  function looksLikeStudentDashboard(){
    if(isLoginPage()) return false;
    const body = normalize(document.body?.innerText || \"\");
    const signals = [
      \"inicio\",\"disciplinas\",\"avaliacoes\",\"notas\",\"frequencia\",
      \"historico academico\",\"plano de estudos\",\"biblioteca\",
      \"horarios\",\"notificacoes\",\"chamados\",\"perfil\"
    ];
    const count = signals.filter(x => body.includes(x)).length;
    return count >= 4;
  }

  function shouldMount(){
    if(isLoginPage()) return false;
    const role = detectRole();
    if(role === \"teacher\" || role === \"admin\") return false;
    if(looksLikeStudentDashboard()) return true;
    return role === \"student\";
  }
"""

if old not in text:
    raise SystemExit('Bloco de detecção antigo não encontrado no JS.')
text = text.replace(old, new, 1)

old_mount = """  function mount(){
    if(!shouldMount()) return;
    createHomeCard();
    createNavItem();
    createFloating();
    createOverlay();
    fetchProfile();

    // Pequena tentativa extra para dashboards que renderizam via JS após o load.
    const observer = new MutationObserver(() => {
      createHomeCard();
      createNavItem();
    });
    observer.observe(document.body,{childList:true,subtree:true});
    setTimeout(()=>observer.disconnect(),12000);
  }

  if(document.readyState === \"loading\"){
    document.addEventListener(\"DOMContentLoaded\", mount);
  }else{
    mount();
  }
})();
"""

new_mount = """  function removeStudentAI(){
    [
      \"#mentor-ai-home-card\",
      \"#mentor-ai-floating\",
      \"#mentor-ai-nudge\",
      \"#mentor-ai-overlay\",
      \"#mentor-ai-nav-item\"
    ].forEach(sel => document.querySelector(sel)?.remove());
    document.body.style.overflow = \"\";
  }

  function refreshStudentAI(){
    if(!shouldMount()){
      removeStudentAI();
      return;
    }
    createNavItem();
    createFloating();
    createOverlay();
    createHomeCard();
    fetchProfile();
  }

  function mount(){
    refreshStudentAI();

    window.addEventListener(\"hashchange\", () => {
      setTimeout(refreshStudentAI, 80);
      setTimeout(refreshStudentAI, 350);
    });

    let timer = null;
    const observer = new MutationObserver(() => {
      clearTimeout(timer);
      timer = setTimeout(refreshStudentAI, 120);
    });
    observer.observe(document.body,{childList:true,subtree:true});

    [250,700,1500,3000].forEach(ms => setTimeout(refreshStudentAI, ms));
  }

  if(document.readyState === \"loading\"){
    document.addEventListener(\"DOMContentLoaded\", mount);
  }else{
    mount();
  }
})();
"""

if old_mount not in text:
    raise SystemExit('Bloco mount antigo não encontrado no JS.')
text = text.replace(old_mount, new_mount, 1)
JS.write_text(text, encoding='utf-8')

for html in FRONT.rglob('*.html'):
    raw = html.read_text(encoding='utf-8-sig', errors='ignore')
    low = raw.lower()
    out = raw

    is_login = (
        'type="password"' in low and
        ('type="email"' in low or 'entre na sua conta' in low or 'bem-vindo ao mentor' in low)
    )
    is_dashboard = html.name.lower() == 'dashboard.html'

    if is_login and not is_dashboard:
        out = re.sub(r'\s*<link[^>]+mentor-ai-student\.css[^>]*>\s*', '\n', out, flags=re.I)
        out = re.sub(r'\s*<script[^>]+mentor-ai-student\.js[^>]*>\s*</script>\s*', '\n', out, flags=re.I)

    if is_dashboard:
        if 'mentor-ai-student.css' not in out:
            out = out.replace('</head>', '\n<link rel="stylesheet" href="mentor-ai-student.css">\n</head>', 1)
        if 'mentor-ai-student.js' not in out:
            out = out.replace('</body>', '\n<script src="mentor-ai-student.js" defer></script>\n</body>', 1)

    if out != raw:
        html.write_text(out, encoding='utf-8')

print('')
print('FIX IA ALUNO V1.1 APLICADO COM SUCESSO.')
print('- IA removida do login')
print('- IA garantida no dashboard.html')
print('- suporte a rotas #/record, #/home etc.')
print('- bolha flutuante nas páginas internas')
print('- card Mentor Edu só aparece onde houver Atalhos rápidos')
print('')
print('Backend e banco: nenhuma alteração.')
