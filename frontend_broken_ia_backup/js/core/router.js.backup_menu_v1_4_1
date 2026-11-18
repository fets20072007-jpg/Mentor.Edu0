import { setActiveSidebarRoute } from "../components/sidebar.js";
import { setTopbarTitle } from "../components/topbar.js";
import { setState } from "../state.js";

const titles = {
    overview: "Dashboard",
    subjects: "Disciplinas",
    assessments: "Avaliações",
    "assessment-history": "Histórico de avaliações",
    "assessment-results": "Resultados das avaliações",
    "assessment-access": "Liberação de acesso",
    grades: "Notas",
    attendance: "Frequência",
    "attendance-justifications": "Justificativas",
    "attendance-pending": "Pendências de frequência",
    "attendance-summary": "Resumo de frequência",
    record: "Histórico acadêmico",
    "study-plans": "Plano de estudos",
    "study-sessions": "Sessões de estudo",
    schedules: "Horários",
    library: "Biblioteca",
    recommendations: "Recomendações",
    activities: "Atividades",
    notifications: "Notificações",
    tickets: "Chamados",
    profile: "Meu perfil",
    classrooms: "Turmas",
    "teacher-dt": "Direção de turma",
    "assessment-create": "Criar avaliação",
    reviews: "Correções",
    results: "Resultados",
    "question-bank": "Banco de questões",
    "question-bank-shared": "Questões compartilhadas",
    analytics: "Desempenho",
    "analytics-difficulties": "Dificuldades",
    "analytics-evolution": "Evolução",
    users: "Usuários",
    students: "Alunos",
    teachers: "Professores",
    "admin-users": "Administração",
    "support-users": "Suporte",
    enrollments: "Matrículas",
    dt: "Diretores de Turma",
    reports: "Relatórios de desempenho",
    "reports-attendance": "Relatório de frequência",
    "reports-classrooms": "Relatório de turmas",
    "reports-assessments": "Relatório de avaliações",
    "library-books": "Livros",
    "library-chapters": "Capítulos",
    "library-content": "Conteúdos",
    settings: "Configurações",
    pending: "Pendências",
    "quick-actions": "Ações rápidas",
};

export function routeTitle(route) { return titles[route] || "Mentor.Edu"; }

export function currentRoute() {
    return location.hash.replace(/^#\/?/, "") || "overview";
}

export function navigate(route) {
    const hash = `#/${route}`;
    if (location.hash === hash) window.dispatchEvent(new HashChangeEvent("hashchange"));
    else location.hash = hash;
}

export function syncRouteUi(route) {
    setState({ currentPage: route });
    setActiveSidebarRoute(route);
    setTopbarTitle(routeTitle(route));
    document.body.classList.remove("sidebar-open");
    const backdrop = document.getElementById("sidebarBackdrop");
    if (backdrop) backdrop.hidden = true;
}
