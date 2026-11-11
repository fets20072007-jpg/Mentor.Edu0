const API_BASE = "http://127.0.0.1:8000";

const state = {
  token: localStorage.getItem("mentor_token") || "",
  user: null,
  page: "inicio",
  fontScale: Number(localStorage.getItem("mentor_font_scale")) || 1,
  highContrast: localStorage.getItem("mentor_high_contrast") === "true"
};

const menuByRole = {
  aluno: [
    ["inicio", "Início", "⌂"],
    ["avaliacoes", "Minhas avaliações", "📝"],
    ["respostas", "Minhas respostas", "✓"],
    ["desempenho", "Meu desempenho", "📈"],
    ["historico", "Histórico", "🕘"],
    ["chamados", "Chamados", "💬"],
    ["notificacoes", "Notificações", "🔔"],
    ["perfil", "Meu perfil", "👤"]
  ],
  professor: [
    ["inicio", "Início", "⌂"],
    ["turmas", "Minhas turmas", "🏫"],
    ["avaliacoes", "Avaliações", "📝"],
    ["alunos", "Alunos", "👥"],
    ["correcoes", "Correções", "✓"],
    ["relatorios", "Relatórios", "📊"],
    ["chamados", "Chamados", "💬"],
    ["notificacoes", "Notificações", "🔔"],
    ["perfil", "Meu perfil", "👤"]
  ],
  administracao: [
    ["inicio", "Início", "⌂"],
    ["usuarios", "Usuários", "👥"],
    ["turmas", "Turmas", "🏫"],
    ["avaliacoes", "Avaliações", "📝"],
    ["relatorios", "Relatórios", "📊"],
    ["chamados", "Chamados", "💬"],
    ["notificacoes", "Notificações", "🔔"],
    ["perfil", "Meu perfil", "👤"]
  ],
  suporte: [
    ["inicio", "Início", "⌂"],
    ["usuarios", "Usuários", "👥"],
    ["administracao", "Administração", "🛡"],
    ["diagnostico", "Diagnóstico", "🩺"],
    ["chamados", "Chamados", "💬"],
    ["notificacoes", "Notificações", "🔔"],
    ["perfil", "Meu perfil", "👤"]
  ]
};

const pageMeta = {
  inicio: ["Visão geral", "Início", "Veja o que precisa da sua atenção hoje."],
  avaliacoes: ["Aprendizagem", "Avaliações", "Consulte e acompanhe avaliações disponíveis."],
  respostas: ["Aprendizagem", "Minhas respostas", "Veja as respostas que você já enviou."],
  desempenho: ["Aprendizagem", "Meu desempenho", "Acompanhe sua evolução e seus pontos de atenção."],
  historico: ["Aprendizagem", "Histórico", "Veja avaliações e resultados anteriores."],
  turmas: ["Organização", "Turmas", "Acesse turmas, disciplinas e estudantes."],
  alunos: ["Acompanhamento", "Alunos", "Acompanhe o desempenho dos estudantes."],
  correcoes: ["Avaliações", "Correções", "Consulte correções e pendências por avaliação."],
  relatorios: ["Acompanhamento", "Relatórios", "Consulte informações acadêmicas consolidadas."],
  usuarios: ["Gestão", "Usuários", "Cadastre e consulte usuários autorizados."],
  administracao: ["Gestão", "Administração", "Consulte integrantes da administração."],
  diagnostico: ["Suporte", "Diagnóstico", "Consulte o estado básico do ambiente."],
  chamados: ["Comunicação", "Chamados", "Acompanhe solicitações e pendências internas."],
  notificacoes: ["Comunicação", "Notificações", "Veja avisos e prazos importantes."],
  perfil: ["Conta", "Meu perfil", "Consulte suas informações pessoais."],
  ajuda: ["Ajuda", "Central de ajuda", "Encontre orientações para usar o Mentor.Edu."]
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function normalizeRole(role = "") {
  return role.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
  }[char]));
}

function formatDate(value) {
  if (!value) return "Data não informada";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return escapeHtml(value);
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" }).format(d);
}

function formatNumber(value, digits = 1) {
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(digits).replace(".", ",") : "—";
}

function applyAccessibilityPreferences() {
  document.documentElement.style.setProperty("--font-scale", String(state.fontScale));
  document.body.classList.toggle("high-contrast", state.highContrast);
  $("#contrast-button")?.setAttribute("aria-pressed", String(state.highContrast));
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (state.token) headers.set("Authorization", `Bearer ${state.token}`);
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    let detail = `Erro ${response.status}`;
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch {}
    if (response.status === 401) {
      state.token = "";
      state.user = null;
      localStorage.removeItem("mentor_token");
    }
    throw new Error(typeof detail === "string" ? detail : "Não foi possível concluir a solicitação.");
  }
  const type = response.headers.get("content-type") || "";
  return type.includes("application/json") ? response.json() : response.text();
}

async function safeApi(path, fallback = null) {
  try { return await api(path); } catch { return fallback; }
}

async function login(email, senha) {
  const form = new URLSearchParams();
  form.set("username", email.trim().toLowerCase());
  form.set("password", senha);

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form
  });

  if (!response.ok) {
    let detail = "Não foi possível entrar.";
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch {}
    throw new Error(detail);
  }

  const data = await response.json();
  state.token = data.access_token;
  localStorage.setItem("mentor_token", state.token);
  state.user = await api("/users/me");
}

async function restoreSession() {
  if (!state.token) return false;
  try {
    state.user = await api("/users/me");
    return true;
  } catch {
    state.token = "";
    state.user = null;
    localStorage.removeItem("mentor_token");
    return false;
  }
}

function showApp() {
  $("#login-view").hidden = true;
  $("#app-view").hidden = false;
  $("#user-name").textContent = state.user?.nome || "Usuário";
  $("#user-role").textContent = state.user?.tipo || "Perfil";
  $("#school-name").textContent = state.user?.escola || "Mentor.Edu";
  $("#avatar-letter").textContent = (state.user?.nome || "U").trim().charAt(0).toUpperCase();
  buildNavigation();
  navigate("inicio");
}

function showLogin(message = "") {
  $("#app-view").hidden = true;
  $("#login-view").hidden = false;
  $("#login-message").textContent = message;
  setTimeout(() => $("#email")?.focus(), 50);
}

function buildNavigation() {
  const role = normalizeRole(state.user?.tipo);
  const menu = menuByRole[role] || menuByRole.aluno;
  $("#primary-nav").innerHTML = menu.map(([id, label, icon]) => `
    <button class="nav-item" type="button" data-page="${id}" aria-current="false">
      <span class="nav-item__icon" aria-hidden="true">${icon}</span>
      <span>${label}</span>
    </button>
  `).join("");
  $$(".nav-item[data-page]").forEach((item) => item.addEventListener("click", () => navigate(item.dataset.page)));
}

function navigate(page) {
  state.page = page;
  const [eyebrow, title, description] = pageMeta[page] || pageMeta.inicio;
  $("#page-eyebrow").textContent = eyebrow;
  $("#page-title").textContent = title;
  $("#page-description").textContent = description;
  $$(".nav-item[data-page]").forEach((item) => item.setAttribute("aria-current", String(item.dataset.page === page ? "page" : "false")));
  closeSidebar();
  renderPage(page);
  $("#conteudo-principal").focus({ preventScroll: true });
}

function loading(label = "Carregando informações…") {
  $("#page-content").innerHTML = `<div class="panel"><div class="empty-state"><strong>${escapeHtml(label)}</strong><span>Aguarde um instante.</span></div></div>`;
}

function emptyState(title, text) {
  return `<div class="empty-state"><strong>${escapeHtml(title)}</strong><span>${escapeHtml(text)}</span></div>`;
}

function statCard(label, value, detail) {
  return `<article class="stat-card"><span class="stat-card__label">${escapeHtml(label)}</span><strong class="stat-card__value">${escapeHtml(value)}</strong><span class="stat-card__detail">${escapeHtml(detail)}</span></article>`;
}

function quickAction(icon, title, desc, page) {
  return `<button class="quick-action" type="button" data-go="${page}"><span aria-hidden="true">${icon}</span><strong>${escapeHtml(title)}</strong><small>${escapeHtml(desc)}</small></button>`;
}

async function renderHome() {
  loading("Preparando sua visão geral…");
  const role = normalizeRole(state.user?.tipo);
  const firstName = (state.user?.nome || "Usuário").split(" ")[0];
  let stats = [];
  let actions = [];
  let attention = [];
  let intro = "Acompanhe as informações do Mentor.Edu em um só lugar.";

  if (role === "aluno") {
    const [assessments, summary, answers] = await Promise.all([
      safeApi("/assessments/", []),
      safeApi("/assessments/summary/me", {}),
      safeApi("/answers/me", [])
    ]);
    stats = [
      ["Avaliações disponíveis", String(assessments.length), "Da sua turma"],
      ["Avaliações realizadas", String(summary.avaliacoes_realizadas ?? 0), "No histórico"],
      ["Desempenho médio", `${formatNumber(summary.percentual_medio ?? 0)}%`, summary.status_geral || "Sem classificação"],
      ["Respostas enviadas", String(answers.length), "Registradas na sua conta"]
    ];
    actions = [
      ["📝", "Ver avaliações", "Acesse as avaliações da sua turma", "avaliacoes"],
      ["✓", "Minhas respostas", "Confira o que já foi enviado", "respostas"],
      ["📈", "Meu desempenho", "Veja resultados e evolução", "desempenho"],
      ["🕘", "Histórico", "Consulte avaliações anteriores", "historico"]
    ];
    intro = "Acompanhe avaliações, respostas, resultados e seu progresso acadêmico.";
    if (assessments.length) attention.push(`${assessments.length} avaliação(ões) disponível(is) para sua turma.`);
  } else if (role === "professor") {
    const [assessments, classrooms, students] = await Promise.all([
      safeApi("/assessments/", []),
      safeApi("/teachers/me/classrooms", []),
      safeApi("/assessments/teacher/students/performance", [])
    ]);
    const pending = await countTeacherPending(assessments);
    stats = [
      ["Turmas vinculadas", String(classrooms.length), "Com disciplinas associadas"],
      ["Minhas avaliações", String(assessments.length), "Criadas por você"],
      ["Alunos acompanhados", String(students.length), "Com dados de desempenho"],
      ["Correções pendentes", String(pending), "Respostas ainda pendentes"]
    ];
    actions = [
      ["🏫", "Minhas turmas", "Veja disciplinas e estudantes", "turmas"],
      ["📝", "Avaliações", "Consulte suas avaliações", "avaliacoes"],
      ["👥", "Acompanhar alunos", "Veja desempenho individual", "alunos"],
      ["📊", "Relatórios", "Analise turmas e dificuldades", "relatorios"]
    ];
    intro = "Acompanhe suas turmas, avaliações, alunos, correções e indicadores pedagógicos.";
    if (pending > 0) attention.push(`Há ${pending} correção(ões) pendente(s) nas suas avaliações.`);
  } else if (role === "administracao") {
    const summary = await safeApi("/admin/summary", {});
    stats = [
      ["Alunos", String(summary.total_alunos ?? 0), "Cadastrados"],
      ["Professores", String(summary.total_professores ?? 0), "Cadastrados"],
      ["Turmas", String(summary.total_turmas ?? 0), "No sistema"],
      ["Avaliações ativas", String(summary.avaliacoes_ativas ?? 0), `${summary.total_avaliacoes ?? 0} avaliação(ões) no total`]
    ];
    actions = [
      ["👥", "Usuários", "Cadastre alunos e professores", "usuarios"],
      ["🏫", "Turmas", "Consulte turmas da instituição", "turmas"],
      ["📝", "Avaliações", "Acompanhe avaliações lançadas", "avaliacoes"],
      ["📊", "Relatórios", "Veja indicadores institucionais", "relatorios"]
    ];
    intro = "Acompanhe cadastros, turmas, avaliações e indicadores institucionais.";
  } else {
    const users = await safeApi("/users/", []);
    const apiStatus = await safeApi("/", null);
    const admins = users.filter((u) => ["administracao", "administracao"].includes(normalizeRole(u.tipo))).length;
    stats = [
      ["Usuários", String(users.length), "Contas cadastradas"],
      ["Administração", String(admins), "Perfis administrativos"],
      ["Backend", apiStatus ? "Online" : "Indisponível", apiStatus ? "API respondeu corretamente" : "Verifique o servidor"],
      ["Chamados", "—", "Módulo previsto"]
    ];
    actions = [
      ["👥", "Usuários", "Consulte e cadastre usuários", "usuarios"],
      ["🛡", "Administração", "Consulte perfis administrativos", "administracao"],
      ["🩺", "Diagnóstico", "Confira o ambiente", "diagnostico"],
      ["💬", "Chamados", "Área reservada para atendimento", "chamados"]
    ];
    intro = "Acompanhe cadastros institucionais e o funcionamento básico do ambiente.";
  }

  $("#page-content").innerHTML = `
    <section class="hero-card"><p class="hero-kicker">Mentor.Edu</p><h2>Olá, ${escapeHtml(firstName)} 👋</h2><p>${escapeHtml(intro)}</p></section>
    <section class="card-grid" aria-label="Resumo">${stats.map((s) => statCard(...s)).join("")}</section>
    <section class="two-column">
      <article class="panel"><div class="panel__header"><h2>O que precisa de atenção</h2><span class="badge badge--info">Agora</span></div>
        <div class="item-list">${attention.length ? attention.map((text) => `<div class="item-row"><div><strong>${escapeHtml(text)}</strong><small>Abra a área correspondente para ver detalhes.</small></div><span class="badge badge--warning">Atenção</span></div>`).join("") : `<div class="item-row"><div><strong>Nenhuma pendência crítica identificada</strong><small>Use as ações rápidas para continuar.</small></div><span class="badge badge--success">Tudo certo</span></div>`}</div>
      </article>
      <aside class="panel" aria-labelledby="quick-title"><div class="panel__header"><h2 id="quick-title">Ações rápidas</h2></div><div class="quick-actions">${actions.map((a) => quickAction(...a)).join("")}</div></aside>
    </section>`;
  $$('[data-go]').forEach((button) => button.addEventListener("click", () => navigate(button.dataset.go)));
}

async function countTeacherPending(assessments) {
  let total = 0;
  for (const a of assessments.slice(0, 20)) {
    const results = await safeApi(`/assessments/${a.id}/results`, []);
    if (Array.isArray(results)) total += results.reduce((sum, r) => sum + Number(r.questoes_pendentes || 0), 0);
  }
  return total;
}

async function renderAssessments() {
  loading("Carregando avaliações…");
  try {
    const assessments = await api("/assessments/");
    if (!Array.isArray(assessments) || assessments.length === 0) {
      $("#page-content").innerHTML = `<section class="panel">${emptyState("Nenhuma avaliação disponível", "Quando houver uma avaliação vinculada ao seu perfil, ela aparecerá aqui.")}</section>`;
      return;
    }
    $("#page-content").innerHTML = `
      <section class="panel">
        <div class="panel__header"><div><h2>Avaliações</h2><p class="panel__subtitle">${assessments.length} registro(s) visível(is) para seu perfil.</p></div><span class="badge badge--info">${assessments.length}</span></div>
        <div class="assessment-grid">${assessments.map((a) => `
          <article class="assessment-card">
            <div class="assessment-card__top"><span class="badge ${a.ativa === false ? "badge--warning" : "badge--success"}">${a.ativa === false ? "Encerrada" : "Disponível"}</span><span class="assessment-card__date">${formatDate(a.data)}</span></div>
            <h3>${escapeHtml(a.titulo || "Avaliação")}</h3>
            <p>${escapeHtml(a.descricao || "Sem descrição.")}</p>
            <dl class="meta-grid"><div><dt>Tipo</dt><dd>${escapeHtml(a.tipo || "—")}</dd></div><div><dt>Valor</dt><dd>${formatNumber(a.valor || 0)} pts</dd></div></dl>
            <button class="button button--secondary button--block" type="button" data-assessment="${a.id}">Abrir avaliação</button>
          </article>`).join("")}</div>
      </section>`;
    $$('[data-assessment]').forEach((button) => button.addEventListener("click", () => renderAssessmentDetail(Number(button.dataset.assessment))));
  } catch (error) {
    showFeedback(error.message);
    $("#page-content").innerHTML = `<section class="panel">${emptyState("Não foi possível carregar as avaliações", "Verifique sua conexão com o backend e tente novamente.")}</section>`;
  }
}

async function renderAssessmentDetail(id) {
  loading("Abrindo avaliação…");
  try {
    const [assessment, questions] = await Promise.all([api(`/assessments/${id}`), api(`/assessments/${id}/questions`)]);
    const role = normalizeRole(state.user?.tipo);
    const answers = role === "aluno" ? await safeApi("/answers/me", []) : [];
    const answeredIds = new Set((answers || []).map((a) => a.question_id));
    const result = role === "aluno" ? await safeApi(`/assessments/${id}/results/me`, null) : null;

    $("#page-content").innerHTML = `
      <div class="page-inline-actions"><button class="button button--ghost" type="button" id="back-assessments">← Voltar às avaliações</button></div>
      <section class="panel assessment-detail">
        <div class="panel__header"><div><h2>${escapeHtml(assessment.titulo)}</h2><p class="panel__subtitle">${escapeHtml(assessment.tipo)} · ${formatDate(assessment.data)} · ${formatNumber(assessment.valor)} pontos</p></div><span class="badge ${assessment.ativa ? "badge--success" : "badge--warning"}">${assessment.ativa ? "Disponível" : "Encerrada"}</span></div>
        ${result ? `<div class="result-strip"><div><span>Respondidas</span><strong>${result.questoes_respondidas}/${result.total_questoes}</strong></div><div><span>Percentual</span><strong>${formatNumber(result.percentual)}%</strong></div><div><span>Nota</span><strong>${formatNumber(result.nota_final)}</strong></div></div>` : ""}
        <div class="question-list">${questions.length ? questions.map((q, index) => questionCard(q, index, role, answeredIds.has(q.id), assessment.ativa)).join("") : emptyState("Esta avaliação ainda não possui questões", "O professor poderá adicionar questões posteriormente.")}</div>
      </section>`;

    $("#back-assessments")?.addEventListener("click", renderAssessments);
    if (role === "aluno") {
      $$("form[data-answer-form]").forEach((form) => form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const questionId = Number(form.dataset.answerForm);
        const data = new FormData(form);
        const resposta = String(data.get("resposta") || "").trim();
        if (!resposta) return showFeedback("Selecione ou escreva uma resposta antes de enviar.");
        const submit = form.querySelector('button[type="submit"]');
        submit.disabled = true;
        submit.textContent = "Enviando…";
        try {
          await api(`/answers/questions/${questionId}`, { method: "POST", body: JSON.stringify({ resposta }) });
          showFeedback("Resposta enviada com sucesso.", "success");
          await renderAssessmentDetail(id);
        } catch (error) {
          showFeedback(error.message);
          submit.disabled = false;
          submit.textContent = "Enviar resposta";
        }
      }));
    }
  } catch (error) {
    showFeedback(error.message);
    $("#page-content").innerHTML = `<section class="panel">${emptyState("Não foi possível abrir esta avaliação", "Ela pode não estar disponível para seu perfil ou sua turma.")}</section>`;
  }
}

function questionCard(q, index, role, answered, active) {
  const isObjective = normalizeRole(q.tipo) === "objetiva";
  const status = answered ? `<span class="badge badge--success">Respondida</span>` : `<span class="badge badge--info">Pendente</span>`;
  let interaction = "";
  if (role === "aluno") {
    if (answered) {
      interaction = `<p class="question-note">Sua resposta já foi registrada. Consulte “Minhas respostas” para acompanhar.</p>`;
    } else if (!active) {
      interaction = `<p class="question-note">Esta avaliação está encerrada.</p>`;
    } else if (isObjective) {
      const opts = [["A", q.alternativa_a], ["B", q.alternativa_b], ["C", q.alternativa_c], ["D", q.alternativa_d]].filter(([, text]) => text);
      interaction = `<form class="answer-form" data-answer-form="${q.id}"><fieldset><legend>Escolha uma alternativa</legend>${opts.map(([letter, text]) => `<label class="option"><input type="radio" name="resposta" value="${letter}" required><span><strong>${letter}</strong> ${escapeHtml(text)}</span></label>`).join("")}</fieldset><button class="button button--primary" type="submit">Enviar resposta</button></form>`;
    } else {
      interaction = `<form class="answer-form" data-answer-form="${q.id}"><label class="field"><span>Escreva sua resposta</span><textarea name="resposta" required></textarea></label><button class="button button--primary" type="submit">Enviar resposta</button></form>`;
    }
  } else {
    interaction = `<dl class="meta-grid compact"><div><dt>Dificuldade</dt><dd>${escapeHtml(q.dificuldade || "—")}</dd></div><div><dt>Categoria</dt><dd>${escapeHtml(q.categoria || "—")}</dd></div><div><dt>Peso</dt><dd>${formatNumber(q.peso || 1)}</dd></div></dl>`;
  }
  return `<article class="question-card"><div class="question-card__header"><span class="question-number">Questão ${index + 1}</span>${role === "aluno" ? status : `<span class="badge badge--info">${escapeHtml(q.tipo)}</span>`}</div><h3>${escapeHtml(q.enunciado)}</h3>${interaction}</article>`;
}

async function renderAnswers() {
  loading("Carregando suas respostas…");
  try {
    const answers = await api("/answers/me");
    $("#page-content").innerHTML = `<section class="panel"><div class="panel__header"><h2>Respostas enviadas</h2><span class="badge badge--info">${answers.length}</span></div>${answers.length ? `<div class="item-list">${answers.slice().reverse().map((a) => `<div class="item-row"><div><strong>Questão #${a.question_id}</strong><small>Resposta: ${escapeHtml(a.resposta)} · ${a.percentual_final == null ? "Aguardando correção" : `${formatNumber(a.percentual_final, 0)}%`}</small></div><span class="badge ${a.percentual_final == null ? "badge--warning" : "badge--success"}">${a.percentual_final == null ? "Pendente" : "Corrigida"}</span></div>`).join("")}</div>` : emptyState("Você ainda não enviou respostas", "Abra uma avaliação disponível para começar.")}</section>`;
  } catch (error) { showFeedback(error.message); }
}

async function renderPerformance() {
  loading("Carregando seu desempenho…");
  try {
    const [summary, subjects, evolution] = await Promise.all([
      api("/assessments/summary/me"),
      api("/assessments/summary/me/subjects"),
      api("/assessments/summary/me/evolution")
    ]);
    $("#page-content").innerHTML = `
      <section class="card-grid">${statCard("Avaliações realizadas", summary.avaliacoes_realizadas ?? 0, "Com respostas registradas")}${statCard("Média geral", formatNumber(summary.media_geral ?? 0), "Nota média")}${statCard("Aproveitamento", `${formatNumber(summary.percentual_medio ?? 0)}%`, summary.status_geral || "Sem status")}${statCard("Melhor nota", summary.melhor_nota == null ? "—" : formatNumber(summary.melhor_nota), "Seu melhor resultado")}</section>
      <section class="two-column"><article class="panel"><div class="panel__header"><h2>Por disciplina</h2></div>${subjects.length ? `<div class="item-list">${subjects.map((s) => `<div class="item-row"><div><strong>Disciplina #${s.subject_id}</strong><small>${s.avaliacoes_realizadas} avaliação(ões) · média ${formatNumber(s.media)}</small></div><span class="badge badge--info">${formatNumber(s.percentual_medio)}%</span></div>`).join("")}</div>` : emptyState("Ainda não há dados por disciplina", "Os dados aparecerão após suas avaliações serem corrigidas.")}</article><article class="panel"><div class="panel__header"><h2>Evolução</h2></div>${evolution.length ? `<div class="item-list">${evolution.map((e) => `<div class="item-row"><div><strong>${e.ano_letivo} · ${e.semestre ? `${e.semestre}º semestre` : "Semestre não informado"}</strong><small>${e.avaliacoes_realizadas} avaliação(ões) · ${escapeHtml(e.status)}</small></div><span class="badge badge--success">${formatNumber(e.percentual_medio)}%</span></div>`).join("")}</div>` : emptyState("Sem evolução calculada", "É necessário ter avaliações realizadas em períodos cadastrados.")}</article></section>`;
  } catch (error) { showFeedback(error.message); }
}

async function renderHistory() {
  loading("Carregando histórico…");
  try {
    const history = await api("/assessments/history/me");
    $("#page-content").innerHTML = `<section class="panel"><div class="panel__header"><h2>Histórico de avaliações</h2><span class="badge badge--info">${history.length}</span></div>${history.length ? `<div class="item-list">${history.slice().reverse().map((h) => `<div class="item-row"><div><strong>${escapeHtml(h.titulo || `Avaliação #${h.assessment_id}`)}</strong><small>${h.ano_letivo || "Ano não informado"}${h.semestre ? ` · ${h.semestre}º semestre` : ""}</small></div><div class="row-metrics"><span>${formatNumber(h.nota_final)} pts</span><span class="badge badge--info">${formatNumber(h.percentual)}%</span></div></div>`).join("")}</div>` : emptyState("Seu histórico ainda está vazio", "Avaliações respondidas aparecerão aqui.")}</section>`;
  } catch (error) {
    showFeedback(error.message);
    $("#page-content").innerHTML = `<section class="panel">${emptyState("Não foi possível carregar o histórico", "O endpoint de histórico precisa ser corrigido no backend antes de esta tela funcionar.")}</section>`;
  }
}

async function renderClassrooms() {
  loading("Carregando turmas…");
  const role = normalizeRole(state.user?.tipo);
  try {
    if (role === "professor") {
      const classrooms = await api("/teachers/me/classrooms");
      $("#page-content").innerHTML = `<section class="panel"><div class="panel__header"><h2>Minhas turmas</h2><span class="badge badge--info">${classrooms.length}</span></div>${classrooms.length ? `<div class="assessment-grid">${classrooms.map((c) => `<article class="assessment-card"><h3>${escapeHtml(c.turma)}</h3><p>${escapeHtml(c.disciplina)} · ${escapeHtml(c.serie)} · ${escapeHtml(c.turno)}</p><dl class="meta-grid"><div><dt>Ano</dt><dd>${c.ano}</dd></div><div><dt>Alunos</dt><dd>${c.alunos?.length ?? 0}</dd></div></dl>${c.alunos?.length ? `<details><summary>Ver alunos</summary><ul class="simple-list">${c.alunos.map((s) => `<li>${escapeHtml(s.nome)}</li>`).join("")}</ul></details>` : ""}</article>`).join("")}</div>` : emptyState("Nenhuma turma vinculada", "O professor precisa estar associado a uma disciplina e turma no backend.")}</section>`;
    } else {
      const classrooms = await api("/admin/classrooms");
      $("#page-content").innerHTML = `<section class="panel"><div class="panel__header"><h2>Turmas da instituição</h2><span class="badge badge--info">${classrooms.length}</span></div><div class="item-list">${classrooms.map((c) => `<div class="item-row"><div><strong>${escapeHtml(c.nome)}</strong><small>ID ${c.classroom_id}${c.ano_letivo ? ` · ${c.ano_letivo}` : ""}</small></div><span class="badge badge--success">Ativa</span></div>`).join("")}</div></section>`;
    }
  } catch (error) { showFeedback(error.message); }
}

async function renderStudents() {
  loading("Carregando alunos…");
  try {
    const students = await api("/assessments/teacher/students/performance");
    $("#page-content").innerHTML = `<section class="panel"><div class="panel__header"><h2>Desempenho dos alunos</h2><span class="badge badge--info">${students.length}</span></div>${students.length ? `<div class="responsive-table"><table><thead><tr><th>Aluno</th><th>Avaliações</th><th>Média</th><th>Aproveitamento</th><th>Status</th></tr></thead><tbody>${students.map((s) => `<tr><td>${escapeHtml(s.nome)}</td><td>${s.avaliacoes_realizadas}</td><td>${formatNumber(s.media)}</td><td>${formatNumber(s.percentual_medio)}%</td><td><span class="badge badge--info">${escapeHtml(s.status)}</span></td></tr>`).join("")}</tbody></table></div>` : emptyState("Ainda não há desempenho disponível", "Os alunos aparecerão após participarem das avaliações deste professor.")}</section>`;
  } catch (error) { showFeedback(error.message); }
}

async function renderCorrections() {
  loading("Carregando correções…");
  try {
    const assessments = await api("/assessments/");
    const rows = [];
    for (const a of assessments) {
      const results = await safeApi(`/assessments/${a.id}/results`, []);
      const pending = Array.isArray(results) ? results.reduce((sum, r) => sum + Number(r.questoes_pendentes || 0), 0) : 0;
      const students = Array.isArray(results) ? results.length : 0;
      rows.push({ a, pending, students });
    }
    $("#page-content").innerHTML = `<section class="panel"><div class="panel__header"><h2>Correções por avaliação</h2><span class="badge badge--info">${rows.reduce((s, r) => s + r.pending, 0)} pendente(s)</span></div>${rows.length ? `<div class="item-list">${rows.map(({a, pending, students}) => `<div class="item-row"><div><strong>${escapeHtml(a.titulo)}</strong><small>${students} aluno(s) com resultado · ${pending} questão(ões) pendente(s)</small></div><span class="badge ${pending ? "badge--warning" : "badge--success"}">${pending ? "Pendente" : "Em dia"}</span></div>`).join("")}</div><div class="notice-card"><strong>Próxima melhoria necessária</strong><p>O backend ainda precisa de uma rota para listar as respostas discursivas pendentes com o <code>answer_id</code>. Sem isso, a tela não consegue abrir cada resposta diretamente para revisão.</p></div>` : emptyState("Nenhuma avaliação encontrada", "Crie avaliações para acompanhar correções.")}</section>`;
  } catch (error) { showFeedback(error.message); }
}

async function renderReports() {
  loading("Gerando visão de relatórios…");
  const role = normalizeRole(state.user?.tipo);
  try {
    if (role === "professor") {
      const [classrooms, questions] = await Promise.all([safeApi("/assessments/teacher/summary/classrooms", []), safeApi("/assessments/teacher/questions/difficulties", [])]);
      $("#page-content").innerHTML = `<section class="two-column"><article class="panel"><div class="panel__header"><h2>Resumo por turma</h2></div>${classrooms.length ? `<div class="item-list">${classrooms.map((c) => `<div class="item-row"><div><strong>Turma #${c.classroom_id}</strong><small>${c.avaliacoes_criadas} avaliação(ões) · ${c.alunos_avaliados} aluno(s)</small></div><span class="badge badge--info">${formatNumber(c.percentual_medio)}%</span></div>`).join("")}</div>` : emptyState("Sem dados por turma", "Crie avaliações e registre respostas para gerar indicadores.")}</article><article class="panel"><div class="panel__header"><h2>Questões com dificuldade</h2></div>${questions.length ? `<div class="item-list">${questions.slice(0, 10).map((q) => `<div class="item-row"><div><strong>Questão #${q.question_id}</strong><small>${escapeHtml(q.categoria || "Sem categoria")} · ${q.respostas_com_erro}/${q.total_respostas} resposta(s) com erro · ${escapeHtml(q.dificuldade || "")}</small></div><span class="badge badge--warning">${formatNumber(q.percentual_erro ?? 0)}% erro</span></div>`).join("")}</div>` : emptyState("Sem questões críticas", "Ainda não há dados suficientes para esta análise.")}</article></section>`;
    } else {
      const [summary, teachers, students] = await Promise.all([api("/admin/summary"), api("/admin/teachers"), api("/admin/students")]);
      $("#page-content").innerHTML = `<section class="card-grid">${statCard("Alunos", summary.total_alunos, "Cadastrados")}${statCard("Professores", summary.total_professores, "Cadastrados")}${statCard("Turmas", summary.total_turmas, "Cadastradas")}${statCard("Avaliações", summary.total_avaliacoes, `${summary.avaliacoes_ativas} ativa(s)`)}</section><section class="two-column"><article class="panel"><div class="panel__header"><h2>Professores</h2></div><div class="item-list">${teachers.slice(0, 10).map((t) => `<div class="item-row"><div><strong>${escapeHtml(t.nome)}</strong><small>${escapeHtml(t.especialidade || "Especialidade não informada")}</small></div><span class="badge ${t.ativo ? "badge--success" : "badge--warning"}">${t.ativo ? "Ativo" : "Inativo"}</span></div>`).join("")}</div></article><article class="panel"><div class="panel__header"><h2>Alunos</h2></div><div class="item-list">${students.slice(0, 10).map((s) => `<div class="item-row"><div><strong>${escapeHtml(s.nome)}</strong><small>${escapeHtml(s.serie || "Série não informada")}</small></div></div>`).join("")}</div></article></section>`;
    }
  } catch (error) { showFeedback(error.message); }
}

async function renderUsers(filterAdminsOnly = false) {
  loading("Carregando usuários…");
  try {
    const [users, classrooms] = await Promise.all([api("/users/"), safeApi("/classrooms", [])]);
    const role = normalizeRole(state.user?.tipo);
    const visibleUsers = filterAdminsOnly ? users.filter((u) => normalizeRole(u.tipo) === "administracao") : users;
    const allowedTypes = role === "suporte" ? [["Aluno","Aluno"],["Professor","Professor"],["Administracao","Administração"]] : [["Aluno","Aluno"],["Professor","Professor"]];

    $("#page-content").innerHTML = `
      <section class="two-column users-layout">
        <article class="panel"><div class="panel__header"><div><h2>${filterAdminsOnly ? "Integrantes da administração" : "Usuários cadastrados"}</h2><p class="panel__subtitle">${visibleUsers.length} registro(s)</p></div></div>${visibleUsers.length ? `<div class="item-list users-list">${visibleUsers.map((u) => `<div class="item-row"><div><strong>${escapeHtml(u.nome)}</strong><small>${escapeHtml(u.email)} · ${escapeHtml(u.tipo)}</small></div>${u.classroom_id ? `<span class="badge badge--info">Turma ${u.classroom_id}</span>` : ""}</div>`).join("")}</div>` : emptyState("Nenhum usuário encontrado", "Os registros aparecerão aqui.")}</article>
        <aside class="panel"><div class="panel__header"><h2>Novo cadastro</h2></div><form id="user-create-form" class="form-stack"><label class="field"><span>Nome</span><input name="nome" required></label><label class="field"><span>E-mail</span><input type="email" name="email" required></label><label class="field"><span>Senha inicial</span><input type="password" name="senha" minlength="6" required></label><label class="field"><span>Perfil</span><select name="tipo" id="new-user-type" required>${allowedTypes.map(([v,l]) => `<option value="${v}">${l}</option>`).join("")}</select></label><label class="field" id="classroom-field"><span>Turma do aluno</span><select name="classroom_id"><option value="">Selecione</option>${classrooms.map((c) => `<option value="${c.id}">${escapeHtml(c.nome)} · ${escapeHtml(c.serie || "")}</option>`).join("")}</select></label><label class="field"><span>Escola</span><input name="escola"></label><button class="button button--primary button--block" type="submit">Cadastrar usuário</button><p class="form-hint">O cadastro é institucional. Administração cria alunos/professores; Suporte também pode criar Administração.</p></form></aside>
      </section>`;
    const typeSelect = $("#new-user-type");
    const classroomField = $("#classroom-field");
    const syncClassroom = () => classroomField.hidden = normalizeRole(typeSelect.value) !== "aluno";
    typeSelect.addEventListener("change", syncClassroom); syncClassroom();
    $("#user-create-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const fd = new FormData(event.currentTarget);
      const tipo = String(fd.get("tipo") || "");
      const classroom = String(fd.get("classroom_id") || "");
      const payload = { nome: String(fd.get("nome") || "").trim(), email: String(fd.get("email") || "").trim(), senha: String(fd.get("senha") || ""), tipo, escola: String(fd.get("escola") || "").trim() || null, classroom_id: normalizeRole(tipo) === "aluno" && classroom ? Number(classroom) : null };
      try {
        await api("/users/register", { method: "POST", body: JSON.stringify(payload) });
        showFeedback(normalizeRole(tipo) === "professor" ? "Conta de professor criada. Atenção: o backend ainda precisa automatizar a criação do perfil Teacher para que todas as funções docentes sejam liberadas." : "Usuário cadastrado com sucesso.", "success");
        await renderUsers(filterAdminsOnly);
      } catch (error) { showFeedback(error.message); }
    });
  } catch (error) { showFeedback(error.message); }
}

async function renderAdminAssessments() {
  loading("Carregando avaliações da instituição…");
  try {
    const assessments = await api("/admin/assessments");
    $("#page-content").innerHTML = `<section class="panel"><div class="panel__header"><h2>Avaliações da instituição</h2><span class="badge badge--info">${assessments.length}</span></div>${assessments.length ? `<div class="responsive-table"><table><thead><tr><th>Avaliação</th><th>Tipo</th><th>Turma</th><th>Professor</th><th>Status</th></tr></thead><tbody>${assessments.map((a) => `<tr><td>${escapeHtml(a.titulo)}</td><td>${escapeHtml(a.tipo)}</td><td>#${a.classroom_id}</td><td>#${a.teacher_id}</td><td><span class="badge ${a.ativa ? "badge--success" : "badge--warning"}">${a.ativa ? "Ativa" : "Encerrada"}</span></td></tr>`).join("")}</tbody></table></div>` : emptyState("Nenhuma avaliação cadastrada", "As avaliações criadas pelos professores aparecerão aqui.")}</section>`;
  } catch (error) { showFeedback(error.message); }
}

async function renderDiagnostic() {
  loading("Verificando ambiente…");
  const [root, users] = await Promise.all([safeApi("/", null), safeApi("/users/", [])]);
  $("#page-content").innerHTML = `<section class="card-grid">${statCard("Backend", root ? "Online" : "Indisponível", root?.message || "Sem resposta")}${statCard("Frontend", "Online", "Interface carregada")}${statCard("Usuários", users.length, "Contas acessíveis ao suporte")}${statCard("Sessão", state.token ? "Autenticada" : "Sem token", "Token local do navegador")}</section><section class="panel"><div class="panel__header"><h2>Diagnóstico básico</h2><span class="badge ${root ? "badge--success" : "badge--warning"}">${root ? "Operacional" : "Atenção"}</span></div><div class="notice-card"><strong>Limite desta tela</strong><p>Este diagnóstico confirma comunicação básica com a API. Logs, banco, fila de e-mails e monitoramento de infraestrutura precisam de endpoints específicos antes de serem exibidos aqui.</p></div></section>`;
}

function renderPlanned(page) {
  const [, title] = pageMeta[page] || ["", "Página"];
  $("#page-content").innerHTML = `<section class="panel"><div class="panel__header"><h2>${escapeHtml(title)}</h2><span class="badge badge--warning">Planejado</span></div>${emptyState("Módulo ainda não disponível no backend", page === "chamados" ? "Esta área receberá chamados internos, responsáveis, prioridade, prazo e status." : "Esta área receberá notificações de atividades, provas, prazos e chamados.")}</section>`;
}

function renderProfile() {
  const u = state.user || {};
  $("#page-content").innerHTML = `<section class="two-column"><article class="panel"><div class="panel__header"><h2>Dados da conta</h2><span class="badge badge--success">${escapeHtml(u.tipo || "Usuário")}</span></div><div class="profile-grid"><div><span>Nome</span><strong>${escapeHtml(u.nome || "—")}</strong></div><div><span>E-mail</span><strong>${escapeHtml(u.email || "—")}</strong></div><div><span>Escola</span><strong>${escapeHtml(u.escola || "Não informada")}</strong></div><div><span>Série</span><strong>${escapeHtml(u.serie || "Não se aplica")}</strong></div><div><span>Turma</span><strong>${u.classroom_id ? `#${u.classroom_id}` : "Não se aplica"}</strong></div><div><span>Horas de estudo</span><strong>${u.horas_estudo ?? "Não informado"}</strong></div></div></article><aside class="panel"><div class="panel__header"><h2>Segurança da conta</h2></div><div class="notice-card"><strong>Conta institucional</strong><p>Tipo de usuário e turma não podem ser alterados pelo próprio usuário. Essas mudanças devem passar pela Administração ou Suporte.</p></div></aside></section>`;
}

function renderHelp() {
  $("#page-content").innerHTML = `<section class="two-column"><article class="panel"><div class="panel__header"><h2>Como usar</h2></div><div class="item-list"><div class="item-row"><div><strong>1. Use o menu principal</strong><small>As opções mudam de acordo com seu perfil.</small></div></div><div class="item-row"><div><strong>2. Comece pela página Início</strong><small>Ela reúne os principais números e atalhos.</small></div></div><div class="item-row"><div><strong>3. Avaliações e resultados têm áreas próprias</strong><small>Evite procurar respostas enviadas dentro da lista de avaliações.</small></div></div><div class="item-row"><div><strong>4. Em caso de dúvida, procure a instituição</strong><small>O módulo Chamados será conectado ao backend em uma próxima etapa.</small></div></div></div></article><aside class="panel"><div class="panel__header"><h2>Acessibilidade</h2></div><p>Use <strong>A−</strong>, <strong>A+</strong> e <strong>◐</strong> no topo para ajustar a leitura. A interface possui foco visível, navegação por teclado e adaptação para telas menores.</p></aside></section>`;
}

async function renderPage(page) {
  clearFeedback();
  $("#page-actions").innerHTML = "";
  const role = normalizeRole(state.user?.tipo);

  if (page === "inicio") return renderHome();
  if (page === "avaliacoes") return role === "administracao" ? renderAdminAssessments() : renderAssessments();
  if (page === "respostas" && role === "aluno") return renderAnswers();
  if (page === "desempenho" && role === "aluno") return renderPerformance();
  if (page === "historico" && role === "aluno") return renderHistory();
  if (page === "turmas" && ["professor", "administracao"].includes(role)) return renderClassrooms();
  if (page === "alunos" && role === "professor") return renderStudents();
  if (page === "correcoes" && role === "professor") return renderCorrections();
  if (page === "relatorios" && ["professor", "administracao"].includes(role)) return renderReports();
  if (page === "usuarios" && ["administracao", "suporte"].includes(role)) return renderUsers(false);
  if (page === "administracao" && role === "suporte") return renderUsers(true);
  if (page === "diagnostico" && role === "suporte") return renderDiagnostic();
  if (["chamados", "notificacoes"].includes(page)) return renderPlanned(page);
  if (page === "perfil") return renderProfile();
  if (page === "ajuda") return renderHelp();

  $("#page-content").innerHTML = `<section class="panel">${emptyState("Área indisponível para este perfil", "Use o menu lateral para acessar as funções autorizadas.")}</section>`;
}

function showFeedback(message, type = "error") {
  const el = $("#feedback-message");
  el.textContent = message || "";
  el.dataset.type = type;
}
function clearFeedback() { const el = $("#feedback-message"); el.textContent = ""; el.dataset.type = ""; }
function openSidebar() { $("#sidebar").classList.add("is-open"); $("#sidebar-backdrop").hidden = false; $("#menu-button").setAttribute("aria-expanded", "true"); }
function closeSidebar() { $("#sidebar").classList.remove("is-open"); $("#sidebar-backdrop").hidden = true; $("#menu-button").setAttribute("aria-expanded", "false"); }

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = $("#email").value;
  const senha = $("#senha").value;
  $("#login-message").textContent = "Entrando…";
  try {
    await login(email, senha);
    $("#login-message").textContent = "";
    showApp();
  } catch (error) {
    $("#login-message").textContent = error.message;
  }
});

$("#toggle-password").addEventListener("click", () => {
  const input = $("#senha");
  const visible = input.type === "text";
  input.type = visible ? "password" : "text";
  $("#toggle-password").setAttribute("aria-pressed", String(!visible));
  $("#toggle-password").setAttribute("aria-label", visible ? "Mostrar senha" : "Ocultar senha");
});

$("#logout-button").addEventListener("click", () => {
  localStorage.removeItem("mentor_token");
  state.token = "";
  state.user = null;
  showLogin("Você saiu da sua conta.");
});

$("#notification-button").addEventListener("click", () => navigate("notificacoes"));
$("#menu-button").addEventListener("click", () => $("#sidebar").classList.contains("is-open") ? closeSidebar() : openSidebar());
$("#sidebar-backdrop").addEventListener("click", closeSidebar);

$("#increase-font").addEventListener("click", () => {
  state.fontScale = Math.min(1.25, +(state.fontScale + .1).toFixed(2));
  localStorage.setItem("mentor_font_scale", state.fontScale);
  applyAccessibilityPreferences();
});
$("#decrease-font").addEventListener("click", () => {
  state.fontScale = Math.max(.9, +(state.fontScale - .1).toFixed(2));
  localStorage.setItem("mentor_font_scale", state.fontScale);
  applyAccessibilityPreferences();
});
$("#contrast-button").addEventListener("click", () => {
  state.highContrast = !state.highContrast;
  localStorage.setItem("mentor_high_contrast", String(state.highContrast));
  applyAccessibilityPreferences();
});

window.addEventListener("keydown", (event) => { if (event.key === "Escape") closeSidebar(); });

(async function init() {
  applyAccessibilityPreferences();
  const restored = await restoreSession();
  restored ? showApp() : showLogin();
})();
