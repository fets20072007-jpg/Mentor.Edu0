const index = {
  aluno: [
    ['Disciplinas','subjects'],['Biblioteca','library'],['Avaliações','assessments'],['Histórico de avaliações','assessment-history'],['Resultados','assessment-results'],['Notas','grades'],['Frequência','attendance'],['Justificativas','attendance-justifications'],['Histórico acadêmico','record'],['Plano de estudos','study-plans'],['Sessões de estudo','study-sessions'],['Recomendações','recommendations'],['Horários','schedules'],['Notificações','notifications'],['Chamados','tickets'],['Perfil','profile']
  ],
  professor: [
    ['Turmas','classrooms'],['Direção de turma','teacher-dt'],['Disciplinas','subjects'],['Criar avaliação','assessment-create'],['Avaliações','assessments'],['Resultados','results'],['Correções','reviews'],['Liberação de acesso','assessment-access'],['Registrar frequência','attendance'],['Pendências de frequência','attendance-pending'],['Resumo de frequência','attendance-summary'],['Notas','grades'],['Banco de questões','question-bank'],['Questões compartilhadas','question-bank-shared'],['Biblioteca','library'],['Desempenho','analytics'],['Dificuldades','analytics-difficulties'],['Evolução','analytics-evolution'],['Horários','schedules'],['Chamados','tickets'],['Perfil','profile']
  ],
  administracao: [
    ['Alunos','students'],['Professores','teachers'],['Administração','admin-users'],['Suporte','support-users'],['Turmas','classrooms'],['Diretores de turma','dt'],['Disciplinas','subjects'],['Matrículas','enrollments'],['Horários','schedules'],['Avaliações','assessments'],['Livros','library-books'],['Capítulos','library-chapters'],['Conteúdos','library-content'],['Relatório de desempenho','reports'],['Relatório de frequência','reports-attendance'],['Relatório de avaliações','reports-assessments'],['Configurações','settings'],['Mensagens','notifications'],['Perfil','profile']
  ],
  suporte: [['Chamados','tickets'],['Usuários','users'],['Professores','teachers'],['Livros','library-books'],['Capítulos','library-chapters'],['Configurações','settings'],['Perfil','profile']]
};
const norm = v => String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
export function searchRoutes(role, query){
  const q=norm(query).trim(); if(!q) return [];
  return (index[role]||[]).filter(([label])=>norm(label).includes(q)).slice(0,6).map(([label,route])=>({label,route}));
}
