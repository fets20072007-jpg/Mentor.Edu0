const API = 'http://127.0.0.1:8000';
const state = { token: localStorage.getItem('mentor_token'), user: null, demo: false, role: null, cache: {} };

const $ = (s) => document.querySelector(s);
const loginView = $('#loginView'); const appView = $('#appView'); const content = $('#content');

const roleNames = { aluno:'Aluno', professor:'Professor', administracao:'Administração', suporte:'Suporte' };
const icons = { dashboard:'⌂', subjects:'▤', assessments:'✓', grades:'★', attendance:'◷', record:'▦', classes:'⌘', analytics:'⌁', library:'▣', questionbank:'?', study:'◎', calendar:'□', tickets:'✦', admin:'⚙', profile:'○' };
const navByRole = {
  aluno:[['dashboard','Dashboard'],['subjects','Disciplinas'],['assessments','Avaliações'],['grades','Notas'],['attendance','Frequência'],['record','Histórico'],['library','Biblioteca'],['study','Plano de estudos'],['calendar','Calendário'],['profile','Meu perfil']],
  professor:[['dashboard','Dashboard'],['classes','Minhas turmas'],['subjects','Disciplinas'],['assessments','Avaliações'],['attendance','Frequência'],['analytics','Desempenho'],['questionbank','Banco de questões'],['library','Biblioteca'],['calendar','Calendário'],['tickets','Chamados'],['profile','Meu perfil']],
  administracao:[['dashboard','Dashboard'],['admin','Gestão escolar'],['classes','Turmas'],['subjects','Disciplinas'],['assessments','Avaliações'],['analytics','Indicadores'],['calendar','Calendário'],['tickets','Chamados'],['profile','Meu perfil']],
  suporte:[['dashboard','Dashboard'],['admin','Usuários e professores'],['library','Acervo técnico'],['tickets','Chamados'],['profile','Meu perfil']]
};

const demoUsers = {
  professor:{ nome:'Professor Teste A', tipo:'Professor', especialidade:'Física' },
  aluno:{ nome:'Aluno Teste A', tipo:'Aluno', serie:'3º ano' },
  administracao:{ nome:'Maria Lena', tipo:'Administracao', cargo_administrativo:'Gestão Escolar' },
  suporte:{ nome:'Suporte Mentor.Edu', tipo:'Suporte' }
};
const demo = {
  subjects:[{nome:'Física',descricao:'Mecânica e fundamentos',carga_horaria:80},{nome:'ICD',descricao:'Introdução ao conhecimento científico',carga_horaria:40}],
  assessments:[{titulo:'Avaliação diagnóstica',tipo:'Diagnóstica',valor:10,ativa:true},{titulo:'Cinemática - Unidade 1',tipo:'Formativa',valor:10,ativa:true}],
  grades:[{avaliacao:'Avaliação diagnóstica',nota:8.4},{avaliacao:'Cinemática - Unidade 1',nota:7.8}],
  classes:[{turma:'3A',serie:'3º ano',turno:'Manhã',ano:2026,is_dt:true,disciplinas:['Física','ICD'],alunos:[{nome:'Aluno Teste A'},{nome:'Aluno Teste B'},{nome:'Aluno Teste C'}]},{turma:'3B',serie:'3º ano',turno:'Tarde',ano:2026,is_dt:false,disciplinas:['Física'],alunos:[{nome:'Aluno Teste D'}]}],
  attendance:[{status:'Presente',data:'05/11/2026',disciplina:'Física'},{status:'Presente',data:'04/11/2026',disciplina:'Física'},{status:'Falta justificada',data:'03/11/2026',disciplina:'ICD'}],
  users:[{nome:'Aluno Teste A',tipo:'Aluno'},{nome:'Professor Teste A',tipo:'Professor'},{nome:'Maria Lena',tipo:'Administracao'}]
};

function normalizeRole(tipo=''){
  const r=tipo.normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim().toLowerCase();
  if(r.startsWith('admin')) return 'administracao'; if(r==='professor') return 'professor'; if(r==='aluno') return 'aluno'; if(r==='suporte') return 'suporte'; return r||'aluno';
}
function toast(msg, bad=false){ const t=$('#toast'); t.textContent=msg; t.className=`toast show ${bad?'bad':''}`; setTimeout(()=>t.className='toast',2800); }
async function request(path, options={}){
  const headers = {...(options.headers||{})}; if(state.token) headers.Authorization=`Bearer ${state.token}`;
  const res=await fetch(API+path,{...options,headers});
  if(!res.ok){ let detail=`Erro ${res.status}`; try{const j=await res.json(); detail=j.detail||detail}catch{}; throw new Error(detail); }
  const text=await res.text(); return text?JSON.parse(text):null;
}
async function apiGet(path){ return request(path); }
async function pingBackend(){
  const box=$('#backendStatus'); try{ const res=await fetch(API+'/',{cache:'no-store'}); if(!res.ok) throw 0; box.className='status-pill ok'; box.innerHTML='<span class="dot"></span>Backend conectado'; }
  catch{ box.className='status-pill bad'; box.innerHTML='<span class="dot"></span>Backend offline'; }
}

$('#loginForm').addEventListener('submit', async (e)=>{
  e.preventDefault(); const btn=$('#loginBtn'); btn.disabled=true; btn.textContent='Entrando...';
  try{
    const body=new URLSearchParams({username:$('#email').value.trim(),password:$('#password').value});
    const data=await request('/auth/login',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body});
    state.token=data.access_token; localStorage.setItem('mentor_token',state.token); state.demo=false;
    state.user=await apiGet('/users/me'); state.role=normalizeRole(state.user.tipo); openApp();
  }catch(err){ toast(err.message||'Não foi possível entrar.',true); }
  finally{btn.disabled=false;btn.textContent='Entrar';}
});
$('#demoBtn').addEventListener('click',()=>startDemo('professor'));
$('#logoutBtn').addEventListener('click',logout);
$('#demoRole').addEventListener('change',(e)=>startDemo(e.target.value));

function startDemo(role){ state.demo=true; state.token=null; localStorage.removeItem('mentor_token'); state.role=role; state.user=demoUsers[role]; state.cache={}; openApp(); $('#demoRole').value=role; }
function logout(){ state.token=null;state.user=null;state.demo=false;state.cache={};localStorage.removeItem('mentor_token');appView.classList.add('hidden');loginView.classList.remove('hidden'); }
function initials(name='Mentor Edu'){return name.split(/\s+/).slice(0,2).map(x=>x[0]).join('').toUpperCase()}
function openApp(){ loginView.classList.add('hidden');appView.classList.remove('hidden');$('#userName').textContent=state.user?.nome||'Usuário';$('#userRole').textContent=roleNames[state.role]||state.user?.tipo||'Perfil';$('#userAvatar').textContent=initials(state.user?.nome);$('#demoRoleWrap').classList.toggle('hidden',!state.demo);buildNav();pingBackend();navigate('dashboard'); }
function buildNav(){ const nav=$('#nav');nav.innerHTML='';(navByRole[state.role]||navByRole.aluno).forEach(([key,label])=>{const b=document.createElement('button');b.dataset.key=key;b.innerHTML=`<span class="ico">${icons[key]||'•'}</span><span>${label}</span>`;b.onclick=()=>navigate(key);nav.appendChild(b);}); }
function setActive(key){ document.querySelectorAll('#nav button').forEach(b=>b.classList.toggle('active',b.dataset.key===key)); }
const titles={dashboard:'Dashboard',subjects:'Disciplinas',assessments:'Avaliações',grades:'Notas',attendance:'Frequência',record:'Histórico acadêmico',classes:'Turmas',analytics:'Desempenho e indicadores',library:'Biblioteca',questionbank:'Banco de questões',study:'Plano de estudos',calendar:'Calendário',tickets:'Chamados',admin:'Gestão escolar',profile:'Meu perfil'};
async function navigate(key){ setActive(key);$('#pageTitle').textContent=titles[key]||key;$('#crumb').textContent=`MENTOR.EDU / ${roleNames[state.role]||'PERFIL'}`.toUpperCase();content.innerHTML='<div class="skeleton"></div><div style="height:12px"></div><div class="skeleton"></div>';
  try{ const fn=pages[key]||pages.dashboard; await fn(); }catch(err){content.innerHTML=errorBox(err.message);}
}
function errorBox(msg){return `<div class="callout error-box"><strong>Não foi possível carregar esta área.</strong><p>${escapeHtml(msg)}. Você pode usar o modo demonstração para visualizar a proposta da interface.</p></div>`}
function escapeHtml(v){return String(v??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
function humanKey(k){return k.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
function visibleEntries(obj){return Object.entries(obj||{}).filter(([k,v])=>!['id','user_id','teacher_id','classroom_id','subject_id','assessment_id','question_id','student_id'].includes(k) && !k.endsWith('_id') && v!==null && typeof v!=='object');}
function genericCards(items,empty='Nenhum registro encontrado.'){
  if(!Array.isArray(items)||!items.length)return `<div class="empty">${empty}</div>`;
  return `<div class="section-grid">${items.map((item)=>{const entries=visibleEntries(item);const title=item.nome||item.titulo||item.name||item.tipo||'Registro';const body=entries.filter(([k])=>!['nome','titulo','name'].includes(k)).slice(0,5).map(([k,v])=>`<div><b>${escapeHtml(humanKey(k))}:</b> ${escapeHtml(typeof v==='boolean'?(v?'Sim':'Não'):v)}</div>`).join('');return `<article class="feature-card"><span class="feature-icon">▦</span><h3>${escapeHtml(title)}</h3><p>${body||'Informação disponível no backend.'}</p></article>`}).join('')}</div>`;
}
function list(items,mapper){if(!items?.length)return '<div class="empty">Nenhum dado disponível.</div>';return `<div class="list">${items.map(mapper).join('')}</div>`}
async function load(path,demoKey){ if(state.demo)return demo[demoKey]||[]; if(state.cache[path])return state.cache[path]; const d=await apiGet(path);state.cache[path]=d;return d; }

const pages={
  dashboard:async()=>{
    let subjects=[],assessments=[],extra=[];
    try{subjects=await load('/subjects/me','subjects')}catch{}
    try{assessments=await load('/assessments/','assessments')}catch{}
    if(state.role==='professor'){try{extra=await load('/teachers/me/classrooms','classes')}catch{}}
    if(state.role==='aluno'){try{extra=await load('/grades/me','grades')}catch{}}
    if(state.role==='administracao'||state.role==='suporte'){try{extra=await load('/users/','users')}catch{}}
    const roleText={aluno:'acompanhe sua aprendizagem e próximos passos',professor:'acompanhe suas turmas e ações pedagógicas',administracao:'acompanhe a operação acadêmica da instituição',suporte:'acompanhe usuários e operação técnica'}[state.role];
    content.innerHTML=`<section class="hero-card"><div><p class="eyebrow">BEM-VINDO(A)</p><h2>${escapeHtml(state.user.nome)}</h2><p>No Mentor.Edu, ${roleText}.</p></div><div class="hero-badge"><strong>${state.demo?'DEMO':'ONLINE'}</strong><span>${state.demo?'Dados ilustrativos':'Dados do backend local'}</span></div></section>
    <div class="stat-grid"><div class="stat"><span class="label">Disciplinas</span><strong>${subjects.length||0}</strong><small>no seu escopo atual</small></div><div class="stat"><span class="label">Avaliações</span><strong>${assessments.length||0}</strong><small>visíveis para seu perfil</small></div><div class="stat"><span class="label">${state.role==='professor'?'Turmas':state.role==='aluno'?'Notas':'Usuários'}</span><strong>${extra.length||0}</strong><small>registros carregados</small></div><div class="stat"><span class="label">Projeto</span><strong>Dia 3</strong><small>Professor/DT em validação</small></div></div>
    <div class="grid-2"><section class="panel"><div class="panel-head"><h3>Atividade acadêmica</h3><span class="tag green">Backend protegido</span></div>${list(assessments.slice(0,4),a=>`<div class="list-item"><div><h4>${escapeHtml(a.titulo||'Avaliação')}</h4><p>${escapeHtml(a.tipo||'Avaliação acadêmica')} · ${a.ativa===false?'Inativa':'Ativa'}</p></div><span class="tag">${escapeHtml(a.valor??'—')} pts</span></div>`)}</section>
    <section class="panel"><div class="panel-head"><h3>Próximas etapas do projeto</h3><span class="tag amber">Em desenvolvimento</span></div><div class="list"><div class="list-item"><div><h4>Finalizar validação do DT</h4><p>Teste de atuação em múltiplas turmas e restauração do estado.</p></div><span class="metric">Dia 3</span></div><div class="list-item"><div><h4>Gestão de turmas de atuação</h4><p>Fluxo amigável para Administração vincular professor, turma e disciplina.</p></div><span class="metric">Dia 4</span></div><div class="list-item"><div><h4>Frontend definitivo</h4><p>Será iniciado após o backend e a documentação consolidada.</p></div><span class="metric">Dias 15+</span></div></div></section></div>`;
  },
  subjects:async()=>{const data=await load('/subjects/me','subjects');content.innerHTML=`<div class="callout"><strong>Disciplinas do seu escopo</strong><p>O backend filtra os registros conforme o perfil, a turma e o professor autenticado.</p></div>${genericCards(data,'Nenhuma disciplina disponível.')}`;},
  assessments:async()=>{const data=await load('/assessments/','assessments');content.innerHTML=`<div class="callout"><strong>Avaliações com acesso controlado</strong><p>Aluno vê avaliações ativas de sua turma; Professor vê as próprias e o DT possui leitura ampliada da turma, sem assumir autoria.</p></div>${genericCards(data,'Nenhuma avaliação disponível.')}`;},
  grades:async()=>{const data=await load('/grades/me','grades');content.innerHTML=`<div class="callout"><strong>Minhas notas</strong><p>Esta tela usa o endpoint protegido do próprio aluno.</p></div>${genericCards(data,'Nenhuma nota registrada.')}`;},
  attendance:async()=>{let data=[];if(state.demo)data=demo.attendance;else if(state.role==='aluno')data=await apiGet('/attendance/me');else{content.innerHTML=illustrative('Frequência','Registro e acompanhamento de frequência já existem no backend. A tela definitiva terá seleção amigável de turma e disciplina, sem IDs visíveis.','Funcionalidade existente / interface ilustrativa');return;}content.innerHTML=`<div class="callout"><strong>Frequência</strong><p>Registros vinculados ao usuário autenticado.</p></div>${genericCards(data,'Nenhum registro de frequência.')}`;},
  record:async()=>{const data=state.demo?{aluno:'Aluno Teste A',situacao:'Matriculado',media_geral:'8,1',frequencia:'94%',disciplinas:'Física, ICD'}:await apiGet('/academic-record/me');content.innerHTML=`<div class="callout"><strong>Histórico acadêmico protegido</strong><p>Aluno acessa o próprio histórico; Professor comum enxerga suas disciplinas; DT possui visão completa da própria turma.</p></div><section class="panel"><div class="kv">${visibleEntries(data).map(([k,v])=>`<div class="kv-item"><span>${escapeHtml(humanKey(k))}</span><strong>${escapeHtml(v)}</strong></div>`).join('')}</div>${Array.isArray(data?.disciplinas)?genericCards(data.disciplinas):''}</section>`;},
  classes:async()=>{if(state.role==='professor'){const data=await load('/teachers/me/classrooms','classes');content.innerHTML=`<div class="callout"><strong>Turmas de atuação ≠ turma de DT</strong><p>As turmas de atuação vêm das disciplinas do professor. O campo <b>is_dt</b> informa em qual turma ele exerce a função de Diretor de Turma.</p></div>${genericCards(data,'Nenhuma turma de atuação.')}`;}else if(state.role==='administracao'){const data=state.demo?demo.classes:await apiGet('/classrooms');content.innerHTML=`<div class="callout"><strong>Gestão de turmas</strong><p>A Administração cria turmas e define o DT após o professor já atuar na turma.</p></div>${genericCards(data)}`;}else content.innerHTML=illustrative('Turmas','Área disponível conforme o perfil.','Acesso condicionado ao papel');},
  analytics:async()=>{content.innerHTML=illustrative('Desempenho e analytics','O backend já possui média por aluno/disciplina e análises de desempenho protegidas por Professor, DT, Aluno e Administração. A interface definitiva mostrará gráficos, filtros e alertas de dificuldade.','Backend existente / visual em evolução');},
  library:async()=>{let data=null;if(!state.demo){try{data=await apiGet('/library/')}catch{}}content.innerHTML=`<div class="callout"><strong>Biblioteca e acervo institucional</strong><p>O projeto separa gestão técnica do acervo e criação pedagógica de materiais.</p></div>${data?genericCards(Array.isArray(data)?data:[data]):illustrative('Acervo e materiais','Livros, capítulos, vídeos, PDFs, exemplos e exercícios já fazem parte do backend. O banco de questões possui autoria e compartilhamento.','Funcionalidade existente / demonstração visual')}`;},
  questionbank:async()=>{content.innerHTML=illustrative('Banco de questões','O professor cria questões próprias, pode compartilhar e mantém controle de autoria. Questões privadas de outros professores são bloqueadas.','Backend existente');},
  study:async()=>{content.innerHTML=illustrative('Plano de estudos personalizado','Planos de estudo, sessões, dashboard e recomendações já possuem rotas protegidas para o Aluno. A camada de IA/Gemini será integrada após a consolidação do backend.','Backend existente / IA planejada');},
  calendar:async()=>{content.innerHTML=illustrative('Calendário acadêmico','Área planejada para aulas, prazos de avaliações, eventos e notificações.','Planejado para Dia 7');},
  tickets:async()=>{content.innerHTML=illustrative('Chamados e notificações','Canal para suporte operacional, acompanhamento de solicitações e alertas do sistema.','Planejado para Dia 6');},
  admin:async()=>{let users=[],teachers=[],classes=[],subjects=[];if(state.demo){users=demo.users;teachers=[demoUsers.professor];classes=demo.classes;subjects=demo.subjects}else{try{users=await apiGet('/users/')}catch{}try{teachers=await apiGet('/teachers')}catch{}if(state.role==='administracao'){try{classes=await apiGet('/classrooms')}catch{}try{subjects=await apiGet('/subjects')}catch{}}}content.innerHTML=`<div class="stat-grid"><div class="stat"><span class="label">Usuários</span><strong>${users.length}</strong><small>cadastros institucionais</small></div><div class="stat"><span class="label">Professores</span><strong>${teachers.length}</strong><small>perfis Teacher</small></div><div class="stat"><span class="label">Turmas</span><strong>${classes.length}</strong><small>${state.role==='suporte'?'sem acesso pedagógico':'gestão acadêmica'}</small></div><div class="stat"><span class="label">Disciplinas</span><strong>${subjects.length}</strong><small>${state.role==='suporte'?'bloqueadas para Suporte':'ativas no escopo'}</small></div></div><div class="grid-2"><section class="panel"><div class="panel-head"><h3>Usuários</h3><span class="tag">Institucional</span></div>${genericCards(users.slice(0,6))}</section><section class="panel"><div class="panel-head"><h3>Professores</h3><span class="tag green">Perfil automático</span></div>${genericCards(teachers.slice(0,6))}</section></div>`;},
  profile:async()=>{const u=state.user||{};content.innerHTML=`<section class="panel"><div class="panel-head"><h3>Dados do perfil</h3><span class="tag">${escapeHtml(roleNames[state.role]||u.tipo)}</span></div><div class="kv">${visibleEntries(u).map(([k,v])=>`<div class="kv-item"><span>${escapeHtml(humanKey(k))}</span><strong>${escapeHtml(v)}</strong></div>`).join('')}</div></section>`;}
};
function illustrative(title,desc,status){return `<div class="callout"><strong>${escapeHtml(title)}</strong><p>${escapeHtml(desc)}</p></div><div class="section-grid"><article class="feature-card"><span class="feature-icon">◉</span><h3>Visão amigável</h3><p>O frontend definitivo ocultará IDs técnicos e usará nomes, filtros e seletores dinâmicos.</p><span class="tag gray">${escapeHtml(status)}</span></article><article class="feature-card"><span class="feature-icon">⌁</span><h3>Integração progressiva</h3><p>As telas serão ligadas aos endpoints à medida que o cronograma do backend for concluído.</p><span class="tag">Roadmap</span></article><article class="feature-card"><span class="feature-icon">✓</span><h3>Regras de acesso</h3><p>Cada tela respeitará Aluno, Professor, DT, Administração e Suporte.</p><span class="tag green">Segurança</span></article></div>`}

(async()=>{ const demoRoleParam=new URLSearchParams(location.search).get('demo'); if(demoRoleParam && demoUsers[demoRoleParam]){startDemo(demoRoleParam);return;} if(state.token){try{state.user=await apiGet('/users/me');state.role=normalizeRole(state.user.tipo);openApp();}catch{localStorage.removeItem('mentor_token');state.token=null;}} })();
