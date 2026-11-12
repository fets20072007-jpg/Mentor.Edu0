import { FEATURES } from "./config.js";
import { login, requestPasswordReset } from "./api/auth.js";
import { getMe } from "./api/users.js";
import { getUnreadCount } from "./api/notifications.js";
import { clearSession, hasSession, setCachedUser, setSession } from "./core/session.js";
import { normalizeRole, ROLES } from "./core/permissions.js";
import { currentRoute, navigate, routeTitle, syncRouteUi } from "./core/router.js";
import { setState } from "./state.js";
import { renderSidebar } from "./components/sidebar.js";
import { renderTopbar } from "./components/topbar.js";
import { loadingMarkup } from "./components/loading.js";
import { renderPlaceholder } from "./pages/shared/placeholder.js";
import { renderStudentDashboard } from "./pages/student/dashboard.js?v=19.3";
import { renderTeacherDashboard } from "./pages/teacher/dashboard.js?v=19.3";
import { renderAdminDashboard } from "./pages/admin/dashboard.js?v=19.3";
import { renderSupportDashboard } from "./pages/support/dashboard.js?v=19.3";
import { renderSupportTickets } from "./pages/support/tickets.js";
import { renderSupportUsers, renderSupportTeachers } from "./pages/support/users.js";
import { renderSupportBooks, renderSupportChapters } from "./pages/support/library.js";
import { renderSupportSettings } from "./pages/support/settings.js";
import { renderAdminStudents, renderAdminTeachers, renderAdminUsers, renderSupportUsers as renderAdminSupportUsers } from "./pages/admin/users.js?v=19.5";
import { renderAdminClassrooms, renderAdminDt } from "./pages/admin/classrooms.js";
import { renderAdminSubjects } from "./pages/admin/subjects.js";
import { renderAdminEnrollments } from "./pages/admin/enrollments.js";
import { renderAdminSchedules } from "./pages/admin/schedules.js";
import { renderAdminAssessments, renderAdminReports } from "./pages/admin/assessments.js";

import { renderTeacherClassrooms } from "./pages/teacher/classrooms.js";
import { renderTeacherDt } from "./pages/teacher/dt.js";
import { renderTeacherSubjects } from "./pages/teacher/subjects.js";
import { renderTeacherAssessments } from "./pages/teacher/assessments.js";
import { renderTeacherAssessmentCreate } from "./pages/teacher/assessment-create.js";
import { renderTeacherResults } from "./pages/teacher/results.js";
import { renderTeacherAssessmentAccess } from "./pages/teacher/assessment-access.js";
import { renderTeacherReviews } from "./pages/teacher/reviews.js";
import { renderTeacherAttendance } from "./pages/teacher/attendance.js";
import { renderTeacherAttendancePending } from "./pages/teacher/attendance-pending.js";
import { renderTeacherAttendanceSummary } from "./pages/teacher/attendance-summary.js";
import { renderTeacherGrades } from "./pages/teacher/grades.js";
import { renderTeacherQuestionBank } from "./pages/teacher/question-bank.js";
import { renderTeacherQuestionBankShared } from "./pages/teacher/question-bank-shared.js";
import { renderTeacherLibrary } from "./pages/teacher/library.js";
import { renderTeacherAnalytics } from "./pages/teacher/analytics.js";
import { renderTeacherAnalyticsDifficulties } from "./pages/teacher/analytics-difficulties.js";
import { renderTeacherAnalyticsEvolution } from "./pages/teacher/analytics-evolution.js";
import { renderTeacherSchedules } from "./pages/teacher/schedules.js";

import { renderStudentSubjects } from "./pages/student/subjects.js";
import { renderStudentAssessments } from "./pages/student/assessments.js";
import { renderStudentAssessmentHistory } from "./pages/student/assessment-history.js";
import { renderStudentAssessmentResults } from "./pages/student/assessment-results.js";
import { renderStudentGrades } from "./pages/student/grades.js";
import { renderStudentAttendance } from "./pages/student/attendance.js";
import { renderStudentAttendanceJustifications } from "./pages/student/attendance-justifications.js";
import { renderStudentRecord } from "./pages/student/record.js";
import { renderStudentStudyPlans } from "./pages/student/study-plans.js";
import { renderStudentStudySessions } from "./pages/student/study-sessions.js";
import { renderStudentLibrary } from "./pages/student/library.js";
import { renderStudentSchedules } from "./pages/student/schedules.js";
import { renderStudentRecommendations } from "./pages/student/recommendations.js";
import { renderNotifications } from "./pages/shared/notifications.js";
import { renderMyTickets } from "./pages/shared/tickets.js";
import { renderProfile } from "./pages/shared/profile.js";
import { errorBlock } from "./pages/shared/page-ui.js";
import { applyUiPreferences } from "./core/ui-preferences.js";
import { renderAdminLibraryBooks, renderAdminLibraryChapters, renderAdminLibraryContent } from "./pages/admin/library.js";
import { renderAdminSettings } from "./pages/admin/settings.js";
import { renderAdminPerformanceReport, renderAdminAttendanceReport, renderAdminAssessmentReport } from "./pages/admin/reports.js";

const page = document.body.dataset.page;

function showLoginMessage(message, type = "error") {
    const target = document.getElementById("loginMessage");
    if (!target) return;
    target.textContent = message;
    target.className = `form-message is-visible ${type === "success" ? "is-success" : "is-error"}`;
}

async function bootLogin() {
    if (hasSession()) {
        try {
            await getMe();
            location.replace("dashboard.html");
            return;
        } catch { clearSession(); }
    }

    const social = document.getElementById("socialLoginArea");
    if (social) {
        social.hidden = false;
        social.querySelectorAll("[data-provider]").forEach(button => {
            button.disabled = false;
            button.addEventListener("click", () => {
                const provider = button.dataset.provider === "google" ? "Google" : "Microsoft";
                if (!FEATURES.socialLogin) return showLoginMessage(`Login com ${provider}: estrutura pronta, aguardando as credenciais OAuth institucionais para ativaÃ§Ã£o.`, "success");
                location.href = `${location.origin}/auth/oauth/${button.dataset.provider}`;
            });
        });
    }

    const password = document.getElementById("password");
    const toggle = document.getElementById("togglePassword");
    toggle?.addEventListener("click", () => {
        const visible = password.type === "text";
        password.type = visible ? "password" : "text";
        toggle.setAttribute("aria-label", visible ? "Mostrar senha" : "Ocultar senha");
    });

    document.getElementById("forgotPassword")?.addEventListener("click", () => {
        const currentEmail = document.getElementById("email")?.value?.trim() || "";
        const wrapper = document.createElement("div");
        wrapper.className = "modal-backdrop";
        wrapper.innerHTML = `<section class="modal-card" role="dialog" aria-modal="true" aria-labelledby="forgotTitle"><button class="modal-close" type="button" aria-label="Fechar">Ã—</button><h3 id="forgotTitle">Recuperar acesso</h3><p>Informe seu e-mail institucional. O Mentor.Edu abrirÃ¡ um chamado de acesso para o suporte.</p><form data-forgot-form><label>E-mail<input type="email" name="email" required value="${currentEmail.replace(/&/g,'&amp;').replace(/"/g,'&quot;')}"></label><div class="form-actions"><button type="button" class="mini-button" data-close>Cancelar</button><button class="mini-button mini-button--primary" type="submit">Enviar ao suporte</button></div><p class="form-message" data-forgot-message></p></form></section>`;
        document.body.appendChild(wrapper);
        const close=()=>wrapper.remove(); wrapper.querySelector('.modal-close').onclick=close; wrapper.querySelector('[data-close]').onclick=close;
        wrapper.querySelector('[data-forgot-form]').addEventListener('submit', async event => { event.preventDefault(); const btn=event.currentTarget.querySelector('button[type="submit"]'); btn.disabled=true; try { const data=await requestPasswordReset(event.currentTarget.email.value); const msg=wrapper.querySelector('[data-forgot-message]'); msg.textContent=data.message; msg.className='form-message is-visible is-success'; } catch(error){ const msg=wrapper.querySelector('[data-forgot-message]'); msg.textContent=error.message; msg.className='form-message is-visible is-error'; btn.disabled=false; } });
    });

    document.getElementById("loginForm")?.addEventListener("submit", async event => {
        event.preventDefault();
        const email = document.getElementById("email").value.trim();
        const pass = password.value;
        const button = document.getElementById("loginButton");
        if (!email || !pass) return showLoginMessage("Preencha o e-mail e a senha.");
        button.disabled = true;
        button.textContent = "Entrando...";
        try {
            const auth = await login(email, pass);
            const persistent = Boolean(document.getElementById("rememberMe")?.checked);
            setSession(auth.access_token, null, { persistent });
            const user = await getMe();
            setSession(auth.access_token, user, { persistent });
            showLoginMessage(`Bem-vindo, ${user.nome}!`, "success");
            location.replace("dashboard.html");
        } catch (error) {
            clearSession();
            showLoginMessage(error.message || "NÃ£o foi possÃ­vel entrar.");
        } finally {
            button.disabled = false;
            button.textContent = "Entrar";
        }
    });
}

function logout() {
    clearSession();
    location.replace("index.html");
}

function toggleSidebar() {
    const backdrop = document.getElementById("sidebarBackdrop");
    if (window.matchMedia("(max-width: 980px)").matches) {
        const open = document.body.classList.toggle("sidebar-open");
        if (backdrop) backdrop.hidden = !open;
        return;
    }
    document.body.classList.toggle("sidebar-collapsed");
    if (backdrop) backdrop.hidden = true;
}

async function renderRoute(route, role, user) {
    const container = document.getElementById("pageContent");
    syncRouteUi(route);
    container.innerHTML = loadingMarkup("Carregando...");

    try {
        if (route === "overview") {
            if (role === ROLES.STUDENT) return await renderStudentDashboard(container, user, navigate);
            if (role === ROLES.TEACHER) return await renderTeacherDashboard(container, user, navigate);
            if (role === ROLES.ADMIN) return await renderAdminDashboard(container, user, navigate);
            if (role === ROLES.SUPPORT) return await renderSupportDashboard(container, user, navigate);
        }

        if (route === "notifications") return await renderNotifications(container);
        if (route === "profile") return await renderProfile(container);
        if (route === "tickets" && role !== ROLES.SUPPORT) return await renderMyTickets(container);

        if (role === ROLES.TEACHER) {
            const teacherRoutes = {
                classrooms: renderTeacherClassrooms,
                "teacher-dt": renderTeacherDt,
                subjects: renderTeacherSubjects,
                assessments: renderTeacherAssessments,
                "assessment-create": renderTeacherAssessmentCreate,
                results: renderTeacherResults,
                "assessment-access": renderTeacherAssessmentAccess,
                reviews: renderTeacherReviews,
                attendance: renderTeacherAttendance,
                "attendance-pending": renderTeacherAttendancePending,
                "attendance-summary": renderTeacherAttendanceSummary,
                grades: renderTeacherGrades,
                "question-bank": renderTeacherQuestionBank,
                "question-bank-shared": renderTeacherQuestionBankShared,
                library: renderTeacherLibrary,
                analytics: renderTeacherAnalytics,
                "analytics-difficulties": renderTeacherAnalyticsDifficulties,
                "analytics-evolution": renderTeacherAnalyticsEvolution,
                schedules: renderTeacherSchedules,
            };
            const renderer = teacherRoutes[route];
            if (renderer) return await renderer(container, navigate);
        }

        if (role === ROLES.ADMIN) {
            const adminRoutes = {
                students: renderAdminStudents,
                teachers: renderAdminTeachers,
                "admin-users": renderAdminUsers,
                "support-users": renderAdminSupportUsers,
                classrooms: renderAdminClassrooms,
                dt: renderAdminDt,
                subjects: renderAdminSubjects,
                enrollments: renderAdminEnrollments,
                schedules: renderAdminSchedules,
                assessments: renderAdminAssessments,
                reports: renderAdminPerformanceReport,
                "reports-attendance": renderAdminAttendanceReport,
                "reports-assessments": renderAdminAssessmentReport,
                "library-books": renderAdminLibraryBooks,
                "library-chapters": renderAdminLibraryChapters,
                "library-content": renderAdminLibraryContent,
                settings: renderAdminSettings,
            };
            const renderer = adminRoutes[route];
            if (renderer) return await renderer(container, navigate);
        }

        if (role === ROLES.SUPPORT) {
            const supportRoutes = {
                tickets: renderSupportTickets,
                users: renderSupportUsers,
                teachers: renderSupportTeachers,
                "library-books": renderSupportBooks,
                "library-chapters": renderSupportChapters,
                settings: renderSupportSettings,
            };
            const renderer = supportRoutes[route];
            if (renderer) return await renderer(container, navigate);
        }

        if (role === ROLES.STUDENT) {
            const studentRoutes = {
                subjects: renderStudentSubjects,
                assessments: renderStudentAssessments,
                "assessment-history": renderStudentAssessmentHistory,
                "assessment-results": renderStudentAssessmentResults,
                grades: renderStudentGrades,
                attendance: renderStudentAttendance,
                "attendance-justifications": renderStudentAttendanceJustifications,
                record: renderStudentRecord,
                "study-plans": renderStudentStudyPlans,
                "study-sessions": renderStudentStudySessions,
                library: renderStudentLibrary,
                schedules: renderStudentSchedules,
                recommendations: renderStudentRecommendations,
            };
            const renderer = studentRoutes[route];
            if (renderer) return await renderer(container, navigate);
        }

        renderPlaceholder(container, routeTitle(route), "Esta pÃ¡gina serÃ¡ integrada na etapa correspondente ao seu perfil.");
    } catch (error) {
        console.error(error);
        container.innerHTML = errorBlock(error.message || "Ocorreu um erro ao carregar a pÃ¡gina.");
    }
}

async function bootDashboard() {
    if (!hasSession()) return location.replace("index.html");

    try {
        const user = await getMe();
        const role = normalizeRole(user.tipo);
        if (![ROLES.STUDENT, ROLES.TEACHER, ROLES.ADMIN, ROLES.SUPPORT].includes(role)) throw new Error("Perfil nÃ£o reconhecido pelo Mentor.Edu.");
        setCachedUser(user);
        document.body.dataset.role = role;

        let unread = 0;
        try { unread = Number((await getUnreadCount())?.nao_lidas || 0); } catch { unread = 0; }
        setState({ user, role, unreadNotifications: unread });

        renderSidebar({ user, role, unread, onNavigate: navigate, onLogout: logout });
        renderTopbar({ user, role, title: routeTitle(currentRoute()), unread, onMenu: toggleSidebar, onNotifications: () => navigate("notifications"), onSearchNavigate: navigate });

        document.getElementById("sidebarBackdrop")?.addEventListener("click", toggleSidebar);
        window.addEventListener("hashchange", () => renderRoute(currentRoute(), role, user));

        if (!location.hash) navigate("overview");
        else await renderRoute(currentRoute(), role, user);
    } catch (error) {
        console.error(error);
        clearSession();
        location.replace("index.html");
    }
}

applyUiPreferences();

if (page === "login") bootLogin();
if (page === "dashboard") bootDashboard();


