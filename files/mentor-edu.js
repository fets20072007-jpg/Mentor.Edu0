import { api } from "../../api/client.js";

const PROFILE_CACHE_MS = 5 * 60 * 1000;
const CHAT_HISTORY_LIMIT = 40;

function firstName(user) {
    const raw = user?.nome || user?.name || "Aluno";
    return String(raw).trim().split(/\s+/)[0] || "Aluno";
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function humanize(value) {
    if (value === null || value === undefined || value === "") return "Em análise";
    return String(value)
        .replaceAll("_", " ")
        .replaceAll("-", " ")
        .replace(/\b\w/g, letter => letter.toUpperCase());
}

function normalizeList(value) {
    if (!value) return [];
    if (Array.isArray(value)) return value.filter(Boolean);
    if (typeof value === "string") {
        return value
            .split(/\n|;/)
            .map(item => item.replace(/^[\s•\-–—\d.)]+/, "").trim())
            .filter(Boolean);
    }
    if (typeof value === "object") {
        return Object.values(value).filter(Boolean);
    }
    return [value];
}

function itemParts(item) {
    if (typeof item === "string" || typeof item === "number") {
        return { title: String(item), detail: "" };
    }

    if (item && typeof item === "object") {
        const title =
            item.titulo ??
            item.title ??
            item.nome ??
            item.name ??
            item.ponto ??
            item.acao ??
            item.sugestao ??
            item.disciplina ??
            item.area ??
            item.texto ??
            item.resumo ??
            "Insight";

        const detail =
            item.descricao ??
            item.description ??
            item.detalhe ??
            item.detail ??
            item.motivo ??
            item.justificativa ??
            item.explicacao ??
            "";

        return { title: String(title), detail: String(detail || "") };
    }

    return { title: String(item ?? "Insight"), detail: "" };
}

function formatMetric(value, suffix = "") {
    if (value === null || value === undefined || value === "") return "—";
    const number = Number(value);
    if (!Number.isFinite(number)) return `${value}${suffix}`;
    const rounded = Number.isInteger(number) ? number : Number(number.toFixed(1));
    return `${rounded}${suffix}`;
}

function metricNumber(value) {
    if (typeof value === "number") return value;
    if (value && typeof value === "object") {
        const candidate =
            value.media ??
            value.percentual ??
            value.desempenho ??
            value.nota ??
            value.valor ??
            value.score;
        const parsed = Number(candidate);
        return Number.isFinite(parsed) ? parsed : null;
    }
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
}

function getSubjectEntries(metrics) {
    const source =
        metrics?.desempenho_por_disciplina ??
        metrics?.disciplinas ??
        metrics?.por_disciplina ??
        metrics?.subjects ??
        {};

    if (!source || typeof source !== "object" || Array.isArray(source)) return [];

    return Object.entries(source)
        .map(([name, value]) => ({
            name,
            value: metricNumber(value),
        }))
        .filter(item => item.value !== null)
        .sort((a, b) => b.value - a.value);
}

function listMarkup(items, tone = "good", emptyText = "Nenhum dado disponível ainda.") {
    const normalized = normalizeList(items);

    if (!normalized.length) {
        return `
            <div class="mentor-empty-state">
                <strong>Ainda não há informação suficiente.</strong>
                <p>${escapeHtml(emptyText)}</p>
            </div>
        `;
    }

    return `
        <div class="mentor-real-list">
            ${normalized.map((item, index) => {
                const { title, detail } = itemParts(item);
                return `
                    <article class="mentor-real-item">
                        <span class="mentor-status mentor-status--${tone}">
                            ${tone === "good" ? "Forte" : tone === "attention" ? "Atenção" : String(index + 1).padStart(2, "0")}
                        </span>
                        <div>
                            <strong>${escapeHtml(title)}</strong>
                            ${detail ? `<p>${escapeHtml(detail)}</p>` : ""}
                        </div>
                    </article>
                `;
            }).join("")}
        </div>
    `;
}

function suggestionsMarkup(items) {
    const normalized = normalizeList(items);

    if (!normalized.length) {
        return `
            <div class="mentor-empty-state">
                <strong>Sem sugestões novas por enquanto.</strong>
                <p>O Mentor vai criar ações assim que houver dados suficientes do seu perfil.</p>
            </div>
        `;
    }

    return `
        <div class="mentor-suggestion-stack">
            ${normalized.map((item, index) => {
                const { title, detail } = itemParts(item);
                return `
                    <button
                        type="button"
                        class="mentor-suggestion"
                        data-real-suggestion="${escapeHtml(title)}"
                    >
                        <span>${String(index + 1).padStart(2, "0")}</span>
                        <div>
                            <strong>${escapeHtml(title)}</strong>
                            ${detail ? `<p>${escapeHtml(detail)}</p>` : `<p>Sugestão criada a partir do seu perfil.</p>`}
                        </div>
                        <b aria-hidden="true">→</b>
                    </button>
                `;
            }).join("")}
        </div>
    `;
}

function loadingMarkup(label) {
    return `
        <div class="mentor-loading-state">
            <span class="mentor-loading-spinner" aria-hidden="true"></span>
            <div>
                <strong>${escapeHtml(label)}</strong>
                <p>O Mentor está analisando seus dados.</p>
            </div>
        </div>
    `;
}

function errorMarkup(message) {
    return `
        <div class="mentor-error-state">
            <strong>Não foi possível carregar esta análise.</strong>
            <p>${escapeHtml(message || "Confira se o backend está ativo e tente novamente.")}</p>
        </div>
    `;
}

function cacheKey(user) {
    const identity = user?.id ?? user?.email ?? user?.matricula ?? "student";
    return `mentor_edu_profile_v1:${identity}`;
}

function readProfileCache(user) {
    try {
        const raw = sessionStorage.getItem(cacheKey(user));
        if (!raw) return null;
        const cached = JSON.parse(raw);
        if (!cached?.at || !cached?.data) return null;
        if (Date.now() - cached.at > PROFILE_CACHE_MS) return null;
        return cached.data;
    } catch {
        return null;
    }
}

function writeProfileCache(user, data) {
    try {
        sessionStorage.setItem(
            cacheKey(user),
            JSON.stringify({ at: Date.now(), data }),
        );
    } catch {
        // Cache é apenas uma otimização; falha nele não impede a página.
    }
}

function clearProfileCache(user) {
    try {
        sessionStorage.removeItem(cacheKey(user));
    } catch {
        // Sem ação.
    }
}


// MENTOR_EDU_CHAT_REAL_V5
function chatHistoryKey(user) {
    const identity = user?.id ?? user?.email ?? user?.matricula ?? "student";
    return `mentor_edu_chat_v1:${identity}`;
}

function readChatHistory(user) {
    try {
        const raw = localStorage.getItem(chatHistoryKey(user));
        const parsed = raw ? JSON.parse(raw) : [];
        return Array.isArray(parsed) ? parsed.slice(-CHAT_HISTORY_LIMIT) : [];
    } catch {
        return [];
    }
}

function writeChatHistory(user, history) {
    try {
        localStorage.setItem(
            chatHistoryKey(user),
            JSON.stringify(history.slice(-CHAT_HISTORY_LIMIT)),
        );
    } catch {
        // Histórico local é um recurso auxiliar.
    }
}

function clearChatHistory(user) {
    try {
        localStorage.removeItem(chatHistoryKey(user));
    } catch {
        // Sem ação.
    }
}

function chatTextHtml(value) {
    return escapeHtml(value).replace(/\n/g, "<br>");
}

function tutorReply(data) {
    const candidate =
        data?.resposta ??
        data?.answer ??
        data?.reply ??
        data?.text ??
        data?.mensagem ??
        data?.message ??
        data?.resultado ??
        data?.result?.text ??
        data?.data?.resposta ??
        data?.data?.text ??
        "";

    let text = "";
    if (typeof candidate === "string") {
        text = candidate.trim();
    } else if (candidate !== null && candidate !== undefined) {
        try {
            text = JSON.stringify(candidate, null, 2);
        } catch {
            text = String(candidate);
        }
    }

    if (!text) {
        text = "Recebi a resposta do Tutor, mas não consegui interpretar o texto retornado.";
    }

    const route = data?.model_route ?? data?.rota_modelo ?? "";
    const model = data?.model ?? data?.modelo ?? "";
    const version = data?.tutor_version ?? data?.versao_tutor ?? "";

    const meta = [route, model, version ? `Tutor ${version}` : ""]
        .filter(Boolean)
        .join(" • ");

    return { text, meta };
}

function chatMessageMarkup(message) {
    const role = message?.role === "user"
        ? "user"
        : message?.role === "error"
            ? "error"
            : "assistant";

    const label = role === "user"
        ? "Você"
        : role === "error"
            ? "Erro"
            : "Mentor.Edu";

    const avatar = role === "user"
        ? `<span class="mentor-chat-user-avatar" aria-hidden="true">Você</span>`
        : `<img src="assets/brand/mentor-ai-bot.png" alt="">`;

    return `
        <article class="mentor-chat-message is-${role}">
            <div class="mentor-chat-message-avatar">${avatar}</div>
            <div class="mentor-chat-message-content">
                <small>${label}</small>
                <div class="mentor-chat-bubble">${chatTextHtml(message?.text ?? "")}</div>
                ${message?.meta ? `<span class="mentor-chat-meta">${escapeHtml(message.meta)}</span>` : ""}
            </div>
        </article>
    `;
}

function renderChatHistory(target, history) {
    if (!target) return;

    if (!history.length) {
        target.innerHTML = `
            <div class="mentor-chat-empty" data-chat-empty>
                <strong>Sua conversa começa aqui.</strong>
                <p>Pergunte sobre Física, Matemática, revisão, exercícios ou outro conteúdo.</p>
            </div>
        `;
        return;
    }

    target.innerHTML = history.map(chatMessageMarkup).join("");
    target.scrollTop = target.scrollHeight;
}

function appendChatMessage(target, message) {
    if (!target) return;
    target.querySelector("[data-chat-empty]")?.remove();
    target.insertAdjacentHTML("beforeend", chatMessageMarkup(message));
    target.scrollTop = target.scrollHeight;
}

function thinkingMarkup() {
    return `
        <article class="mentor-chat-message is-assistant" data-chat-thinking>
            <div class="mentor-chat-message-avatar">
                <img src="assets/brand/mentor-ai-bot.png" alt="">
            </div>
            <div class="mentor-chat-message-content">
                <small>Mentor.Edu</small>
                <div class="mentor-chat-bubble mentor-chat-thinking">
                    <i></i><i></i><i></i>
                    <span>Pensando...</span>
                </div>
            </div>
        </article>
    `;
}

function recentConversationContext(history) {
    const recent = history.slice(-6);
    if (!recent.length) return "";

    return recent
        .map(item => `${item.role === "user" ? "Aluno" : "Mentor"}: ${item.text}`)
        .join("\n");
}


const sections = [
    {
        id: "perfil",
        eyebrow: "Perfil",
        title: "Seu perfil de aprendizagem",
        icon: "◎",
        summary: "Uma visão rápida de como você aprende melhor.",
        target: "profile",
    },
    {
        id: "fortes",
        eyebrow: "Desempenho",
        title: "Pontos fortes",
        icon: "↗",
        summary: "Conteúdos e hábitos em que você vem se destacando.",
        target: "strengths",
    },
    {
        id: "melhorar",
        eyebrow: "Prioridades",
        title: "Pontos para melhorar",
        icon: "!",
        summary: "O Mentor destacará primeiro o que merece sua atenção.",
        target: "attention",
    },
    {
        id: "sugestoes",
        eyebrow: "Mentor",
        title: "Sugestões do Mentor",
        icon: "✦",
        summary: "Ações curtas e objetivas para o seu próximo estudo.",
        target: "suggestions",
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
                    <strong>Alertas inteligentes entram depois do perfil e do chat.</strong>
                    <p>Esta área será conectada às avaliações, frequência e prioridades acadêmicas.</p>
                </div>
            </div>
        `,
    },
];

function sectionMarkup(section) {
    const body = section.target
        ? `<div data-profile-target="${section.target}">${loadingMarkup("Preparando análise...")}</div>`
        : section.body;

    return `
        <article class="mentor-collapse-card" data-mentor-section="${section.id}">
            <button class="mentor-collapse-head" type="button" aria-expanded="false">
                <span class="mentor-collapse-icon">${section.icon}</span>
                <span class="mentor-collapse-copy">
                    <small>${section.eyebrow}</small>
                    <strong>${section.title}</strong>
                    <em data-section-summary="${section.id}">${section.summary}</em>
                </span>
                <span class="mentor-collapse-action">
                    <span data-toggle-label>Ver mais</span>
                    <b aria-hidden="true">⌄</b>
                </span>
            </button>
            <div class="mentor-collapse-body" hidden>
                ${body}
            </div>
        </article>
    `;
}

function profileMarkup(data) {
    const analysis = data?.analise ?? data?.analysis ?? {};
    const metrics = data?.metricas ?? data?.metrics ?? {};
    const profileRaw = data?.perfil ?? data?.profile ?? analysis?.perfil ?? analysis?.profile ?? "Em análise";
    const profileLabel =
        typeof profileRaw === "object"
            ? profileRaw?.nome ?? profileRaw?.tipo ?? profileRaw?.classificacao ?? "Personalizado"
            : profileRaw;

    const summary =
        analysis?.resumo ??
        analysis?.summary ??
        (typeof profileRaw === "object" ? profileRaw?.resumo ?? profileRaw?.descricao : "") ??
        "O Mentor está construindo seu perfil com base nos dados disponíveis.";

    // MENTOR_EDU_METRICS_FIX_V4_1
    const averageRaw =
        metrics?.media_geral ??
        metrics?.media ??
        metrics?.average ??
        metrics?.nota_media ??
        null;

    const attendanceRaw =
        metrics?.frequencia_percentual ??
        metrics?.frequencia ??
        metrics?.attendance ??
        metrics?.presenca ??
        null;

    const average = metricNumber(averageRaw);
    const attendance = metricNumber(attendanceRaw);

    const subjects = getSubjectEntries(metrics);
    const strongest = subjects[0];
    const focus = subjects.length > 1 ? subjects[subjects.length - 1] : subjects[0];

    return `
        <div class="mentor-profile-real">
            <div class="mentor-profile-summary">
                <span class="mentor-ai-source">Análise do Mentor</span>
                <strong>${escapeHtml(humanize(profileLabel))}</strong>
                <p>${escapeHtml(summary)}</p>
            </div>

            <div class="mentor-insight-grid mentor-insight-grid--3">
                <article class="mentor-mini-card">
                    <span class="mentor-mini-label">Média geral</span>
                    <strong>${escapeHtml(formatMetric(average))}</strong>
                    <p>${strongest ? `Destaque atual: ${escapeHtml(humanize(strongest.name))}.` : "Calculada com os dados disponíveis."}</p>
                </article>
                <article class="mentor-mini-card">
                    <span class="mentor-mini-label">Frequência</span>
                    <strong>${escapeHtml(formatMetric(attendance, "%"))}</strong>
                    <p>A presença também ajuda o Mentor a entender seu momento acadêmico.</p>
                </article>
                <article class="mentor-mini-card">
                    <span class="mentor-mini-label">Foco atual</span>
                    <strong>${focus ? escapeHtml(humanize(focus.name)) : "Em análise"}</strong>
                    <p>${focus ? `Indicador atual: ${escapeHtml(formatMetric(focus.value))}.` : "A prioridade aparecerá quando houver dados suficientes."}</p>
                </article>
            </div>
        </div>
    `;
}

function applyProfileData(page, data) {
    const analysis = data?.analise ?? data?.analysis ?? {};

    const strengths =
        analysis?.pontos_fortes ??
        analysis?.strengths ??
        data?.pontos_fortes ??
        [];

    const attention =
        analysis?.pontos_atencao ??
        analysis?.pontos_melhorar ??
        analysis?.areas_melhoria ??
        analysis?.attention_points ??
        data?.pontos_atencao ??
        [];

    const suggestions =
        analysis?.acoes_aluno ??
        analysis?.sugestoes ??
        analysis?.recomendacoes ??
        analysis?.recommendations ??
        data?.sugestoes ??
        [];

    const targets = {
        profile: profileMarkup(data),
        strengths: listMarkup(
            strengths,
            "good",
            "Continue usando o Mentor e registrando atividades para identificar seus destaques.",
        ),
        attention: listMarkup(
            attention,
            "attention",
            "Nenhuma prioridade crítica foi identificada com os dados atuais.",
        ),
        suggestions: suggestionsMarkup(suggestions),
    };

    for (const [key, markup] of Object.entries(targets)) {
        const target = page.querySelector(`[data-profile-target="${key}"]`);
        if (target) target.innerHTML = markup;
    }

    const firstStrength = itemParts(normalizeList(strengths)[0] ?? "").title;
    const firstAttention = itemParts(normalizeList(attention)[0] ?? "").title;
    const firstSuggestion = itemParts(normalizeList(suggestions)[0] ?? "").title;

    const summaryStrength = page.querySelector('[data-section-summary="fortes"]');
    const summaryAttention = page.querySelector('[data-section-summary="melhorar"]');
    const summarySuggestions = page.querySelector('[data-section-summary="sugestoes"]');

    if (summaryStrength && firstStrength) summaryStrength.textContent = firstStrength;
    if (summaryAttention && firstAttention) summaryAttention.textContent = firstAttention;
    if (summarySuggestions && firstSuggestion) summarySuggestions.textContent = firstSuggestion;

    const metrics = data?.metricas ?? data?.metrics ?? {};
    const subjectCount = getSubjectEntries(metrics).length;

    const weekCount = page.querySelector("[data-profile-count]");
    const weekText = page.querySelector("[data-profile-count-text]");
    if (weekCount) weekCount.textContent = subjectCount || "✓";
    if (weekText) {
        weekText.textContent = subjectCount
            ? `${subjectCount} disciplina${subjectCount === 1 ? "" : "s"} analisada${subjectCount === 1 ? "" : "s"} pelo Mentor`
            : "perfil acadêmico analisado pelo Mentor";
    }

    const tipTitle = page.querySelector("[data-mentor-tip-title]");
    const tipText = page.querySelector("[data-mentor-tip-text]");
    if (tipTitle) {
        tipTitle.textContent =
            firstAttention ||
            firstSuggestion ||
            "Continue acompanhando seu perfil.";
    }
    if (tipText) {
        tipText.textContent = firstSuggestion
            ? `Próxima ação sugerida: ${firstSuggestion}`
            : "Abra seus insights para acompanhar as próximas recomendações.";
    }

    const badge = page.querySelector("[data-profile-status]");
    if (badge) {
        badge.textContent = "IA conectada";
        badge.classList.remove("is-loading", "is-error");
        badge.classList.add("is-connected");
    }

    const heroNote = page.querySelector("[data-profile-hero-note]");
    if (heroNote) {
        heroNote.textContent =
            "Os insights abaixo foram preenchidos com dados reais do seu perfil acadêmico.";
    }

    page.querySelectorAll("[data-real-suggestion]").forEach(button => {
        button.addEventListener("click", () => {
            const chat = page.querySelector("[data-mentor-chat]");
            chat?.classList.add("is-open");
            chat?.scrollIntoView({ behavior: "smooth", block: "center" });

            const input = chat?.querySelector("input");
            if (input) {
                input.value = button.dataset.realSuggestion || "";
                setTimeout(() => input.focus(), 250);
            }

            showToast(page, "Sugestão carregada no chat.");
        });
    });
}

function applyProfileError(page, error) {
    const message =
        error?.message ||
        "Confira se o backend está ativo e tente novamente.";

    ["profile", "strengths", "attention", "suggestions"].forEach(key => {
        const target = page.querySelector(`[data-profile-target="${key}"]`);
        if (target) target.innerHTML = errorMarkup(message);
    });

    const badge = page.querySelector("[data-profile-status]");
    if (badge) {
        badge.textContent = "Perfil indisponível";
        badge.classList.remove("is-loading", "is-connected");
        badge.classList.add("is-error");
    }
}

function showToast(page, message) {
    const toast = page.querySelector("[data-preview-toast]");
    if (!toast) return;

    toast.textContent = message;
    toast.hidden = false;

    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(() => {
        toast.hidden = true;
    }, 3000);
}

async function loadStudentProfile(page, user, { force = false } = {}) {
    const badge = page.querySelector("[data-profile-status]");
    const refresh = page.querySelector("[data-refresh-profile]");

    if (refresh) refresh.disabled = true;
    if (badge) {
        badge.textContent = "Analisando perfil...";
        badge.classList.remove("is-connected", "is-error");
        badge.classList.add("is-loading");
    }

    if (force) clearProfileCache(user);

    try {
        let data = !force ? readProfileCache(user) : null;

        if (!data) {
            data = await api.get("/mentor-ai/student/profile");
            writeProfileCache(user, data);
        }

        if (!document.body.contains(page)) return;

        applyProfileData(page, data);
    } catch (error) {
        console.error("[Mentor Edu] Falha ao carregar perfil:", error);
        if (document.body.contains(page)) applyProfileError(page, error);
    } finally {
        if (refresh && document.body.contains(page)) refresh.disabled = false;
    }
}

export async function renderStudentMentorEdu(container, user, navigate) {
    const name = firstName(user);

    container.innerHTML = `
        <section class="mentor-page">
            <header class="mentor-page-head">
                <div>
                    <span class="mentor-page-kicker">MENTOR EDU • INSIGHTS COM IA</span>
                    <h1>Olá, ${escapeHtml(name)}! <span aria-hidden="true">👋</span></h1>
                    <p>Seu espaço para entender o aprendizado, organizar os estudos e conversar com o Mentor.</p>
                </div>

                <div class="mentor-profile-controls">
                    <span class="mentor-page-badge is-loading" data-profile-status>
                        Analisando perfil...
                    </span>
                    <button type="button" class="mentor-profile-refresh" data-refresh-profile>
                        Atualizar análise
                    </button>
                </div>
            </header>

            <article class="mentor-hero">
                <div class="mentor-hero-bot">
                    <img src="assets/brand/mentor-ai-bot.png" alt="Robô do Mentor Edu">
                </div>
                <div class="mentor-hero-copy">
                    <span>Seu copiloto de aprendizagem</span>
                    <h2>Insights claros, sem sobrecarregar sua tela.</h2>
                    <p data-profile-hero-note>
                        O Mentor está preparando seus insights com base nos dados acadêmicos disponíveis.
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
                                <small>PERFIL ATUAL</small>
                                <strong>Resumo da análise</strong>
                            </div>
                            <span>IA</span>
                        </div>
                        <div class="mentor-week-stat">
                            <strong data-profile-count>...</strong>
                            <span data-profile-count-text>preparando análise acadêmica</span>
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
                        <p>O perfil é armazenado temporariamente por 5 minutos para evitar análises repetidas.</p>
                    </article>

                    <article class="mentor-tip-card">
                        <span>✦</span>
                        <div>
                            <small>DICA DO MENTOR</small>
                            <strong data-mentor-tip-title>Analisando sua próxima prioridade...</strong>
                            <p data-mentor-tip-text>As recomendações serão atualizadas com o seu perfil.</p>
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
                            <span><i></i> Tutor IA conectado ao seu perfil</span>
                        </div>
                    </div>
                    <div class="mentor-chat-actions">
                        <button type="button" class="mentor-chat-clear" data-clear-chat>Limpar conversa</button>
                        <button type="button" class="mentor-ghost-button" data-expand-chat>Expandir chat</button>
                        <button type="button" class="mentor-chat-close" data-close-chat aria-label="Fechar chat">×</button>
                    </div>
                </header>

                <div class="mentor-chat-body">
                    <div class="mentor-chat-welcome">
                        <img src="assets/brand/mentor-ai-bot.png" alt="">
                        <div>
                            <strong>Olá, ${escapeHtml(name)}! Eu sou o Mentor.Edu.</strong>
                            <p>
                                Posso explicar conteúdos passo a passo, revisar conceitos,
                                ajudar com exercícios e adaptar a resposta ao seu momento acadêmico.
                            </p>
                        </div>
                    </div>

                    <div class="mentor-chat-suggestions">
                        <button type="button" data-chat-suggestion>Explique um conteúdo passo a passo</button>
                        <button type="button" data-chat-suggestion>Monte uma revisão para mim</button>
                        <button type="button" data-chat-suggestion>Quero praticar com exercícios</button>
                    </div>

                    <div class="mentor-chat-messages" data-chat-messages aria-live="polite"></div>
                </div>

                <form class="mentor-chat-compose" data-chat-form>
                    <input
                        type="text"
                        placeholder="Pergunte qualquer coisa ao Mentor.Edu..."
                        aria-label="Mensagem para o Mentor Edu"
                        autocomplete="off"
                    >
                    <button type="submit" data-chat-submit>Enviar</button>
                </form>
            </section>

            <div class="mentor-preview-toast" data-preview-toast hidden></div>
        </section>
    `;

    const page = container.querySelector(".mentor-page");
    const chat = page.querySelector("[data-mentor-chat]");
    const chatMessages = chat.querySelector("[data-chat-messages]");
    const chatForm = chat.querySelector("[data-chat-form]");
    const chatInput = chatForm?.querySelector("input");
    const chatSubmit = chatForm?.querySelector("[data-chat-submit]");
    let chatBusy = false;
    let chatHistory = readChatHistory(user);

    renderChatHistory(chatMessages, chatHistory);

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

    async function sendTutorMessage(rawMessage) {
        const message = String(rawMessage ?? "").trim();
        if (!message || chatBusy) return;

        openChat();
        chatBusy = true;

        if (chatInput) {
            chatInput.value = "";
            chatInput.disabled = true;
        }
        if (chatSubmit) {
            chatSubmit.disabled = true;
            chatSubmit.textContent = "Pensando...";
        }

        const userMessage = {
            role: "user",
            text: message,
            at: Date.now(),
        };

        chatHistory.push(userMessage);
        chatHistory = chatHistory.slice(-CHAT_HISTORY_LIMIT);
        writeChatHistory(user, chatHistory);
        appendChatMessage(chatMessages, userMessage);

        chatMessages?.insertAdjacentHTML("beforeend", thinkingMarkup());
        if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const previousContext = recentConversationContext(chatHistory.slice(0, -1));
            const tutorMessage = previousContext
                ? `Considere este contexto recente apenas para manter a continuidade da conversa:\n${previousContext}\n\nMensagem atual do aluno:\n${message}`
                : message;

            const response = await api.post(
                "/mentor-ai/student/tutor",
                { mensagem: tutorMessage },
            );

            chatMessages?.querySelector("[data-chat-thinking]")?.remove();

            const parsed = tutorReply(response);
            const assistantMessage = {
                role: "assistant",
                text: parsed.text,
                meta: parsed.meta,
                at: Date.now(),
            };

            chatHistory.push(assistantMessage);
            chatHistory = chatHistory.slice(-CHAT_HISTORY_LIMIT);
            writeChatHistory(user, chatHistory);
            appendChatMessage(chatMessages, assistantMessage);
        } catch (error) {
            console.error("[Mentor Edu] Falha no Tutor IA:", error);
            chatMessages?.querySelector("[data-chat-thinking]")?.remove();

            const errorText =
                error?.message ||
                "Não consegui falar com o Tutor agora. Confira o backend e tente novamente.";

            appendChatMessage(chatMessages, {
                role: "error",
                text: errorText,
            });

            showToast(page, "Não foi possível obter a resposta do Tutor.");
        } finally {
            chatBusy = false;

            if (chatInput) {
                chatInput.disabled = false;
                chatInput.focus();
            }
            if (chatSubmit) {
                chatSubmit.disabled = false;
                chatSubmit.textContent = "Enviar";
            }
        }
    }

    chatForm?.addEventListener("submit", event => {
        event.preventDefault();
        sendTutorMessage(chatInput?.value);
    });

    page.querySelectorAll("[data-chat-suggestion]").forEach(button => {
        button.addEventListener("click", () => {
            openChat();
            if (chatInput) {
                chatInput.value = button.textContent.trim();
                chatInput.focus();
            }
        });
    });

    page.querySelector("[data-clear-chat]")?.addEventListener("click", () => {
        if (!chatHistory.length) {
            showToast(page, "A conversa já está vazia.");
            return;
        }

        const confirmed = window.confirm(
            "Limpar o histórico desta conversa com o Mentor Edu?"
        );
        if (!confirmed) return;

        chatHistory = [];
        clearChatHistory(user);
        renderChatHistory(chatMessages, chatHistory);
        showToast(page, "Conversa limpa.");
    });

    page.querySelector("[data-refresh-profile]")?.addEventListener("click", () => {
        ["profile", "strengths", "attention", "suggestions"].forEach(key => {
            const target = page.querySelector(`[data-profile-target="${key}"]`);
            if (target) target.innerHTML = loadingMarkup("Atualizando análise...");
        });
        loadStudentProfile(page, user, { force: true });
    });

    const onKeyDown = event => {
        if (event.key === "Escape" && chat.classList.contains("is-fullscreen")) {
            chat.classList.remove("is-fullscreen");
            document.body.classList.remove("mentor-chat-fullscreen-open");
            const expand = chat.querySelector("[data-expand-chat]");
            if (expand) expand.textContent = "Expandir chat";
        }
    };

    document.addEventListener("keydown", onKeyDown);

    const observer = new MutationObserver(() => {
        if (!document.body.contains(page)) {
            document.body.classList.remove("mentor-chat-fullscreen-open");
            document.removeEventListener("keydown", onKeyDown);
            observer.disconnect();
        }
    });

    observer.observe(container, { childList: true });

    loadStudentProfile(page, user);
}
