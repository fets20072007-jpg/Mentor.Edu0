
const state = {
  mode: 'demo',
  role: 'aluno',
  apiUrl: localStorage.getItem('mentor_api') || 'http://127.0.0.1:8000',
  token: localStorage.getItem('mentor_token') || '',
  currentUser: null,
  currentPage: 'dashboard'
};

const DEMO = {
  aluno: {
    user: { nome: 'Ana Beatriz', tipo: 'Aluno', avatar: 'AB', tags: ['3º A', '2026'] },
    nav: [
      ['dashboard', '⌂', 'Visão geral'],
      ['subjects', '▦', 'Disciplinas'],
      ['assessments', '✓', 'Avaliações', '2'],
      ['grades', '★', 'Notas'],
      ['attendance', '◷', 'Frequência'],
      ['record', '▤', 'Histórico'],
      ['study', '◎', 'Plano de estudos'],
      ['recommendations', '✦', 'Recomendações'],
      ['library', '▣', 'Biblioteca'],
      ['calendar', '□', 'Calendário'],
      ['profile', '○', 'Perfil']
    ]
  },
  professor: {
    user: { nome: 'Prof. Estevão', tipo: 'Professor / DT', avatar: 'ES', tags: ['Física', 'DT 3A'] },
    nav: [
      ['dashboard', '⌂', 'Visão geral'],
      ['classrooms', '▥', 'Minhas turmas'],
      ['assessments', '✓', 'Avaliações'],
      ['attendance', '◷', 'Frequência', '3'],
      ['grades', '★', 'Notas'],
      ['questionbank', '?', 'Banco de questões'],
      ['analytics', '↗', 'Desempenho'],
      ['library', '▣', 'Biblioteca'],
      ['calendar', '□', 'Calendário'],
      ['tickets', '◇', 'Chamados'],
      ['profile', '○', 'Perfil']
    ]
  },
  administracao: {
    user: { nome: 'Maria Lena', tipo: 'Administração', avatar: 'ML', tags: ['Gestão', 'Institucional'] },
    nav: [
      ['dashboard', '⌂', 'Visão geral'],
      ['users', '♙', 'Usuários'],
      ['teachers', '♟', 'Professores'],
      ['classrooms', '▥', 'Turmas'],
      ['subjects', '▦', 'Disciplinas'],
      ['enrollments', '⊕', 'Matrículas'],
      ['dt', '◆', 'Diretores de turma'],
      ['reports', '↗', 'Relatórios'],
      ['library', '▣', 'Biblioteca'],
      ['calendar', '□', 'Calendário'],
      ['profile', '○', 'Perfil']
    ]
  },
  suporte: {
    user: { nome: 'Equipe Suporte', tipo: 'Suporte', avatar: 'ST', tags: ['Operacional', 'Sistema'] },
    nav: [
      ['dashboard', '⌂', 'Visão geral'],
      ['tickets', '◇', 'Chamados', '5'],
      ['system', '⌁', 'Saúde do sistema'],
      ['users', '♙', 'Cadastro institucional'],
      ['library', '▣', 'Acervo técnico'],
      ['logs', '≡', 'Auditoria'],
      ['profile', '○', 'Perfil']
    ]
  }
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function showToast(message) {
  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = message;
  $('#toast-root').appendChild(el);
  setTimeout(() => el.remove(), 2600);
}

function initials(name = '') {
  return name.split(/\s+/).filter(Boolean).slice(0, 2).map(x => x[0]).join('').toUpperCase() || 'ME';
}

function normalizeRole(tipo = '') {
  const value = (tipo || '').trim().toLowerCase();
  if (value === 'aluno') return 'aluno';
  if (value === 'professor') return 'professor';
  if (value === 'suporte') return 'suporte';
  return 'administracao';
}

function currentMeta() {
  if (state.mode === 'live' && state.currentUser) {
    return {
      nome: state.currentUser.nome || 'Usuário',
      tipo: state.currentUser.tipo || 'Usuário',
      avatar: initials(state.currentUser.nome || 'Usuário'),
      tags: [state.currentUser.tipo || 'Perfil']
    };
  }
  return DEMO[state.role].user;
}

function hero(kicker, title, description, actions = '') {
  return `
    <div class="page-hero">
      <div>
        <span class="eyebrow">${kicker}</span>
        <h2>${title}</h2>
        <p>${description}</p>
      </div>
      <div class="page-hero-actions">${actions}</div>
    </div>
  `;
}

function metric(label, value, note) {
  return `
    <div class="metric-card">
      <div class="metric-label">${label}</div>
      <div class="metric-value">${value}</div>
      <div class="metric-note">${note}</div>
    </div>
  `;
}

function panel(title, subtitle, body, col = 6, action = '') {
  return `
    <div class="panel-card col-${col}">
      <div class="panel-head">
        <div>
          <h3>${title}</h3>
          ${subtitle ? `<p>${subtitle}</p>` : ''}
        </div>
        ${action}
      </div>
      ${body}
    </div>
  `;
}

function barChart(values) {
  return `<div class="chart-bars">${values.map(v => `<span style="height:${v}%"></span>`).join('')}</div>`;
}

function progressRow(label, value) {
  return `
    <div class="progress-row">
      <span>${label}</span>
      <div class="progress-track"><div class="progress-fill" style="width:${value}%"></div></div>
      <span class="progress-value">${value}%</span>
    </div>
  `;
}

function status(text, type = 'info') {
  return `<span class="status ${type}">${text}</span>`;
}

function inlinePerson(name, sub, avatar) {
  return `
    <div class="inline-person">
      <span class="inline-mini-avatar">${avatar}</span>
      <div>
        <div>${name}</div>
        <small style="color:#64748b">${sub}</small>
      </div>
    </div>
  `;
}

function listItem(icon, title, text, side = '') {
  return `
    <div class="list-item">
      <div class="list-icon">${icon}</div>
      <div class="list-body">
        <strong>${title}</strong>
        <span>${text}</span>
      </div>
      ${side ? `<div class="list-side">${side}</div>` : ''}
    </div>
  `;
}

function table(headers, rows) {
  return `
    <div class="table-wrap">
      <table class="table">
        <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
        <tbody>${rows.join('')}</tbody>
      </table>
    </div>
  `;
}

const PAGES = {
  aluno: {
    dashboard: () => hero('ALUNO', 'Seu aprendizado em um só lugar', 'Acompanhe desempenho, frequência e próximos passos com base nos seus resultados.', `<button class="btn btn-soft" data-goto="study">Ver plano de estudos</button>`) +
      `<div class="grid">
        ${metric('Média geral', '8,2', '+0,6 neste bimestre')}
        ${metric('Frequência', '92%', 'Acima do mínimo esperado')}
        ${metric('Avaliações pendentes', '2', 'Próxima: Física • 12 nov')}
        ${metric('Plano semanal', '74%', '4 de 6 atividades concluídas')}
        ${panel('Evolução do desempenho', 'Últimos 6 registros', barChart([52, 60, 56, 72, 78, 84]), 8)}
        ${panel('Desempenho por disciplina', 'Percentual consolidado', `<div class="progress-list">${progressRow('Física', 88)}${progressRow('Matemática', 81)}${progressRow('Química', 72)}${progressRow('Português', 90)}</div>`, 4)}
        ${panel('Próximas atividades', '', `<div class="list">${listItem('✓', 'Avaliação — Cinemática', 'Física • 12 nov • 08:00', status('Em breve', 'warn'))}${listItem('◎', 'Revisão — Vetores', 'Plano de estudos • 14 nov', status('Planejado', 'info'))}${listItem('▣', 'Leitura recomendada', 'Capítulo 4 • Mecânica', status('Novo', 'ok'))}</div>`, 6)}
        ${panel('Frequência', 'Resumo do período', `<div class="note-box"><strong>Resumo:</strong> você está dentro da faixa segura de presença. Continue acompanhando as faltas justificadas e as avaliações da semana.</div>`, 6)}
      </div>`,
    subjects: () => subjectsPage(false),
    assessments: () => assessmentsPage(false),
    grades: () => gradesPage(false),
    attendance: () => attendanceStudentPage(),
    record: () => recordPage(),
    study: () => studyPage(),
    recommendations: () => recommendationsPage(),
    library: () => libraryPage('aluno'),
    calendar: () => calendarPage(),
    profile: () => profilePage()
  },
  professor: {
    dashboard: () => hero('PROFESSOR / DT', 'Bom trabalho, Estevão', 'Visão consolidada das suas disciplinas e da turma 3A, onde você atua como Diretor de Turma.', `<button class="btn btn-soft" data-goto="assessments">Nova avaliação</button>`) +
      `<div class="grid">
        ${metric('Turmas de atuação', '3', '3A • 3B • 2C')}
        ${metric('Alunos acompanhados', '86', '31 alunos na turma DT')}
        ${metric('Avaliações ativas', '8', '2 aguardando correção')}
        ${metric('Frequência média', '89%', 'Turma DT 3A')}
        ${panel('Desempenho das turmas', 'Média percentual das avaliações', barChart([78, 84, 69, 88, 81, 75]), 8)}
        ${panel('Turma DT — 3A', 'Acompanhamento ampliado', `<div class="note-box"><strong>Regra DT:</strong> visão acadêmica ampliada da própria turma, sem editar avaliações ou notas de outros professores.</div>`, 4)}
        ${panel('Alunos que precisam de atenção', 'Menor desempenho', `<div class="list">${listItem('LM', 'Lucas Moura', '3A • 61%', status('Atenção', 'bad'))}${listItem('CS', 'Camila Sousa', '3A • 68%', status('Regular', 'warn'))}${listItem('JP', 'João Pedro', '3B • 72%', status('Regular', 'warn'))}</div>`, 6)}
        ${panel('Pendências de hoje', '', `<div class="quick-actions"><button class="quick-action" data-goto="attendance"><span class="quick-action-icon">◷</span><strong>3 frequências</strong><small>Aguardando fechamento</small></button><button class="quick-action" data-goto="assessments"><span class="quick-action-icon">✓</span><strong>2 correções</strong><small>Respostas abertas</small></button><button class="quick-action" data-goto="questionbank"><span class="quick-action-icon">?</span><strong>Banco</strong><small>42 questões</small></button><button class="quick-action" data-goto="analytics"><span class="quick-action-icon">↗</span><strong>Analytics</strong><small>Ver dificuldades</small></button></div>`, 6)}
      </div>`,
    classrooms: () => classroomsPage(),
    assessments: () => assessmentsPage(true),
    attendance: () => attendanceTeacherPage(),
    grades: () => gradesPage(true),
    questionbank: () => questionBankPage(),
    analytics: () => analyticsPage(),
    library: () => libraryPage('professor'),
    calendar: () => calendarPage(),
    tickets: () => ticketsPage(),
    profile: () => profilePage()
  },
  administracao: {
    dashboard: () => hero('ADMINISTRAÇÃO', 'Painel institucional', 'Gerencie usuários, turmas, disciplinas, matrículas e funções de Diretor de Turma em um só ambiente.', `<button class="btn btn-soft" data-goto="users">Cadastrar usuário</button>`) +
      `<div class="grid">
        ${metric('Usuários ativos', '214', '183 alunos • 18 professores')}
        ${metric('Turmas ativas', '12', 'Ano letivo 2026')}
        ${metric('Professores', '18', '3 Diretores de Turma')}
        ${metric('Matrículas', '183', '100% vinculadas')}
        ${panel('Distribuição de usuários', 'Cadastros institucionais', barChart([94, 58, 41, 29]), 7)}
        ${panel('Situação das turmas', '', `<div class="list">${listItem('3A', '3º A', '31 alunos • Manhã', status('DT definido', 'ok'))}${listItem('3B', '3º B', '29 alunos • Tarde', status('DT definido', 'ok'))}${listItem('2C', '2º C', '33 alunos • Tarde', status('Sem DT', 'warn'))}</div>`, 5)}
        ${panel('Ações administrativas', '', `<div class="quick-actions"><button class="quick-action" data-goto="users"><span class="quick-action-icon">♙</span><strong>Novo usuário</strong><small>Aluno ou professor</small></button><button class="quick-action" data-goto="classrooms"><span class="quick-action-icon">▥</span><strong>Nova turma</strong><small>Organização anual</small></button><button class="quick-action" data-goto="enrollments"><span class="quick-action-icon">⊕</span><strong>Matrícula</strong><small>Vincular aluno</small></button><button class="quick-action" data-goto="dt"><span class="quick-action-icon">◆</span><strong>Definir DT</strong><small>Professor da turma</small></button></div>`, 12)}
      </div>`,
    users: () => usersPage('administracao'),
    teachers: () => teachersPage(),
    classrooms: () => adminClassroomsPage(),
    subjects: () => subjectsPage(true),
    enrollments: () => enrollmentsPage(),
    dt: () => dtPage(),
    reports: () => reportsPage(),
    library: () => libraryPage('administracao'),
    calendar: () => calendarPage(),
    profile: () => profilePage()
  },
  suporte: {
    dashboard: () => hero('SUPORTE', 'Painel operacional', 'Acompanhe a saúde do sistema, chamados e acervo técnico sem acessar dados pedagógicos dos alunos.', `<button class="btn btn-soft" data-goto="tickets">Ver chamados</button>`) +
      `<div class="grid">
        ${metric('Serviços online', '6/6', 'API • Banco • Auth')}
        ${metric('Chamados abertos', '5', '2 com prioridade alta')}
        ${metric('Acervo institucional', '128', 'Livros cadastrados')}
        ${metric('Último backup', '02:10', 'Executado com sucesso')}
        ${panel('Saúde dos serviços', '', `<div class="list">${listItem('⌁', 'API FastAPI', '18 ms', status('Online', 'ok'))}${listItem('⌁', 'Banco SQLite', '4 ms', status('Online', 'ok'))}${listItem('⌁', 'Autenticação JWT', '11 ms', status('Online', 'ok'))}${listItem('⌁', 'Armazenamento', '34% utilizado', status('Online', 'ok'))}</div>`, 7)}
        ${panel('Permissões do Suporte', '', `<div class="note-box">O perfil Suporte gerencia operação, cadastro de Administração e acervo técnico. <strong>Não acessa notas, avaliações, frequência ou histórico pedagógico.</strong></div>`, 5)}
        ${panel('Chamados recentes', 'Fila operacional', ticketsTable(), 12)}
      </div>`,
    tickets: () => ticketsPage(),
    system: () => systemPage(),
    users: () => usersPage('suporte'),
    library: () => libraryPage('suporte'),
    logs: () => logsPage(),
    profile: () => profilePage()
  }
};

function subjectsPage(admin) {
  return hero('DISCIPLINAS', admin ? 'Gestão das disciplinas' : 'Minhas disciplinas', admin ? 'Vínculos entre professor, turma e componente curricular.' : 'Conteúdos e progresso por componente curricular.', admin ? `<button class="btn btn-soft" onclick="showToast('Demonstração: formulário de nova disciplina')">Nova disciplina</button>` : '') +
    panel('Lista de disciplinas', '', `
      <div class="toolbar">
        <div class="toolbar-group">
          <input class="toolbar-input" placeholder="Buscar disciplina..." />
          <select class="toolbar-select"><option>Todas as turmas</option><option>3A</option><option>3B</option></select>
        </div>
      </div>
      ${table(['Disciplina', 'Turma', 'Professor', 'Carga horária', 'Status'], [
        `<tr><td><strong>Física</strong></td><td>3A</td><td>Prof. Estevão</td><td>80h</td><td>${status('Ativa', 'ok')}</td></tr>`,
        `<tr><td><strong>Matemática</strong></td><td>3A</td><td>Prof. Carla</td><td>100h</td><td>${status('Ativa', 'ok')}</td></tr>`,
        `<tr><td><strong>Química</strong></td><td>3B</td><td>Prof. Roberto</td><td>80h</td><td>${status('Ativa', 'ok')}</td></tr>`
      ])}
    `, 12);
}

function assessmentsPage(teacher) {
  return hero('AVALIAÇÕES', teacher ? 'Gestão de avaliações' : 'Minhas avaliações', teacher ? 'Crie, acompanhe respostas e consulte resultados das avaliações de suas disciplinas.' : 'Acompanhe avaliações disponíveis, realizadas e resultados liberados.', teacher ? `<button class="btn btn-soft" onclick="showToast('Demonstração: criação de avaliação')">Criar avaliação</button>` : '') +
  `<div class="grid">
    ${metric(teacher ? 'Ativas' : 'Disponíveis', teacher ? '8' : '2', teacher ? 'Período atual' : 'Para esta semana')}
    ${metric(teacher ? 'Respostas recebidas' : 'Realizadas', teacher ? '126' : '12', 'Últimos registros')}
    ${metric(teacher ? 'Aguardando revisão' : 'Média', teacher ? '17' : '8,1', teacher ? 'Questões discursivas' : 'Avaliações liberadas')}
    ${metric(teacher ? 'Banco vinculado' : 'Melhor resultado', teacher ? '42' : '9,4', teacher ? 'Questões próprias' : 'Física • Vetores')}
    ${panel('Avaliações recentes', '', table(['Avaliação', 'Disciplina', 'Turma', 'Data', 'Status', teacher ? 'Respostas' : 'Resultado'], [
      `<tr><td><strong>Cinemática I</strong></td><td>Física</td><td>3A</td><td>12/11</td><td>${status('Ativa', 'ok')}</td><td>${teacher ? '28/31' : 'Pendente'}</td></tr>`,
      `<tr><td><strong>Vetores e movimento</strong></td><td>Física</td><td>3B</td><td>03/11</td><td>${status('Encerrada', 'info')}</td><td>${teacher ? '29/29' : '9,4'}</td></tr>`,
      `<tr><td><strong>Movimento circular</strong></td><td>Física</td><td>2C</td><td>28/10</td><td>${status('Encerrada', 'info')}</td><td>${teacher ? '31/33' : '7,8'}</td></tr>`
    ]), 12)}
  </div>`;
}

function gradesPage(teacher) {
  return hero('NOTAS', teacher ? 'Notas das minhas avaliações' : 'Minhas notas', teacher ? 'Lance e altere notas somente das avaliações sob sua responsabilidade.' : 'Consulte resultados acadêmicos liberados.') +
  `<div class="grid">
    ${panel(teacher ? 'Resumo por turma' : 'Desempenho por disciplina', '', barChart(teacher ? [68, 82, 74, 88, 80] : [74, 81, 66, 90, 79]), 7)}
    ${panel('Indicadores', '', `<div class="progress-list">${progressRow(teacher ? '3A' : 'Física', 88)}${progressRow(teacher ? '3B' : 'Matemática', 81)}${progressRow(teacher ? '2C' : 'Química', 73)}</div>`, 5)}
    ${panel('Registros recentes', '', table([teacher ? 'Aluno' : 'Avaliação', 'Disciplina', 'Nota', 'Status'], [
      `<tr><td>${teacher ? 'Ana Beatriz' : 'Cinemática I'}</td><td>Física</td><td><strong>8,8</strong></td><td>${status('Lançada', 'ok')}</td></tr>`,
      `<tr><td>${teacher ? 'Lucas Moura' : 'Vetores'}</td><td>Física</td><td><strong>6,1</strong></td><td>${status('Atenção', 'warn')}</td></tr>`,
      `<tr><td>${teacher ? 'Camila Sousa' : 'Funções'}</td><td>Matemática</td><td><strong>7,2</strong></td><td>${status('Lançada', 'ok')}</td></tr>`
    ]), 12)}
  </div>`;
}

function attendanceStudentPage() {
  return hero('FREQUÊNCIA', 'Minha frequência', 'Visualize presenças, faltas e justificativas registradas.') +
  `<div class="grid">
    ${metric('Frequência geral', '92%', 'Período letivo')}
    ${metric('Presenças', '118', 'Aulas registradas')}
    ${metric('Faltas', '10', '2 justificadas')}
    ${metric('Atrasos', '3', 'Neste semestre')}
    ${panel('Frequência por disciplina', '', `<div class="progress-list">${progressRow('Física', 94)}${progressRow('Matemática', 90)}${progressRow('Química', 88)}${progressRow('Português', 96)}</div>`, 7)}
    ${panel('Resumo', '', `<div class="note-box"><strong>Resumo:</strong> sua frequência está adequada. Continue acompanhando as faltas justificadas e os atrasos registrados no período.</div>`, 5)}
  </div>`;
}

function attendanceTeacherPage() {
  return hero('FREQUÊNCIA', 'Registro e acompanhamento', 'Faça a chamada das suas disciplinas e acompanhe justificativas. O DT visualiza o panorama da própria turma.', `<button class="btn btn-soft" onclick="showToast('Demonstração: nova chamada')">Fazer chamada</button>`) +
  `<div class="grid">
    ${metric('Chamadas hoje', '4', '3 finalizadas')}
    ${metric('Pendentes', '1', '3A • Física')}
    ${metric('Justificativas', '6', '2 aguardando análise')}
    ${metric('Frequência 3A', '91%', 'Turma DT')}
    ${panel('Chamada — 3A • Física', '06 de novembro de 2026', table(['Aluno', 'Status', 'Observação'], [
      `<tr><td>${inlinePerson('Ana Beatriz', '3A', 'AB')}</td><td>${status('Presente', 'ok')}</td><td>—</td></tr>`,
      `<tr><td>${inlinePerson('Lucas Moura', '3A', 'LM')}</td><td>${status('Falta', 'bad')}</td><td>Aguardando justificativa</td></tr>`,
      `<tr><td>${inlinePerson('Camila Sousa', '3A', 'CS')}</td><td>${status('Atraso', 'warn')}</td><td>Entrada 08:17</td></tr>`
    ]), 12)}
  </div>`;
}

function recordPage() {
  return hero('HISTÓRICO', 'Histórico acadêmico', 'Consolidação das disciplinas, notas e frequência do estudante.') +
    panel('2026 • 1º semestre', '', table(['Disciplina', 'Média', 'Frequência', 'Situação'], [
      `<tr><td>Física</td><td>8,8</td><td>94%</td><td>${status('Aprovado', 'ok')}</td></tr>`,
      `<tr><td>Matemática</td><td>8,1</td><td>90%</td><td>${status('Aprovado', 'ok')}</td></tr>`,
      `<tr><td>Química</td><td>7,2</td><td>88%</td><td>${status('Aprovado', 'ok')}</td></tr>`,
      `<tr><td>Português</td><td>9,0</td><td>96%</td><td>${status('Aprovado', 'ok')}</td></tr>`
    ]), 12);
}

function studyPage() {
  return hero('PLANO DE ESTUDOS', 'Plano personalizado da semana', 'Sugestões organizadas a partir das dificuldades e do desempenho recente.') +
  `<div class="grid">
    ${metric('Progresso', '74%', '4 de 6 atividades')}
    ${metric('Tempo previsto', '3h20', 'Restante na semana')}
    ${metric('Prioridade', 'Vetores', 'Física')}
    ${metric('Sequência', '4 dias', 'Estudando em ritmo')}
    ${panel('Roteiro da semana', '', `<div class="list">${listItem('✓', 'Revisar componentes vetoriais', '25 min • concluído', status('Feito', 'ok'))}${listItem('✓', 'Resolver 8 questões de MRUV', '40 min • concluído', status('Feito', 'ok'))}${listItem('◎', 'Lista de movimento circular', '50 min', status('Hoje', 'warn'))}${listItem('□', 'Revisão final para avaliação', '35 min', status('Planejado', 'info'))}</div>`, 7)}
    ${panel('Foco sugerido', 'Com base no desempenho', `<div class="progress-list">${progressRow('Vetores', 58)}${progressRow('Movimento circular', 64)}${progressRow('MRUV', 82)}</div>`, 5)}
  </div>`;
}

function recommendationsPage() {
  return hero('RECOMENDAÇÕES', 'Materiais para você', 'Conteúdos sugeridos de acordo com os pontos que mais precisam de reforço.') +
    panel('Recomendado agora', '', `<div class="list">${listItem('▶', 'Vetores: decomposição em x e y', 'Vídeo • 12 min', status('Alta prioridade', 'warn'))}${listItem('▣', 'Capítulo 3 — Cinemática vetorial', 'Livro institucional', status('Recomendado', 'info'))}${listItem('?', '10 questões de treino', 'Banco de exercícios', status('Praticar', 'ok'))}</div>`, 12);
}

function classroomsPage() {
  return hero('TURMAS', 'Minhas turmas de atuação', 'As turmas são derivadas das disciplinas vinculadas ao professor. A função DT é exibida separadamente.') +
  `<div class="grid">
    ${panel('3A', 'Diretor de Turma', `<div class="progress-list">${progressRow('Frequência média', 91)}</div><div style="margin-top:12px">${status('DT', 'info')}</div>`, 4)}
    ${panel('3B', 'Professor de Física', `<div class="progress-list">${progressRow('Frequência média', 88)}</div>`, 4)}
    ${panel('2C', 'Professor de Física', `<div class="progress-list">${progressRow('Frequência média', 90)}</div>`, 4)}
    ${panel('Alunos da turma 3A', '', table(['Aluno', 'Média', 'Frequência', 'Status'], [
      `<tr><td>${inlinePerson('Ana Beatriz', '3A', 'AB')}</td><td>8,8</td><td>94%</td><td>${status('Bom', 'ok')}</td></tr>`,
      `<tr><td>${inlinePerson('Lucas Moura', '3A', 'LM')}</td><td>6,1</td><td>81%</td><td>${status('Atenção', 'bad')}</td></tr>`,
      `<tr><td>${inlinePerson('Camila Sousa', '3A', 'CS')}</td><td>6,8</td><td>89%</td><td>${status('Regular', 'warn')}</td></tr>`
    ]), 12)}
  </div>`;
}

function questionBankPage() {
  return hero('BANCO DE QUESTÕES', 'Meu banco de questões', 'Crie questões próprias, compartilhe quando desejar e reutilize em avaliações.', `<button class="btn btn-soft" onclick="showToast('Demonstração: editor de questão')">Nova questão</button>`) +
  `<div class="grid">
    ${metric('Questões próprias', '42', '38 ativas')}
    ${metric('Compartilhadas', '16', 'Visíveis para professores')}
    ${metric('Objetivas', '31', '74% do banco')}
    ${metric('Discursivas', '11', '26% do banco')}
    ${panel('Questões recentes', '', table(['Enunciado', 'Disciplina', 'Dificuldade', 'Visibilidade'], [
      `<tr><td>Um móvel parte do repouso...</td><td>Física</td><td>${status('Média', 'warn')}</td><td>${status('Privada', 'info')}</td></tr>`,
      `<tr><td>Determine o módulo do vetor...</td><td>Física</td><td>${status('Alta', 'bad')}</td><td>${status('Compartilhada', 'ok')}</td></tr>`,
      `<tr><td>Analise o gráfico v × t...</td><td>Física</td><td>${status('Média', 'warn')}</td><td>${status('Compartilhada', 'ok')}</td></tr>`
    ]), 12)}
  </div>`;
}

function analyticsPage() {
  return hero('ANALYTICS', 'Desempenho e dificuldades', 'Identifique alunos, conteúdos e questões que precisam de maior atenção.') +
  `<div class="grid">
    ${metric('Média geral', '78%', 'Suas avaliações')}
    ${metric('Alunos críticos', '7', 'Abaixo de 60%')}
    ${metric('Conteúdo crítico', 'Vetores', '58% médio')}
    ${metric('Questão mais difícil', 'Q12', '72% de erro')}
    ${panel('Evolução das turmas', '', barChart([54, 61, 65, 71, 75, 80]), 8)}
    ${panel('Conteúdos', '', `<div class="progress-list">${progressRow('MRU/MRUV', 84)}${progressRow('Vetores', 58)}${progressRow('Mov. circular', 66)}${progressRow('Gráficos', 76)}</div>`, 4)}
    ${panel('Alunos com menor desempenho', '', table(['Aluno', 'Turma', 'Percentual', 'Status'], [
      `<tr><td>Lucas Moura</td><td>3A</td><td>61%</td><td>${status('Atenção', 'bad')}</td></tr>`,
      `<tr><td>Camila Sousa</td><td>3A</td><td>68%</td><td>${status('Regular', 'warn')}</td></tr>`,
      `<tr><td>João Pedro</td><td>3B</td><td>72%</td><td>${status('Regular', 'warn')}</td></tr>`
    ]), 12)}
  </div>`;
}

function usersPage(role) {
  return hero('USUÁRIOS', role === 'suporte' ? 'Cadastro institucional' : 'Gestão de usuários', role === 'suporte' ? 'Suporte pode cadastrar Administração, Professor e Aluno.' : 'Administração cadastra Professor e Aluno.', `<button class="btn btn-soft" onclick="showToast('Demonstração: formulário de cadastro')">Novo usuário</button>`) +
    panel('Usuários cadastrados', '', table(['Usuário', 'Perfil', 'Vínculo', 'Status'], [
      `<tr><td>${inlinePerson('Ana Beatriz', 'ana@escola.com', 'AB')}</td><td>Aluno</td><td>3A</td><td>${status('Ativo', 'ok')}</td></tr>`,
      `<tr><td>${inlinePerson('Prof. Estevão', 'estevao@escola.com', 'ES')}</td><td>Professor</td><td>Física • DT 3A</td><td>${status('Ativo', 'ok')}</td></tr>`,
      `<tr><td>${inlinePerson('Maria Lena', 'maria@escola.com', 'ML')}</td><td>Administração</td><td>Gestão</td><td>${status('Ativo', 'ok')}</td></tr>`
    ]), 12);
}

function teachersPage() {
  return hero('PROFESSORES', 'Professores cadastrados', 'Perfis Teacher são criados automaticamente quando um usuário Professor é cadastrado.') +
  `<div class="grid">
    ${metric('Professores ativos', '18', 'Perfis sincronizados')}
    ${metric('Diretores de Turma', '3', 'Função por turma')}
    ${metric('Sem turma', '1', 'Aguardando vínculo')}
    ${metric('Carga média', '32h', 'Semanal')}
    ${panel('Quadro docente', '', table(['Professor', 'Especialidade', 'Turmas', 'DT', 'Status'], [
      `<tr><td>${inlinePerson('Prof. Estevão', 'MAT-001', 'ES')}</td><td>Física</td><td>3A, 3B, 2C</td><td>3A</td><td>${status('Ativo', 'ok')}</td></tr>`,
      `<tr><td>${inlinePerson('Prof. Carla', 'MAT-002', 'CA')}</td><td>Matemática</td><td>3A, 2A</td><td>—</td><td>${status('Ativo', 'ok')}</td></tr>`,
      `<tr><td>${inlinePerson('Prof. Roberto', 'MAT-003', 'RO')}</td><td>Química</td><td>3B, 3C</td><td>3B</td><td>${status('Ativo', 'ok')}</td></tr>`
    ]), 12)}
  </div>`;
}

function adminClassroomsPage() {
  return hero('TURMAS', 'Gestão de turmas', 'Crie turmas e acompanhe capacidade, matrículas e Diretor de Turma.', `<button class="btn btn-soft" onclick="showToast('Demonstração: nova turma')">Nova turma</button>`) +
  `<div class="grid">
    ${panel('3A', 'Manhã', `<div class="note-box"><strong>31 alunos</strong><br>${status('DT definido', 'ok')}</div>`, 3)}
    ${panel('3B', 'Tarde', `<div class="note-box"><strong>29 alunos</strong><br>${status('DT definido', 'ok')}</div>`, 3)}
    ${panel('2C', 'Tarde', `<div class="note-box"><strong>33 alunos</strong><br>${status('Sem DT', 'warn')}</div>`, 3)}
    ${panel('2A', 'Manhã', `<div class="note-box"><strong>30 alunos</strong><br>${status('Sem DT', 'warn')}</div>`, 3)}
  </div>`;
}

function enrollmentsPage() {
  return hero('MATRÍCULAS', 'Matrículas ativas', 'Vincule cada aluno a uma turma ativa e acompanhe transferências.', `<button class="btn btn-soft" onclick="showToast('Demonstração: nova matrícula')">Nova matrícula</button>`) +
    panel('Matrículas', '', table(['Aluno', 'Turma', 'Data', 'Status'], [
      `<tr><td>${inlinePerson('Ana Beatriz', 'ID 108', 'AB')}</td><td>3A</td><td>02/02/2026</td><td>${status('Ativa', 'ok')}</td></tr>`,
      `<tr><td>${inlinePerson('Lucas Moura', 'ID 109', 'LM')}</td><td>3A</td><td>02/02/2026</td><td>${status('Ativa', 'ok')}</td></tr>`,
      `<tr><td>${inlinePerson('João Pedro', 'ID 110', 'JP')}</td><td>3B</td><td>03/02/2026</td><td>${status('Ativa', 'ok')}</td></tr>`
    ]), 12);
}

function dtPage() {
  return hero('DIRETOR DE TURMA', 'Gestão de DT', 'O DT é uma função do Professor vinculada a uma turma, não um novo perfil de usuário.', `<button class="btn btn-soft" onclick="showToast('Demonstração: seleção de professor DT')">Definir DT</button>`) +
  `<div class="grid">
    ${panel('Regras aplicadas', '', `<div class="note-box"><strong>Um DT por turma.</strong> O professor precisa lecionar ao menos uma disciplina na turma. Ele recebe leitura acadêmica ampliada, mas não edita avaliações/notas de outros professores.</div>`, 5)}
    ${panel('Turmas e DT', '', table(['Turma', 'Diretor de Turma', 'Atuação', 'Status'], [
      `<tr><td>3A</td><td>Prof. Estevão</td><td>Física</td><td>${status('Definido', 'ok')}</td></tr>`,
      `<tr><td>3B</td><td>Prof. Roberto</td><td>Química</td><td>${status('Definido', 'ok')}</td></tr>`,
      `<tr><td>2C</td><td>—</td><td>—</td><td>${status('Sem DT', 'warn')}</td></tr>`
    ]), 7)}
  </div>`;
}

function reportsPage() {
  return hero('RELATÓRIOS', 'Visão institucional', 'Indicadores administrativos agregados para acompanhamento da instituição.') +
  `<div class="grid">
    ${panel('Matrículas por turma', '', barChart([82, 76, 88, 79, 71, 84]), 7)}
    ${panel('Indicadores', '', `<div class="progress-list">${progressRow('Turmas com DT', 75)}${progressRow('Professores vinculados', 94)}${progressRow('Matrículas completas', 100)}</div>`, 5)}
  </div>`;
}

function libraryPage(role) {
  return hero('BIBLIOTECA', role === 'suporte' ? 'Acervo institucional' : 'Biblioteca e materiais', role === 'suporte' ? 'Gestão técnica dos livros e capítulos do acervo oficial.' : 'Consulte livros, capítulos e materiais autorizados.', `<button class="btn btn-soft" onclick="showToast('Demonstração: ação de biblioteca')">Ação</button>`) +
  `<div class="grid">
    ${metric('Livros', '128', 'Acervo oficial')}
    ${metric('Capítulos', '1.042', 'Catalogados')}
    ${metric(role === 'suporte' ? 'Pendências técnicas' : 'Recomendados', role === 'suporte' ? '3' : '12', 'Resumo do acervo')}
    ${metric('Última atualização', 'Hoje', '16:40')}
    ${panel('Acervo em destaque', '', `<div class="list">${listItem('▣', 'Fundamentos de Física — Mecânica', 'Livro institucional • 12 capítulos', status('Disponível', 'ok'))}${listItem('▣', 'Física para o Ensino Médio', 'Livro institucional • 18 capítulos', status('Disponível', 'ok'))}${listItem('▣', 'Matemática Elementar', 'Livro institucional • 16 capítulos', status('Disponível', 'ok'))}</div>`, 12)}
  </div>`;
}

function calendarPage() {
  const days = Array.from({ length: 28 }, (_, i) => `<div class="calendar-day"><strong>${i + 1}</strong>${i === 5 ? '<span class="calendar-event">Reunião PIBID</span>' : ''}${i === 11 ? '<span class="calendar-event">Avaliação Física</span>' : ''}${i === 17 ? '<span class="calendar-event">Conselho</span>' : ''}${i === 23 ? '<span class="calendar-event">Entrega relatório</span>' : ''}</div>`).join('');
  return hero('CALENDÁRIO', 'Agenda acadêmica', 'Visão demonstrativa de avaliações, aulas, reuniões e eventos. Módulo completo previsto para etapa futura.') +
    panel('Calendário do mês', '', `<div class="note-box" style="margin-bottom:14px"><strong>Roadmap:</strong> esta tela representa a experiência planejada para o calendário acadêmico.</div><div class="calendar">${days}</div>`, 12);
}

function ticketsTable() {
  return table(['ID', 'Assunto', 'Solicitante', 'Prioridade', 'Status'], [
    `<tr><td>#1042</td><td>Erro ao anexar justificativa</td><td>Professor</td><td>${status('Alta', 'bad')}</td><td>${status('Em análise', 'warn')}</td></tr>`,
    `<tr><td>#1041</td><td>Dúvida sobre cadastro de turma</td><td>Administração</td><td>${status('Média', 'warn')}</td><td>${status('Aberto', 'info')}</td></tr>`,
    `<tr><td>#1039</td><td>Livro com capítulo duplicado</td><td>Biblioteca</td><td>${status('Baixa', 'info')}</td><td>${status('Em análise', 'warn')}</td></tr>`
  ]);
}

function ticketsPage() {
  return hero('CHAMADOS', 'Central de chamados', 'Módulo planejado para o cronograma técnico. A interface abaixo é demonstrativa.', `<button class="btn btn-soft" onclick="showToast('Demonstração: novo chamado')">Novo chamado</button>`) +
  `<div class="grid">
    ${metric('Abertos', '5', 'Fila atual')}
    ${metric('Em análise', '3', 'Responsável atribuído')}
    ${metric('Resolvidos', '42', 'Últimos 30 dias')}
    ${metric('SLA médio', '4h12', 'Tempo de resolução')}
    ${panel('Chamados', '', ticketsTable(), 12)}
  </div>`;
}

function systemPage() {
  return hero('SISTEMA', 'Saúde do sistema', 'Monitoramento operacional demonstrativo para o perfil Suporte.') +
  `<div class="grid">
    ${metric('API', 'Online', '18 ms')}
    ${metric('Banco', 'Online', '4 ms')}
    ${metric('Autenticação', 'Online', '11 ms')}
    ${metric('Disco', '34%', 'Uso atual')}
    ${panel('Latência da API', '', barChart([50, 43, 57, 39, 46, 41]), 8)}
    ${panel('Ambiente', '', `<div class="list">${listItem('⌁', 'FastAPI', 'Uvicorn', status('Online', 'ok'))}${listItem('⌁', 'SQLite', 'mentor.db', status('Online', 'ok'))}${listItem('⌁', 'CORS', 'localhost:5500', status('Online', 'ok'))}</div>`, 4)}
  </div>`;
}

function logsPage() {
  return hero('AUDITORIA', 'Logs operacionais', 'Eventos técnicos e administrativos sem exposição de conteúdo pedagógico.') +
    panel('Eventos recentes', '', table(['Horário', 'Evento', 'Origem', 'Resultado'], [
      `<tr><td>17:42</td><td>Login administrativo</td><td>Auth</td><td>${status('Sucesso', 'ok')}</td></tr>`,
      `<tr><td>17:31</td><td>Cadastro de livro</td><td>Library</td><td>${status('Sucesso', 'ok')}</td></tr>`,
      `<tr><td>16:58</td><td>Tentativa de rota pedagógica</td><td>Suporte</td><td>${status('Bloqueada 403', 'bad')}</td></tr>`
    ]), 12);
}

function profilePage() {
  const meta = currentMeta();
  return hero('PERFIL', 'Meu perfil', 'Informações pessoais e de vínculo no Mentor.Edu.') +
  `<div class="grid">
    ${panel('Informações pessoais', '', `<div class="profile-row"><div class="avatar" style="width:52px;height:52px">${meta.avatar}</div><div><div style="font-size:16px;font-weight:700">${meta.nome}</div><div style="font-size:11px;color:#64748b;margin-top:4px">${meta.tipo}</div></div></div><div class="profile-tags" style="margin-top:16px">${meta.tags.map(tag => `<span>${tag}</span>`).join('')}</div>`, 6)}
    ${panel('Segurança e acesso', '', `<div class="note-box"><strong>Controle por perfil:</strong> cada rota do backend aplica escopo de acesso compatível com Aluno, Professor/DT, Administração ou Suporte.</div>`, 6)}
  </div>`;
}

function renderSidebar() {
  const meta = currentMeta();
  $('#sidebar-profile').innerHTML = `
    <div class="profile-row">
      <div class="avatar">${meta.avatar}</div>
      <div>
        <div class="profile-name">${meta.nome}</div>
        <div class="profile-sub">${meta.tipo}</div>
      </div>
    </div>
    <div class="profile-tags">${meta.tags.map(tag => `<span>${tag}</span>`).join('')}</div>
  `;
  $('#top-avatar').textContent = meta.avatar;

  const navItems = DEMO[state.role].nav;
  $('#sidebar-nav').innerHTML = `<div class="nav-label">Navegação</div>` + navItems.map(([page, icon, label, badge]) => `
    <button class="nav-item ${page === state.currentPage ? 'active' : ''}" data-page="${page}">
      <span class="nav-icon">${icon}</span>
      <span>${label}</span>
      ${badge ? `<span class="nav-badge">${badge}</span>` : ''}
    </button>
  `).join('');

  $$('.nav-item').forEach(btn => btn.addEventListener('click', () => {
    state.currentPage = btn.dataset.page;
    renderApp();
    $('#sidebar').classList.remove('open');
  }));
}

function renderApp() {
  const nav = DEMO[state.role].nav;
  const pageMeta = nav.find(item => item[0] === state.currentPage) || ['dashboard', '⌂', 'Dashboard'];
  $('#page-title').textContent = pageMeta[2];
  $('#page-kicker').textContent = state.mode === 'live' ? 'BACKEND CONECTADO' : 'VISÃO GERAL';
  $('#connection-badge').textContent = state.mode === 'live' ? 'Backend conectado' : 'Modo demonstração';
  $('#connection-badge').className = state.mode === 'live' ? 'badge live' : 'badge muted';
  renderSidebar();

  const renderer = (PAGES[state.role][state.currentPage] || PAGES[state.role].dashboard);
  $('#page-content').innerHTML = renderer();
  $$('[data-goto]').forEach(btn => btn.addEventListener('click', () => {
    state.currentPage = btn.dataset.goto;
    renderApp();
  }));
}

function openApp(role, mode = 'demo', user = null) {
  state.role = role;
  state.mode = mode;
  state.currentUser = user;
  state.currentPage = 'dashboard';
  $('#auth-screen').classList.add('hidden');
  $('#app-shell').classList.remove('hidden');
  renderApp();
}

async function login(event) {
  event.preventDefault();
  $('#login-error').textContent = '';
  state.apiUrl = $('#api-url').value.trim().replace(/\/$/, '');
  localStorage.setItem('mentor_api', state.apiUrl);

  const formData = new URLSearchParams();
  formData.set('username', $('#login-email').value.trim());
  formData.set('password', $('#login-password').value);

  try {
    const loginResponse = await fetch(`${state.apiUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });
    const loginJson = await loginResponse.json();
    if (!loginResponse.ok) throw new Error(loginJson.detail || 'Falha no login.');

    state.token = loginJson.access_token;
    localStorage.setItem('mentor_token', state.token);

    const meResponse = await fetch(`${state.apiUrl}/users/me`, {
      headers: { Authorization: `Bearer ${state.token}` }
    });
    const meJson = await meResponse.json();
    if (!meResponse.ok) throw new Error(meJson.detail || 'Não foi possível carregar o usuário.');

    const role = normalizeRole(meJson.tipo || '');
    openApp(role, 'live', meJson);
    showToast(`Login realizado como ${meJson.tipo}.`);
  } catch (error) {
    $('#login-error').textContent = error.message;
  }
}

function logout() {
  state.token = '';
  state.currentUser = null;
  state.mode = 'demo';
  localStorage.removeItem('mentor_token');
  $('#app-shell').classList.add('hidden');
  $('#auth-screen').classList.remove('hidden');
  showToast('Sessão encerrada.');
}

function init() {
  $('#api-url').value = state.apiUrl;
  $('#login-form').addEventListener('submit', login);
  $('#open-demo-modal').addEventListener('click', () => $('#demo-modal').classList.remove('hidden'));
  $$('[data-close-demo]').forEach(el => el.addEventListener('click', () => $('#demo-modal').classList.add('hidden')));
  $$('.demo-role-btn').forEach(btn => btn.addEventListener('click', () => {
    $('#demo-modal').classList.add('hidden');
    openApp(btn.dataset.demoRole, 'demo', null);
  }));
  $('#logout-btn').addEventListener('click', logout);
  $('#open-sidebar').addEventListener('click', () => $('#sidebar').classList.add('open'));
  $('#close-sidebar').addEventListener('click', () => $('#sidebar').classList.remove('open'));
}

document.addEventListener('DOMContentLoaded', init);
