function firstName(user) {
    const raw = user?.nome || user?.name || "Aluno";
    return String(raw).trim().split(/\s+/)[0] || "Aluno";
}

const sections = [
    {
        id: "perfil",
        eyebrow: "Perfil",
        title: "Seu perfil de aprendizagem",
        icon: "◎",
        summary: "Uma visão rápida de como você aprende melhor.",
        body: `
            <div class="mentor-insight-grid mentor-insight-grid--3">
                <article class="mentor-mini-card">
                    <span class="mentor-mini-label">Ritmo</span>
                    <strong>Equilibrado</strong>
                    <p>Você poderá acompanhar sua evolução e ajustar o ritmo de estudo.</p>
                </article>
                <article class="mentor-mini-card">
                    <span class="mentor-mini-label">Preferência</span>
                    <strong>Passo a passo</strong>
                    <p>Explicações guiadas e exercícios serão organizados aqui.</p>
                </article>
                <article class="mentor-mini-card">
                    <span class="mentor-mini-label">Objetivo</span>
                    <strong>Evolução contínua</strong>
                    <p>O Mentor Edu destacará prioridades sem sobrecarregar a tela.</p>
                </article>
            </div>
        `,
    },
    {
        id: "fortes",
        eyebrow: "Desempenho",
        title: "Pontos fortes",
        icon: "↗",
        summary: "Conteúdos e hábitos em que você vem se destacando.",
        body: `
            <div class="mentor-list-preview">
                <div><span class="mentor-status mentor-status--good">Forte</span><strong>Organização dos estudos</strong><p>Seus melhores indicadores aparecerão aqui quando conectarmos os dados reais.</p></div>
                <div><span class="mentor-status mentor-status--good">Forte</span><strong>Participação</strong><p>A IA poderá cruzar desempenho, frequência e atividades concluídas.</p></div>
            </div>
        `,
    },
    {
        id: "melhorar",
        eyebrow: "Prioridades",
        title: "Pontos para melhorar",
        icon: "!",
        summary: "O Mentor destacará primeiro o que merece sua atenção.",
        body: `
            <div class="mentor-list-preview">
                <div><span class="mentor-status mentor-status--attention">Atenção</span><strong>Conteúdo prioritário</strong><p>A disciplina com maior necessidade de revisão aparecerá neste espaço.</p></div>
                <div><span class="mentor-status mentor-status--attention">Atenção</span><strong>Regularidade</strong><p>O sistema poderá sugerir pequenas sessões para evitar acúmulo.</p></div>
            </div>
        `,
    },
    {
        id: "sugestoes",
        eyebrow: "Mentor",
        title: "Sugestões do Mentor",
        icon: "✦",
        summary: "Ações curtas e objetivas para o seu próximo estudo.",
        body: `
            <div class="mentor-suggestion-stack">
                <button type="button" class="mentor-suggestion" data-preview-action>
                    <span>01</span>
                    <div><strong>Revisar um ponto importante</strong><p>Sugestões reais entrarão na próxima etapa.</p></div>
                    <b>→</b>
                </button>
                <button type="button" class="mentor-suggestion" data-preview-action>
                    <span>02</span>
                    <div><strong>Resolver exercícios guiados</strong><p>O Tutor poderá montar uma sequência adequada ao seu nível.</p></div>
                    <b>→</b>
                </button>
            </div>
        `,
    },
    {
        id: "plano",
        eyebrow: "Organização",
        title: "Plano de estudos",
        icon: "▦",
        summary: "Acesse rapidamente seu plano, recomendações e sessões.",
        body: `
            <div class="mentor-action-grid">
                <button type="button" class="mentor-action-card" data-go="study-plans">
                    <span>Meu plano</span>
                    <strong>Ver planejamento</strong>
                    <small>Seu plano de estudos atual</small>
                </button>
                <button type="button" class="mentor-action-card" data-go="recommendations">
                    <span>Plano indicado</span>
                    <strong>Ver recomendações</strong>
                    <small>Sugestões personalizadas</small>
                </button>
                <button type="button" class="mentor-action-card" data-go="study-sessions">
                    <span>Sessões de estudo</span>
                    <strong>Abrir sessões</strong>
                    <small>Histórico e próximas sessões</small>
                </button>
            </div>
        `,
    },
    {
        id: "alertas",
        eyebrow: "Atenção",
        title: "Alertas inteligentes",
        icon: "◉",
        summary: "Avisos relevantes, sem encher a tela de informação.",
        body: `
            <div class="mentor-alert-preview">
                <span class="mentor-alert-dot"></span>
                <div>
                    <strong>Nenhum alerta real conectado nesta etapa.</strong>
                    <p>Depois, a IA poderá mostrar avaliações próximas, queda de desempenho e prioridades de estudo.</p>
                </div>
            </div>
        `,
    },
];

function sectionMarkup(section) {
    return `
        <article class="mentor-collapse-card" data-mentor-section="${section.id}">
            <button class="mentor-collapse-head" type="button" aria-expanded="false">
                <span class="mentor-collapse-icon">${section.icon}</span>
                <span class="mentor-collapse-copy">
                    <small>${section.eyebrow}</small>
                    <strong>${section.title}</strong>
                    <em>${section.summary}</em>
                </span>
                <span class="mentor-collapse-action">
                    <span data-toggle-label>Ver mais</span>
                    <b aria-hidden="true">⌄</b>
                </span>
            </button>
            <div class="mentor-collapse-body" hidden>
                ${section.body}
            </div>
        </article>
    `;
}

export async function renderStudentMentorEdu(container, user, navigate) {
    const name = firstName(user);

    container.innerHTML = `
        <section class="mentor-page">
            <header class="mentor-page-head">
                <div>
                    <span class="mentor-page-kicker">MENTOR EDU • INSIGHTS COM IA</span>
                    <h1>Olá, ${name}! <span aria-hidden="true">👋</span></h1>
                    <p>Seu espaço para entender o aprendizado, organizar os estudos e conversar com o Mentor.</p>
                </div>
                <span class="mentor-page-badge">Prévia visual</span>
            </header>

            <article class="mentor-hero">
                <div class="mentor-hero-bot">
                    <img src="assets/brand/mentor-ai-bot.png" alt="Robô do Mentor Edu">
                </div>
                <div class="mentor-hero-copy">
                    <span>Seu copiloto de aprendizagem</span>
                    <h2>Insights claros, sem sobrecarregar sua tela.</h2>
                    <p>
                        Os detalhes ficam fechados por padrão. Abra somente o que quiser consultar.
                        Na próxima etapa, estes módulos receberão dados reais do seu perfil.
                    </p>
                </div>
                <button class="mentor-primary-button" type="button" data-open-chat>
                    Conversar com o Mentor
                </button>
            </article>

            <div class="mentor-layout">
                <div class="mentor-insights-column">
                    ${sections.map(sectionMarkup).join("")}
                </div>

                <aside class="mentor-side-column">
                    <article class="mentor-week-card">
                        <div class="mentor-card-heading">
                            <div>
                                <small>ESTA SEMANA</small>
                                <strong>Resumo de estudo</strong>
                            </div>
                            <span>7 dias</span>
                        </div>
                        <div class="mentor-week-stat">
                            <strong>3</strong>
                            <span>áreas organizadas no Mentor Edu</span>
                        </div>
                        <div class="mentor-week-bars" aria-hidden="true">
                            <i style="height:34%"></i>
                            <i style="height:52%"></i>
                            <i style="height:44%"></i>
                            <i style="height:76%"></i>
                            <i style="height:62%"></i>
                            <i style="height:88%"></i>
                            <i style="height:70%"></i>
                        </div>
                        <p>Os dados reais de estudo entram quando conectarmos a IA ao seu perfil.</p>
                    </article>

                    <article class="mentor-tip-card">
                        <span>✦</span>
                        <div>
                            <small>DICA DO MENTOR</small>
                            <strong>Comece pelo que mais precisa de atenção.</strong>
                            <p>Depois, use o chat para pedir uma explicação passo a passo.</p>
                        </div>
                    </article>
                </aside>
            </div>

            <section class="mentor-chat-card" data-mentor-chat>
                <header class="mentor-chat-head">
                    <div class="mentor-chat-identity">
                        <img src="assets/brand/mentor-ai-bot.png" alt="">
                        <div>
                            <small>ASSISTENTE DE ESTUDOS</small>
                            <strong>Conversar com Mentor.Edu</strong>
                            <span><i></i> Interface pronta • IA será conectada na próxima etapa</span>
                        </div>
                    </div>
                    <div class="mentor-chat-actions">
                        <button type="button" class="mentor-ghost-button" data-expand-chat>Expandir chat</button>
                        <button type="button" class="mentor-chat-close" data-close-chat aria-label="Fechar chat">×</button>
                    </div>
                </header>

                <div class="mentor-chat-body">
                    <div class="mentor-chat-welcome">
                        <img src="assets/brand/mentor-ai-bot.png" alt="">
                        <div>
                            <strong>Olá, ${name}! Eu sou o Mentor.Edu.</strong>
                            <p>
                                Nesta etapa o chat é apenas visual. Na próxima, eu vou responder usando
                                o Tutor IA que já está funcionando no backend.
                            </p>
                        </div>
                    </div>

                    <div class="mentor-chat-suggestions">
                        <button type="button" data-preview-message>Explique um conteúdo passo a passo</button>
                        <button type="button" data-preview-message>Monte uma revisão para mim</button>
                        <button type="button" data-preview-message>Quero praticar com exercícios</button>
                    </div>
                </div>

                <form class="mentor-chat-compose" data-chat-form>
                    <input type="text" placeholder="Pergunte qualquer coisa ao Mentor.Edu..." aria-label="Mensagem para o Mentor Edu">
                    <button type="submit">Enviar</button>
                </form>
            </section>

            <div class="mentor-preview-toast" data-preview-toast hidden>
                A IA real será conectada na próxima etapa.
            </div>
        </section>
    `;

    const page = container.querySelector(".mentor-page");
    const chat = page.querySelector("[data-mentor-chat]");
    const toast = page.querySelector("[data-preview-toast]");

    function showPreviewToast(message = "A IA real será conectada na próxima etapa.") {
        if (!toast) return;
        toast.textContent = message;
        toast.hidden = false;
        clearTimeout(showPreviewToast.timer);
        showPreviewToast.timer = setTimeout(() => {
            toast.hidden = true;
        }, 2600);
    }

    page.querySelectorAll(".mentor-collapse-head").forEach(button => {
        button.addEventListener("click", () => {
            const card = button.closest("[data-mentor-section]");
            const body = card?.querySelector(".mentor-collapse-body");
            const label = button.querySelector("[data-toggle-label]");
            if (!body) return;

            const opening = body.hidden;
            body.hidden = !opening;
            card.classList.toggle("is-open", opening);
            button.setAttribute("aria-expanded", String(opening));
            if (label) label.textContent = opening ? "Fechar" : "Ver mais";
        });
    });

    page.querySelectorAll("[data-go]").forEach(button => {
        button.addEventListener("click", () => navigate(button.dataset.go));
    });

    const openChat = () => {
        chat.classList.add("is-open");
        chat.scrollIntoView({ behavior: "smooth", block: "center" });
        setTimeout(() => chat.querySelector("input")?.focus(), 280);
    };

    page.querySelector("[data-open-chat]")?.addEventListener("click", openChat);

    page.querySelector("[data-close-chat]")?.addEventListener("click", () => {
        chat.classList.remove("is-open", "is-fullscreen");
        document.body.classList.remove("mentor-chat-fullscreen-open");
        const expand = chat.querySelector("[data-expand-chat]");
        if (expand) expand.textContent = "Expandir chat";
    });

    page.querySelector("[data-expand-chat]")?.addEventListener("click", event => {
        chat.classList.add("is-open");
        const fullscreen = chat.classList.toggle("is-fullscreen");
        document.body.classList.toggle("mentor-chat-fullscreen-open", fullscreen);
        event.currentTarget.textContent = fullscreen ? "Reduzir chat" : "Expandir chat";
        if (fullscreen) setTimeout(() => chat.querySelector("input")?.focus(), 100);
    });

    page.querySelector("[data-chat-form]")?.addEventListener("submit", event => {
        event.preventDefault();
        showPreviewToast();
    });

    page.querySelectorAll("[data-preview-message], [data-preview-action]").forEach(button => {
        button.addEventListener("click", () => {
            openChat();
            showPreviewToast();
        });
    });

    const onKeyDown = event => {
        if (event.key === "Escape" && chat.classList.contains("is-fullscreen")) {
            chat.classList.remove("is-fullscreen");
            document.body.classList.remove("mentor-chat-fullscreen-open");
            const expand = chat.querySelector("[data-expand-chat]");
            if (expand) expand.textContent = "Expandir chat";
        }
    };

    document.addEventListener("keydown", onKeyDown, { signal: page._mentorAbort?.signal });

    // Evita deixar o body travado se o usuário navegar enquanto o chat estiver expandido.
    const observer = new MutationObserver(() => {
        if (!document.body.contains(page)) {
            document.body.classList.remove("mentor-chat-fullscreen-open");
            observer.disconnect();
        }
    });
    observer.observe(container, { childList: true });
}
