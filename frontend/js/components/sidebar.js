import { icon } from "./icons.js";

const navigation = {
    aluno: [
        { route: "overview", label: "Início", icon: "home" },
        { label: "Disciplinas", icon: "book", children: [
            { route: "subjects", label: "Minhas disciplinas" },
            { route: "library", label: "Conteúdos" },
        ]},
        { label: "Avaliações", icon: "clipboard", children: [
            { route: "assessments", label: "Disponíveis" },
            { route: "assessment-history", label: "Histórico" },
            { route: "assessment-results", label: "Resultados" },
        ]},
        { route: "grades", label: "Notas", icon: "chart" },
        { label: "Frequência", icon: "calendar", children: [
            { route: "attendance", label: "Resumo" },
            { route: "attendance-justifications", label: "Justificativas" },
        ]},
        { route: "record", label: "Histórico acadêmico", icon: "school" },
        { label: "Plano de estudos", icon: "activity", children: [
            { route: "study-plans", label: "Meu plano" },
            { route: "study-sessions", label: "Sessões de estudo" },
        ]},
        { label: "Biblioteca", icon: "book", children: [
            { route: "library", label: "Explorar biblioteca" },
        ]},
        { route: "recommendations", label: "Recomendações", icon: "help" },
        { route: "schedules", label: "Horários", icon: "calendar" },
        { route: "notifications", label: "Notificações", icon: "bell", badge: "notifications" },
        { route: "tickets", label: "Chamados", icon: "message" },
        { route: "profile", label: "Perfil", icon: "user" },
    ],
    professor: [
        { route: "overview", label: "Início", icon: "home" },
        { label: "Minhas turmas", icon: "users", children: [
            { route: "classrooms", label: "Turmas vinculadas" },
            { route: "teacher-dt", label: "Direção de turma" },
        ]},
        { route: "subjects", label: "Disciplinas", icon: "book" },
        { label: "Avaliações", icon: "clipboard", children: [
            { route: "assessment-create", label: "Criar avaliação" },
            { route: "assessments", label: "Minhas avaliações" },
            { route: "results", label: "Resultados" },
            { route: "reviews", label: "Correções" },
            { route: "assessment-access", label: "Liberação de acesso" },
        ]},
        { label: "Frequência", icon: "calendar", children: [
            { route: "attendance", label: "Registrar" },
            { route: "attendance-pending", label: "Pendências" },
            { route: "attendance-summary", label: "Resumos" },
        ]},
        { route: "grades", label: "Notas", icon: "chart" },
        { label: "Banco de questões", icon: "school", children: [
            { route: "question-bank", label: "Minhas questões" },
            { route: "question-bank-shared", label: "Compartilhadas" },
        ]},
        { label: "Biblioteca pedagógica", icon: "book", children: [
            { route: "library", label: "Recursos" },
        ]},
        { label: "Desempenho", icon: "chart", children: [
            { route: "analytics", label: "Turmas" },
            { route: "analytics-difficulties", label: "Dificuldades" },
            { route: "analytics-evolution", label: "Evolução" },
        ]},
        { route: "schedules", label: "Horários", icon: "calendar" },
        { route: "tickets", label: "Chamados", icon: "message" },
        { route: "profile", label: "Perfil", icon: "user" },
    ],
    administracao: [
        { route: "overview", label: "Início", icon: "home" },
        { label: "Usuários", icon: "users", children: [
            { route: "students", label: "Alunos" },
            { route: "teachers", label: "Professores" },
            { route: "admin-users", label: "Administração" },
            { route: "support-users", label: "Suporte" },
        ]},
        { label: "Turmas", icon: "users", children: [
            { route: "classrooms", label: "Listar turmas" },
            { route: "dt", label: "Diretores de turma" },
        ]},
        { route: "subjects", label: "Disciplinas", icon: "book" },
        { route: "enrollments", label: "Matrículas", icon: "file" },
        { route: "schedules", label: "Horários", icon: "calendar" },
        { label: "Avaliações", icon: "clipboard", children: [
            { route: "assessments", label: "Geral" },
            { route: "reports-assessments", label: "Resumo institucional" },
        ]},
        { label: "Biblioteca", icon: "book", children: [
            { route: "library-books", label: "Livros" },
            { route: "library-chapters", label: "Capítulos" },
            { route: "library-content", label: "Conteúdos" },
        ]},
        { label: "Relatórios", icon: "chart", children: [
            { route: "reports", label: "Desempenho" },
            { route: "reports-attendance", label: "Frequência" },
            { route: "reports-assessments", label: "Avaliações" },
        ]},
        { route: "settings", label: "Configurações", icon: "settings" },
        { route: "notifications", label: "Mensagens", icon: "message", badge: "notifications" },
        { route: "profile", label: "Perfil", icon: "user" },
    ],
    suporte: [
        { route: "overview", label: "Início", icon: "home" },
        { label: "Atendimento", icon: "message", children: [
            { route: "tickets", label: "Chamados" },
            { route: "users", label: "Usuários" },
            { route: "teachers", label: "Professores" },
        ]},
        { label: "Estrutura da biblioteca", icon: "book", children: [
            { route: "library-books", label: "Livros" },
            { route: "library-chapters", label: "Capítulos" },
        ]},
        { route: "settings", label: "Configurações", icon: "settings" },
        { route: "profile", label: "Perfil", icon: "user" },
    ],
};

function itemMarkup(item, unread) {
    const badge = item.badge === "notifications" && unread > 0 ? `<span class="nav-badge">${Math.min(unread, 99)}</span>` : "";
    if (item.children) {
        return `<div class="nav-group" data-nav-group><button class="nav-group-toggle" type="button" aria-expanded="false">${icon(item.icon)}<span>${item.label}</span>${icon("chevron", "icon chevron")}</button><div class="nav-children">${item.children.map(child => `<button class="nav-item" type="button" data-route="${child.route}"><span>${child.label}</span>${child.badge === "notifications" && unread > 0 ? `<span class="nav-badge">${Math.min(unread, 99)}</span>` : ""}</button>`).join("")}</div></div>`;
    }
    return `<button class="nav-item" type="button" data-route="${item.route}">${icon(item.icon)}<span>${item.label}</span>${badge}</button>`;
}

export function renderSidebar({ role, unread = 0, onNavigate, onLogout }) {
    const root = document.getElementById("sidebar");
    const items = navigation[role] || [];
    root.innerHTML = `<div class="sidebar-head"><div class="brand-lockup brand-lockup--light"><img class="brand-symbol" src="assets/brand/logo-symbol.png" alt=""><span class="brand-name">Mentor<span>.Edu</span></span></div></div><nav class="sidebar-nav">${items.map(item => itemMarkup(item, unread)).join("")}</nav><div class="sidebar-footer"><button id="sidebarLogout" type="button" class="nav-item">${icon("logout")}<span>Sair</span></button></div>`;

    root.querySelectorAll("[data-nav-group]").forEach(group => {
        const button = group.querySelector(".nav-group-toggle");
        button.addEventListener("click", () => {
            const open = group.classList.toggle("is-open");
            button.setAttribute("aria-expanded", String(open));
        });
    });
    root.querySelectorAll("[data-route]").forEach(button => button.addEventListener("click", () => onNavigate(button.dataset.route)));
    root.querySelector("#sidebarLogout")?.addEventListener("click", onLogout);
}

export function setActiveSidebarRoute(route) {
    document.querySelectorAll(".nav-item[data-route]").forEach(item => {
        const active = item.dataset.route === route;
        item.classList.toggle("is-active", active);
        if (active) {
            const group = item.closest("[data-nav-group]");
            group?.classList.add("is-open");
            group?.querySelector(".nav-group-toggle")?.setAttribute("aria-expanded", "true");
        }
    });
}
