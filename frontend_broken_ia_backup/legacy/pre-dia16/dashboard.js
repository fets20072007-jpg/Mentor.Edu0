const API_URL =
    "http://127.0.0.1:8000";


const token =
    localStorage.getItem(
        "access_token"
    );


let currentUser = null;


/* =====================================================
   SEGURANÇA
===================================================== */

if (!token) {

    window.location.href =
        "index.html";
}


/* =====================================================
   ELEMENTOS
===================================================== */

const sidebarMenu =
    document.getElementById(
        "sidebarMenu"
    );

const pageContent =
    document.getElementById(
        "pageContent"
    );

const pageTitle =
    document.getElementById(
        "pageTitle"
    );

const sidebarName =
    document.getElementById(
        "sidebarName"
    );

const sidebarRole =
    document.getElementById(
        "sidebarRole"
    );

const sidebarAvatar =
    document.getElementById(
        "sidebarAvatar"
    );

const topbarName =
    document.getElementById(
        "topbarName"
    );

const topbarRole =
    document.getElementById(
        "topbarRole"
    );

const topbarAvatar =
    document.getElementById(
        "topbarAvatar"
    );

const logoutButton =
    document.getElementById(
        "logoutButton"
    );


/* =====================================================
   MENUS POR PERFIL
===================================================== */

const menus = {

    aluno: [

        {
            id: "overview",
            icon: "⌂",
            label: "Visão geral"
        },

        {
            id: "subjects",
            icon: "▣",
            label: "Disciplinas"
        },

        {
            id: "assessments",
            icon: "✓",
            label: "Avaliações"
        },

        {
            id: "attendance",
            icon: "◷",
            label: "Frequência"
        },

        {
            id: "performance",
            icon: "↗",
            label: "Desempenho"
        },

        {
            id: "profile",
            icon: "○",
            label: "Meu perfil"
        }

    ],


    professor: [

        {
            id: "overview",
            icon: "⌂",
            label: "Visão geral"
        },

        {
            id: "classrooms",
            icon: "▦",
            label: "Minhas turmas"
        },

        {
            id: "attendance",
            icon: "✓",
            label: "Frequência"
        },

        {
            id: "assessments",
            icon: "□",
            label: "Avaliações"
        },

        {
            id: "questions",
            icon: "?",
            label: "Banco de questões"
        },

        {
            id: "reports",
            icon: "↗",
            label: "Relatórios"
        },

        {
            id: "profile",
            icon: "○",
            label: "Meu perfil"
        }

    ],


    administracao: [

        {
            id: "overview",
            icon: "⌂",
            label: "Visão geral"
        },

        {
            id: "users",
            icon: "♙",
            label: "Usuários"
        },

        {
            id: "teachers",
            icon: "♙",
            label: "Professores"
        },

        {
            id: "classrooms",
            icon: "▦",
            label: "Turmas"
        },

        {
            id: "enrollments",
            icon: "✓",
            label: "Matrículas"
        },

        {
            id: "attendance",
            icon: "◷",
            label: "Frequência"
        },

        {
            id: "reports",
            icon: "↗",
            label: "Relatórios"
        },

        {
            id: "profile",
            icon: "○",
            label: "Perfil"
        }

    ],


    suporte: [

        {
            id: "overview",
            icon: "⌂",
            label: "Visão geral"
        },

        {
            id: "users",
            icon: "♙",
            label: "Usuários"
        },

        {
            id: "classrooms",
            icon: "▦",
            label: "Estrutura"
        },

        {
            id: "support",
            icon: "⚙",
            label: "Suporte"
        },

        {
            id: "profile",
            icon: "○",
            label: "Perfil"
        }

    ]

};


/* =====================================================
   NORMALIZA PERFIL
===================================================== */

function normalizeRole(role) {

    const normalized =
        (role || "")
        .trim()
        .toLowerCase();


    if (
        normalized ===
        "administração"
    ) {
        return "administracao";
    }


    return normalized;
}


/* =====================================================
   INICIAIS
===================================================== */

function getInitials(name) {

    if (!name) {
        return "U";
    }

    const parts =
        name
        .trim()
        .split(" ");


    if (parts.length === 1) {

        return parts[0][0]
            .toUpperCase();
    }


    return (
        parts[0][0] +
        parts[
            parts.length - 1
        ][0]
    ).toUpperCase();
}


/* =====================================================
   API
===================================================== */

async function apiRequest(
    endpoint
) {

    const response =
        await fetch(
            `${API_URL}${endpoint}`,
            {
                headers: {

                    Authorization:
                        `Bearer ${token}`
                }
            }
        );


    if (response.status === 401) {

        logout();

        return null;
    }


    if (!response.ok) {

        throw new Error(
            `Erro ${response.status}`
        );
    }


    return response.json();
}


/* =====================================================
   CARREGA USUÁRIO
===================================================== */

async function loadUser() {

    try {

        currentUser =
            await apiRequest(
                "/users/me"
            );


        renderUser();

        renderMenu();

        renderPage(
            "overview"
        );

    }

    catch (error) {

        console.error(error);

        logout();
    }
}


/* =====================================================
   USUÁRIO NO LAYOUT
===================================================== */

function renderUser() {

    const role =
        normalizeRole(
            currentUser.tipo
        );


    const roleNames = {

        aluno: "Aluno",

        professor:
            "Professor",

        administracao:
            "Administração",

        suporte:
            "Suporte"
    };


    const name =
        currentUser.nome ||
        "Usuário";


    const initials =
        getInitials(name);


    sidebarName.textContent =
        name;

    topbarName.textContent =
        name;


    sidebarRole.textContent =
        roleNames[role] ||
        currentUser.tipo;

    topbarRole.textContent =
        roleNames[role] ||
        currentUser.tipo;


    sidebarAvatar.textContent =
        initials;

    topbarAvatar.textContent =
        initials;
}


/* =====================================================
   MENU
===================================================== */

function renderMenu() {

    const role =
        normalizeRole(
            currentUser.tipo
        );


    const userMenu =
        menus[role] ||
        menus.aluno;


    sidebarMenu.innerHTML =
        "";


    userMenu.forEach(
        item => {

            const button =
                document.createElement(
                    "button"
                );


            button.className =
                "menu-item";


            button.dataset.page =
                item.id;


            button.innerHTML = `

                <span class="menu-icon">
                    ${item.icon}
                </span>

                <span>
                    ${item.label}
                </span>

            `;


            button.addEventListener(
                "click",
                () => {

                    renderPage(
                        item.id
                    );

                }
            );


            sidebarMenu.appendChild(
                button
            );
        }
    );
}


/* =====================================================
   ATIVA ITEM
===================================================== */

function activateMenu(page) {

    document
        .querySelectorAll(
            ".menu-item"
        )
        .forEach(
            item => {

                item.classList
                    .toggle(
                        "active",
                        item.dataset.page
                        === page
                    );
            }
        );
}


/* =====================================================
   TROCA PÁGINA
===================================================== */

async function renderPage(page) {

    activateMenu(page);


    const titles = {

        overview:
            "Visão geral",

        subjects:
            "Disciplinas",

        classrooms:
            "Turmas",

        attendance:
            "Frequência",

        assessments:
            "Avaliações",

        performance:
            "Desempenho",

        questions:
            "Banco de questões",

        reports:
            "Relatórios",

        users:
            "Usuários",

        teachers:
            "Professores",

        enrollments:
            "Matrículas",

        support:
            "Suporte",

        profile:
            "Meu perfil"
    };


    pageTitle.textContent =
        titles[page] ||
        "Mentor.Edu";


    


    if (page === "overview") {
    await renderOverview();
    return;
}

const role = normalizeRole(
    currentUser.tipo
);

if (
    page === "attendance" &&
    role === "aluno"
) {
    await renderStudentAttendancePage();
    return;
}




    renderFeaturePage(
        page
    );
}


/* =====================================================
   VISÃO GERAL
===================================================== */

async function renderOverview() {

    const role =
        normalizeRole(
            currentUser.tipo
        );


    if (role === "aluno") {

        await renderStudentDashboard();

        return;
    }


    if (role === "professor") {

        await renderTeacherDashboard();

        return;
    }


    if (
        role ===
        "administracao"
    ) {

        await renderAdminDashboard();

        return;
    }


    if (role === "suporte") {

        await renderSupportDashboard();

        return;
    }
}


/* =====================================================
   DASHBOARD ALUNO
===================================================== */

async function renderStudentDashboard() {

    let attendance = null;

    let subjects = [];


    try {

        attendance =
            await apiRequest(
                "/attendance/me/summary"
            );

    }

    catch (error) {

        console.log(
            "Frequência ainda indisponível."
        );
    }


    try {

        subjects =
            await apiRequest(
                "/subjects/me"
            );

    }

    catch (error) {

        subjects = [];
    }


    const percentual =
        attendance
            ?.percentual_presenca
        ?? 0;


    pageContent.innerHTML = `

        <section class="dashboard-welcome">

            <h2>
                Olá, ${currentUser.nome} 👋
            </h2>

            <p>
                Veja um resumo da sua vida acadêmica.
            </p>

        </section>


        <section class="stats-grid">

            ${statCard(
                "Disciplinas",
                subjects.length,
                "▣",
                "Matérias da sua turma"
            )}

            ${statCard(
                "Frequência",
                `${percentual}%`,
                "◷",
                "Presença registrada"
            )}

            ${statCard(
                "Presenças",
                attendance?.presencas ?? 0,
                "✓",
                "Aulas registradas"
            )}

            ${statCard(
                "Pendências",
                attendance?.faltas_pendentes ?? 0,
                "!",
                "Faltas aguardando justificativa"
            )}

        </section>


        <section class="dashboard-grid">

            <div>

                <div class="panel">

                    <div class="panel-header">

                        <h3>
                            Minha jornada
                        </h3>

                        <span>
                            Área acadêmica
                        </span>

                    </div>


                    <div class="quick-actions">

                        ${quickAction(
                            "Disciplinas",
                            "Conteúdos e atividades",
                            "subjects"
                        )}

                        ${quickAction(
                            "Avaliações",
                            "Provas e resultados",
                            "assessments"
                        )}

                        ${quickAction(
                            "Frequência",
                            "Presenças e faltas",
                            "attendance"
                        )}

                        ${quickAction(
                            "Desempenho",
                            "Veja sua evolução",
                            "performance"
                        )}

                    </div>

                </div>


                <div class="panel">

                    <div class="panel-header">

                        <h3>
                            Atividades recentes
                        </h3>

                        <span>
                            Protótipo
                        </span>

                    </div>


                    <div class="activity-list">

                        ${activity(
                            "Avaliações",
                            "Consulte provas liberadas pelo professor",
                            "info",
                            "Ver"
                        )}

                        ${activity(
                            "Frequência",
                            "Acompanhe faltas e justificativas",
                            "success",
                            `${percentual}%`
                        )}

                        ${activity(
                            "Desempenho",
                            "Relatórios personalizados de aprendizagem",
                            "warning",
                            "Analisar"
                        )}

                    </div>

                </div>

            </div>


            <div>

                <div class="panel">

                    <div class="panel-header">

                        <h3>
                            Minha frequência
                        </h3>

                    </div>


                    <div class="activity-list">

                        ${activity(
                            "Presenças",
                            "Registros confirmados",
                            "success",
                            attendance?.presencas ?? 0
                        )}

                        ${activity(
                            "Justificadas",
                            "Faltas justificadas",
                            "info",
                            attendance?.faltas_justificadas ?? 0
                        )}

                        ${activity(
                            "Não justificadas",
                            "Faltas sem justificativa",
                            "danger",
                            attendance?.faltas_nao_justificadas ?? 0
                        )}

                        ${activity(
                            "Pendentes",
                            "Aguardando justificativa",
                            "warning",
                            attendance?.faltas_pendentes ?? 0
                        )}

                    </div>

                </div>

            </div>

        </section>

    `;


    bindQuickActions();
}


/* =====================================================
   DASHBOARD PROFESSOR
===================================================== */

async function renderTeacherDashboard() {

    let classrooms = [];

    let pending = [];


    try {

        classrooms =
            await apiRequest(
                "/teachers/me/classrooms"
            );

    }

    catch (error) {

        classrooms = [];
    }


    try {

        pending =
            await apiRequest(
                "/attendance/teacher/pending"
            );

    }

    catch (error) {

        pending = [];
    }


    pageContent.innerHTML = `

        <section class="dashboard-welcome">

            <h2>
                Olá, Prof. ${currentUser.nome} 👋
            </h2>

            <p>
                Gerencie suas turmas e acompanhe seus alunos.
            </p>

        </section>


        <section class="stats-grid">

            ${statCard(
                "Minhas turmas",
                classrooms.length,
                "▦",
                "Turmas vinculadas"
            )}

            ${statCard(
                "Pendências",
                pending.length,
                "!",
                "Faltas aguardando análise"
            )}

            ${statCard(
                "Avaliações",
                "—",
                "□",
                "Criadas por você"
            )}

            ${statCard(
                "Relatórios",
                "—",
                "↗",
                "Desempenho dos alunos"
            )}

        </section>


        <section class="dashboard-grid">

            <div>

                <div class="panel">

                    <div class="panel-header">

                        <h3>
                            Acesso rápido
                        </h3>

                    </div>


                    <div class="quick-actions">

                        ${quickAction(
                            "Minhas turmas",
                            "Alunos e disciplinas",
                            "classrooms"
                        )}

                        ${quickAction(
                            "Fazer chamada",
                            "Registrar frequência",
                            "attendance"
                        )}

                        ${quickAction(
                            "Nova avaliação",
                            "Criar prova ou atividade",
                            "assessments"
                        )}

                        ${quickAction(
                            "Relatórios",
                            "Analisar desempenho",
                            "reports"
                        )}

                    </div>

                </div>


                <div class="panel">

                    <div class="panel-header">

                        <h3>
                            Gestão pedagógica
                        </h3>

                    </div>


                    <div class="activity-list">

                        ${activity(
                            "Avaliações",
                            "Crie e gerencie atividades e provas",
                            "info",
                            "Abrir"
                        )}

                        ${activity(
                            "Banco de questões",
                            "Organize questões por conteúdo",
                            "success",
                            "Abrir"
                        )}

                        ${activity(
                            "Desempenho",
                            "Identifique dificuldades dos alunos",
                            "warning",
                            "Analisar"
                        )}

                    </div>

                </div>

            </div>


            <div>

                <div class="panel">

                    <div class="panel-header">

                        <h3>
                            Frequência
                        </h3>

                        <span>
                            Pendências
                        </span>

                    </div>


                    ${
                        pending.length
                        ? `
                            <div class="activity-list">

                                ${pending
                                    .slice(0, 5)
                                    .map(
                                        item =>
                                        activity(
                                            "Falta pendente",
                                            `Registro #${item.id}`,
                                            "warning",
                                            "Pendente"
                                        )
                                    )
                                    .join("")
                                }

                            </div>
                        `
                        :
                        `
                            <div class="empty-state">
                                Nenhuma pendência no momento.
                            </div>
                        `
                    }

                </div>

            </div>

        </section>

    `;


    bindQuickActions();
}


/* =====================================================
   ADMINISTRAÇÃO
===================================================== */

async function renderAdminDashboard() {

    let users = [];

    let classrooms = [];

    let teachers = [];


    try {

        users =
            await apiRequest(
                "/users/"
            );

    } catch {}


    try {

        classrooms =
            await apiRequest(
                "/classrooms"
            );

    } catch {}


    try {

        teachers =
            await apiRequest(
                "/teachers"
            );

    } catch {}


    pageContent.innerHTML = `

        <section class="dashboard-welcome">

            <h2>
                Administração
            </h2>

            <p>
                Acompanhe a estrutura acadêmica da instituição.
            </p>

        </section>


        <section class="stats-grid">

            ${statCard(
                "Usuários",
                users.length,
                "♙",
                "Contas cadastradas"
            )}

            ${statCard(
                "Professores",
                teachers.length,
                "♙",
                "Professores cadastrados"
            )}

            ${statCard(
                "Turmas",
                classrooms.length,
                "▦",
                "Turmas cadastradas"
            )}

            ${statCard(
                "Relatórios",
                "—",
                "↗",
                "Dados institucionais"
            )}

        </section>


        <section class="dashboard-grid">

            <div>

                <div class="panel">

                    <div class="panel-header">

                        <h3>
                            Gestão institucional
                        </h3>

                    </div>


                    <div class="quick-actions">

                        ${quickAction(
                            "Usuários",
                            "Alunos e professores",
                            "users"
                        )}

                        ${quickAction(
                            "Turmas",
                            "Organizar estrutura",
                            "classrooms"
                        )}

                        ${quickAction(
                            "Matrículas",
                            "Gerenciar alunos",
                            "enrollments"
                        )}

                        ${quickAction(
                            "Relatórios",
                            "Indicadores acadêmicos",
                            "reports"
                        )}

                    </div>

                </div>


                <div class="panel">

                    <div class="panel-header">

                        <h3>
                            Administração acadêmica
                        </h3>

                    </div>


                    <div class="activity-list">

                        ${activity(
                            "Frequência",
                            "Consultar presença dos estudantes",
                            "info",
                            "Consultar"
                        )}

                        ${activity(
                            "Turmas",
                            "Visualizar alunos por turma",
                            "success",
                            classrooms.length
                        )}

                        ${activity(
                            "Professores",
                            "Gerenciar vínculos institucionais",
                            "warning",
                            teachers.length
                        )}

                    </div>

                </div>

            </div>


            <div>

                <div class="panel">

                    <div class="panel-header">

                        <h3>
                            Instituição
                        </h3>

                    </div>


                    <div class="activity-list">

                        ${activity(
                            "Contas",
                            "Usuários cadastrados",
                            "info",
                            users.length
                        )}

                        ${activity(
                            "Turmas",
                            "Estruturas ativas",
                            "success",
                            classrooms.length
                        )}

                    </div>

                </div>

            </div>

        </section>

    `;


    bindQuickActions();
}


/* =====================================================
   SUPORTE
===================================================== */

async function renderSupportDashboard() {

    pageContent.innerHTML = `

        <section class="dashboard-welcome">

            <h2>
                Painel de suporte
            </h2>

            <p>
                Gerencie a estrutura operacional do Mentor.Edu.
            </p>

        </section>


        <section class="stats-grid">

            ${statCard(
                "Usuários",
                "—",
                "♙",
                "Gerenciamento de contas"
            )}

            ${statCard(
                "Estrutura",
                "—",
                "▦",
                "Cadastros institucionais"
            )}

            ${statCard(
                "Sistema",
                "Online",
                "✓",
                "Serviço disponível"
            )}

            ${statCard(
                "Chamados",
                "—",
                "⚙",
                "Será implementado"
            )}

        </section>


        <div class="panel">

            <div class="panel-header">

                <h3>
                    Administração operacional
                </h3>

            </div>


            <div class="quick-actions">

                ${quickAction(
                    "Usuários",
                    "Criar e gerenciar contas",
                    "users"
                )}

                ${quickAction(
                    "Estrutura",
                    "Turmas e instituições",
                    "classrooms"
                )}

                ${quickAction(
                    "Suporte",
                    "Chamados técnicos",
                    "support"
                )}

                ${quickAction(
                    "Perfil",
                    "Minha conta",
                    "profile"
                )}

            </div>

        </div>

    `;


    bindQuickActions();
}


/* =====================================================
   PÁGINAS FUNCIONAIS DO PROTÓTIPO
===================================================== */
async function renderStudentAttendancePage() {

    pageContent.innerHTML = `
        <div class="loading-dashboard">
            Carregando sua frequência...
        </div>
    `;


    let summary = null;
    let attendance = [];
    let subjects = [];


    try {

        summary = await apiRequest(
            "/attendance/me/summary"
        );

        attendance = await apiRequest(
            "/attendance/me"
        );

        subjects = await apiRequest(
            "/subjects/me"
        );

    }

    catch (error) {

        console.error(error);

        pageContent.innerHTML = `
            <div class="panel">
                <div class="empty-state">
                    Não foi possível carregar sua frequência.
                </div>
            </div>
        `;

        return;
    }


    /* ==========================================
       MAPA DAS DISCIPLINAS
    ========================================== */

    const subjectMap = {};

    subjects.forEach(
        subject => {

            subjectMap[subject.id] =
                subject.nome;
        }
    );


    /* ==========================================
       DADOS
    ========================================== */

    const percentual =
        summary?.percentual_presenca ?? 0;

    const presencas =
        summary?.presencas ?? 0;

    const justificadas =
        summary?.faltas_justificadas ?? 0;

    const naoJustificadas =
        summary?.faltas_nao_justificadas ?? 0;

    const pendentes =
        summary?.faltas_pendentes ?? 0;

    const aulasRegistradas =
        summary?.aulas_registradas ?? 0;


    pageContent.innerHTML = `

        <div class="page-header">

            <div>

                <h2>
                    Minha frequência
                </h2>

                <p>
                    Acompanhe suas presenças, faltas
                    e justificativas.
                </p>

            </div>

        </div>


        <section class="stats-grid">

            ${statCard(
                "Frequência",
                `${percentual}%`,
                "◷",
                "Percentual de presença"
            )}

            ${statCard(
                "Presenças",
                presencas,
                "✓",
                "Presenças registradas"
            )}

            ${statCard(
                "Faltas justificadas",
                justificadas,
                "✓",
                "Ausências justificadas"
            )}

            ${statCard(
                "Pendências",
                pendentes,
                "!",
                "Aguardando justificativa"
            )}

        </section>


        <section class="attendance-layout">

            <div class="panel">

                <div class="panel-header">

                    <div>
                        <h3>
                            Frequência geral
                        </h3>

                        <span>
                            ${aulasRegistradas}
                            registros acadêmicos
                        </span>
                    </div>

                </div>


                <div class="frequency-highlight">

                    <div
                        class="frequency-circle"
                    >

                        <strong>
                            ${percentual}%
                        </strong>

                        <span>
                            presença
                        </span>

                    </div>


                    <div class="frequency-progress-area">

                        <div class="frequency-progress-header">

                            <span>
                                Progresso de frequência
                            </span>

                            <strong>
                                ${percentual}%
                            </strong>

                        </div>


                        <div class="frequency-progress">

                            <div
                                class="frequency-progress-bar"
                                style="
                                    width:
                                    ${Math.min(
                                        percentual,
                                        100
                                    )}%
                                "
                            ></div>

                        </div>


                        <p>
                            Este percentual considera
                            as aulas já registradas
                            no sistema.
                        </p>

                    </div>

                </div>

            </div>


            <div class="panel">

                <div class="panel-header">

                    <h3>
                        Situação
                    </h3>

                </div>


                <div class="attendance-summary-list">

                    ${attendanceSummaryItem(
                        "Presenças",
                        presencas,
                        "success"
                    )}

                    ${attendanceSummaryItem(
                        "Faltas justificadas",
                        justificadas,
                        "info"
                    )}

                    ${attendanceSummaryItem(
                        "Faltas não justificadas",
                        naoJustificadas,
                        "danger"
                    )}

                    ${attendanceSummaryItem(
                        "Pendentes",
                        pendentes,
                        "warning"
                    )}

                </div>

            </div>

        </section>


        <section class="panel">

            <div class="panel-header">

                <div>

                    <h3>
                        Histórico de frequência
                    </h3>

                    <span>
                        Registros mais recentes
                    </span>

                </div>

            </div>


            ${
                attendance.length
                ? `
                    <div class="attendance-table">

                        <div class="attendance-row attendance-table-header">

                            <div>
                                Disciplina
                            </div>

                            <div>
                                Data
                            </div>

                            <div>
                                Situação
                            </div>

                            <div>
                                Observação
                            </div>

                        </div>


                        ${attendance
                            .map(
                                item => {

                                    const subject =
                                        subjectMap[
                                            item.subject_id
                                        ] ||
                                        "Disciplina";

                                    return `
                                        <div class="attendance-row">

                                            <div class="attendance-subject">

                                                <strong>
                                                    ${subject}
                                                </strong>

                                            </div>


                                            <div>

                                                ${formatDate(
                                                    item.data
                                                )}

                                            </div>


                                            <div>

                                                ${attendanceStatusBadge(
                                                    item.status
                                                )}

                                            </div>


                                            <div class="attendance-observation">

                                                ${
                                                    item.observacao ||
                                                    item.motivo ||
                                                    "—"
                                                }

                                            </div>

                                        </div>
                                    `;
                                }
                            )
                            .join("")
                        }

                    </div>
                `
                :
                `
                    <div class="empty-state">

                        Nenhum registro de frequência
                        encontrado.

                    </div>
                `
            }

        </section>

    `;
}

function attendanceSummaryItem(
    title,
    value,
    type
) {

    return `

        <div class="attendance-summary-item">

            <div>

                <span class="attendance-dot ${type}">
                </span>

                <strong>
                    ${title}
                </strong>

            </div>

            <span>
                ${value}
            </span>

        </div>

    `;
}


function attendanceStatusBadge(
    status
) {

    const statuses = {

        presente: {
            label: "Presente",
            className: "success"
        },

        falta_pendente: {
            label: "Justificativa pendente",
            className: "warning"
        },

        falta_justificada: {
            label: "Falta justificada",
            className: "info"
        },

        falta_nao_justificada: {
            label: "Falta não justificada",
            className: "danger"
        }

    };


    const config =
        statuses[status] || {
            label: status,
            className: "info"
        };


    return `
        <span class="status ${config.className}">
            ${config.label}
        </span>
    `;
}


function formatDate(
    dateString
) {

    if (!dateString) {
        return "—";
    }


    const date =
        new Date(dateString);


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "—";
    }


    return date.toLocaleDateString(
        "pt-BR",
        {
            day: "2-digit",
            month: "2-digit",
            year: "numeric"
        }
    );
}


function renderFeaturePage(page) {

    const configs = {

        subjects: {
            title: "Minhas disciplinas",
            description:
                "Acesse conteúdos, desempenho, notas e atividades.",
            cards: [
                [
                    "📚",
                    "Conteúdos",
                    "Materiais organizados por disciplina."
                ],
                [
                    "✓",
                    "Atividades",
                    "Veja atividades atuais e encerradas."
                ],
                [
                    "↗",
                    "Meu desempenho",
                    "Acompanhe sua evolução acadêmica."
                ]
            ]
        },

        classrooms: {
            title: "Turmas",
            description:
                "Gerencie e consulte suas turmas.",
            cards: [
                [
                    "▦",
                    "Turmas",
                    "Visualize todas as turmas disponíveis."
                ],
                [
                    "♙",
                    "Alunos",
                    "Consulte os estudantes de cada turma."
                ],
                [
                    "📚",
                    "Disciplinas",
                    "Veja as disciplinas vinculadas."
                ]
            ]
        },

        attendance: {
            title: "Frequência",
            description:
                "Presenças, faltas e justificativas.",
            cards: [
                [
                    "✓",
                    "Chamada",
                    "Registre presença ou ausência."
                ],
                [
                    "!",
                    "Pendências",
                    "Acompanhe justificativas pendentes."
                ],
                [
                    "↗",
                    "Resumo",
                    "Consulte indicadores de frequência."
                ]
            ]
        },

        assessments: {
            title: "Avaliações",
            description:
                "Provas, atividades e resultados.",
            cards: [
                [
                    "□",
                    "Avaliações",
                    "Consulte avaliações disponíveis."
                ],
                [
                    "+",
                    "Criar avaliação",
                    "Monte provas e atividades."
                ],
                [
                    "↗",
                    "Resultados",
                    "Veja desempenho e correções."
                ]
            ]
        },

        performance: {
            title: "Desempenho",
            description:
                "Veja sua evolução acadêmica.",
            cards: [
                [
                    "↗",
                    "Evolução",
                    "Indicadores ao longo do tempo."
                ],
                [
                    "!",
                    "Dificuldades",
                    "Conteúdos que precisam de atenção."
                ],
                [
                    "✓",
                    "Pontos fortes",
                    "Áreas de melhor desempenho."
                ]
            ]
        },

        questions: {
            title: "Banco de questões",
            description:
                "Organize questões pedagógicas.",
            cards: [
                [
                    "+",
                    "Nova questão",
                    "Cadastre uma nova questão."
                ],
                [
                    "📚",
                    "Minha biblioteca",
                    "Questões criadas por você."
                ],
                [
                    "🔎",
                    "Pesquisar",
                    "Filtre por disciplina e conteúdo."
                ]
            ]
        },

        reports: {
            title: "Relatórios",
            description:
                "Indicadores e análises acadêmicas.",
            cards: [
                [
                    "↗",
                    "Desempenho",
                    "Análise dos estudantes."
                ],
                [
                    "◷",
                    "Frequência",
                    "Indicadores de presença."
                ],
                [
                    "□",
                    "Avaliações",
                    "Resultados das avaliações."
                ]
            ]
        },

        users: {
            title: "Usuários",
            description:
                "Gerencie contas da instituição.",
            cards: [
                [
                    "+",
                    "Novo usuário",
                    "Cadastrar aluno ou professor."
                ],
                [
                    "♙",
                    "Usuários",
                    "Consultar contas cadastradas."
                ],
                [
                    "🔎",
                    "Pesquisar",
                    "Localizar usuário."
                ]
            ]
        },

        teachers: {
            title: "Professores",
            description:
                "Gerencie professores e vínculos.",
            cards: [
                [
                    "♙",
                    "Professores",
                    "Consulte o corpo docente."
                ],
                [
                    "📚",
                    "Disciplinas",
                    "Veja vínculos pedagógicos."
                ],
                [
                    "▦",
                    "Turmas",
                    "Turmas de cada professor."
                ]
            ]
        },

        enrollments: {
            title: "Matrículas",
            description:
                "Gerencie alunos e turmas.",
            cards: [
                [
                    "+",
                    "Nova matrícula",
                    "Matricular aluno em uma turma."
                ],
                [
                    "✓",
                    "Ativas",
                    "Consultar matrículas atuais."
                ],
                [
                    "▦",
                    "Por turma",
                    "Ver estudantes matriculados."
                ]
            ]
        },

        support: {
            title: "Suporte",
            description:
                "Área operacional do sistema.",
            cards: [
                [
                    "⚙",
                    "Chamados",
                    "Gerenciar solicitações técnicas."
                ],
                [
                    "✓",
                    "Sistema",
                    "Consultar estado dos serviços."
                ],
                [
                    "♙",
                    "Contas",
                    "Auxiliar usuários."
                ]
            ]
        },

        profile: {
            title: "Meu perfil",
            description:
                "Informações pessoais e institucionais.",
            cards: [
                [
                    "○",
                    currentUser.nome,
                    currentUser.email || "E-mail não informado"
                ],
                [
                    "✓",
                    "Perfil",
                    currentUser.tipo
                ],
                [
                    "⚙",
                    "Configurações",
                    "Preferências da conta."
                ]
            ]
        }

    };


    const config =
        configs[page];


    if (!config) {

        pageContent.innerHTML =
            `
                <div class="empty-state">
                    Página em desenvolvimento.
                </div>
            `;

        return;
    }


    pageContent.innerHTML = `

        <div class="page-header">

            <div>

                <h2>
                    ${config.title}
                </h2>

                <p>
                    ${config.description}
                </p>

            </div>

        </div>


        <div class="feature-grid">

            ${config.cards
                .map(
                    card => `

                        <div class="feature-card">

                            <div class="feature-card-icon">
                                ${card[0]}
                            </div>

                            <h3>
                                ${card[1]}
                            </h3>

                            <p>
                                ${card[2]}
                            </p>

                        </div>

                    `
                )
                .join("")
            }

        </div>

    `;
}


/* =====================================================
   COMPONENTES
===================================================== */

function statCard(
    title,
    value,
    icon,
    description
) {

    return `

        <article class="stat-card">

            <div class="stat-card-header">

                <span class="stat-title">
                    ${title}
                </span>

                <div class="stat-icon">
                    ${icon}
                </div>

            </div>

            <div class="stat-value">
                ${value}
            </div>

            <div class="stat-description">
                ${description}
            </div>

        </article>

    `;
}


function activity(
    title,
    description,
    type,
    badge
) {

    return `

        <div class="activity-item">

            <div class="activity-info">

                <strong>
                    ${title}
                </strong>

                <span>
                    ${description}
                </span>

            </div>

            <span class="status ${type}">
                ${badge}
            </span>

        </div>

    `;
}


function quickAction(
    title,
    description,
    page
) {

    return `

        <button
            class="quick-action"
            data-target="${page}"
        >

            <strong>
                ${title}
            </strong>

            <span>
                ${description}
            </span>

        </button>

    `;
}


/* =====================================================
   ATALHOS
===================================================== */

function bindQuickActions() {

    document
        .querySelectorAll(
            ".quick-action"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        renderPage(
                            button.dataset.target
                        );

                    }
                );
            }
        );
}


/* =====================================================
   LOGOUT
===================================================== */

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "mentor_user"
    );

    window.location.href =
        "index.html";
}


logoutButton.addEventListener(
    "click",
    logout
);


/* =====================================================
   MOBILE
===================================================== */

document
    .getElementById(
        "mobileMenuButton"
    )
    .addEventListener(
        "click",
        () => {

            document
                .getElementById(
                    "sidebar"
                )
                .classList
                .toggle(
                    "open"
                );
        }
    );


/* =====================================================
   INICIAR
===================================================== */

loadUser();