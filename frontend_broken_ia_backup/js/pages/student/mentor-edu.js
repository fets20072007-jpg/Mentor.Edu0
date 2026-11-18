import { api } from "../../api/client.js";

const CHAT_KEY = "mentorEdu.ai.student.page.v2";
const SETTINGS_KEY = "mentorEdu.ai.student.page.settings.v2";

function esc(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function listMarkup(items, emptyText = "Ainda não há dados suficientes.") {
    if (!Array.isArray(items) || !items.length) return `<p class="mentor-empty-copy">${esc(emptyText)}</p>`;
    return `<ul class="mentor-detail-list">${items.map(item => `<li>${esc(item)}</li>`).join("")}</ul>`;
}

function loadChat() {
    try {
        const value = JSON.parse(localStorage.getItem(CHAT_KEY) || "[]");
        return Array.isArray(value) ? value : [];
    } catch { return []; }
}

function saveChat(messages) {
    localStorage.setItem(CHAT_KEY, JSON.stringify(messages.slice(-60)));
}

function loadSettings() {
    try {
        return { floatingEnabled: true, ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}") };
    } catch { return { floatingEnabled: true }; }
}

function saveSettings(settings) {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

function profileSummary(profileData) {
    const metrics = profileData?.metricas || {};
    const profile = profileData?.perfil || "em análise";
    const average = metrics?.media_geral_percentual;
    const attendance = metrics?.frequencia?.taxa_presenca;
    const facts = [`Perfil pedagógico: ${profile}`];
    if (average !== null && average !== undefined) facts.push(`Média geral: ${Number(average).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`);
    if (attendance !== null && attendance !== undefined) facts.push(`Frequência: ${Number(attendance).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%`);
    return facts;
}

function prioritySubject(profileData) {
    const rows = profileData?.metricas?.desempenho_por_disciplina;
    if (!Array.isArray(rows)) return null;
    return [...rows]
        .filter(row => row?.media_percentual !== null && row?.media_percentual !== undefined)
        .sort((a, b) => Number(a.media_percentual) - Number(b.media_percentual))[0] || null;
}

function accordionMarkup({ id, icon, title, preview, badge = "", content = "" }) {
    const badgeMarkup = badge ? `<span class="mentor-ai-inline-badge">${esc(badge)}</span>` : "";
    return `
        <section class="mentor-ai-collapse" data-mentor-collapse="${esc(id)}">
            <button class="mentor-ai-collapse-toggle" type="button" aria-expanded="false">
                <span class="mentor-ai-collapse-title">
                    <span class="mentor-ai-collapse-icon">${icon}</span>
                    <span><strong>${esc(title)} ${badgeMarkup}</strong><small>${esc(preview)}</small></span>
                </span>
                <span class="mentor-ai-collapse-action"><span class="mentor-ai-more-label">Ver mais</span><span class="mentor-ai-chevron">⌄</span></span>
            </button>
            <div class="mentor-ai-collapse-body" hidden>${content}</div>
        </section>`;
}

function renderChatMessages(container, messages) {
    if (!messages.length) {
        container.innerHTML = `
            <div class="mentor-ai-chat-empty">
                <img src="assets/brand/mentor-ai-bot.png" alt="" class="mentor-ai-chat-avatar">
                <div><strong>Olá! Sou o Mentor Edu.</strong><p>Posso explicar conteúdos, analisar seu desempenho e estudar com você.</p></div>
            </div>
            <div class="mentor-ai-chat-quick">
                <button type="button" data-mentor-prompt="Explique um conteúdo que estou com dificuldade.">Explicar um conteúdo</button>
                <button type="button" data-mentor-prompt="Analise meu desempenho e diga onde devo focar primeiro.">Analisar meu desempenho</button>
                <button type="button" data-mentor-prompt="Monte uma sessão de estudos para hoje.">Sessão de estudos</button>
                <button type="button" data-mentor-prompt="Quero resolver um exercício passo a passo.">Resolver exercício</button>
            </div>`;
        return;
    }
    container.innerHTML = messages.map(message => `
        <div class="mentor-ai-chat-message ${message.role === "user" ? "is-user" : "is-mentor"}">
            ${message.role === "assistant" ? `<img src="assets/brand/mentor-ai-bot.png" alt="" class="mentor-ai-message-avatar">` : ""}
            <div class="mentor-ai-message-bubble">${esc(message.content)}</div>
        </div>`).join("");
    container.scrollTop = container.scrollHeight;
}

function fillProfile(container, data) {
    const analysis = data?.analise || {};
    const priority = prioritySubject(data);
    const slots = {
        profile: listMarkup(profileSummary(data), "Seu perfil ainda está sendo construído."),
        strengths: listMarkup(analysis?.pontos_fortes, "Ainda não há pontos fortes suficientes para destacar."),
        attention: listMarkup(analysis?.pontos_atencao, "Nenhum ponto de atenção importante foi identificado."),
        actions: listMarkup(analysis?.acoes_aluno, "O Mentor ainda não possui recomendações suficientes."),
    };
    Object.entries(slots).forEach(([key, html]) => {
        container.querySelector(`[data-mentor-profile-slot="${key}"]`)?.replaceChildren();
        const slot = container.querySelector(`[data-mentor-profile-slot="${key}"]`);
        if (slot) slot.innerHTML = html;
    });

    const alerts = [];
    if (priority) alerts.push(`${priority.disciplina} está entre as disciplinas que mais merecem atenção no momento.`);
    const attendance = data?.metricas?.frequencia?.taxa_presenca;
    if (attendance !== null && attendance !== undefined && Number(attendance) < 80) alerts.push(`Sua frequência está em ${Number(attendance).toLocaleString("pt-BR", { maximumFractionDigits: 1 })}%.`);
    if (!alerts.length && analysis?.pontos_atencao?.length) alerts.push(...analysis.pontos_atencao.slice(0, 2));
    const alertsSlot = container.querySelector('[data-mentor-profile-slot="alerts"]');
    if (alertsSlot) alertsSlot.innerHTML = listMarkup(alerts, "Nenhum alerta acadêmico importante no momento.");

    const summary = container.querySelector("[data-mentor-summary-text]");
    if (summary) summary.textContent = analysis?.resumo || (priority ? `Vamos priorizar ${priority.disciplina} sem perder o ritmo nas outras disciplinas.` : "Seu perfil será atualizado conforme novas informações acadêmicas forem registradas.");

    const badge = container.querySelector("[data-mentor-alert-badge]");
    if (badge) { badge.textContent = String(alerts.length); badge.hidden = alerts.length === 0; }
}

function bindCollapses(container) {
    container.querySelectorAll(".mentor-ai-collapse-toggle").forEach(button => {
        button.addEventListener("click", () => {
            const section = button.closest(".mentor-ai-collapse");
            const body = section.querySelector(".mentor-ai-collapse-body");
            const open = button.getAttribute("aria-expanded") === "true";
            button.setAttribute("aria-expanded", String(!open));
            body.hidden = open;
            section.classList.toggle("is-open", !open);
            const label = button.querySelector(".mentor-ai-more-label");
            if (label) label.textContent = open ? "Ver mais" : "Fechar";
        });
    });
}

function setChatOpen(container, open = true) {
    const card = container.querySelector("[data-mentor-chat-card]");
    const body = container.querySelector("[data-mentor-chat-body]");
    const openButton = container.querySelector("[data-mentor-chat-open]");
    card?.classList.toggle("is-open", open);
    if (body) body.hidden = !open;
    if (openButton) openButton.textContent = open ? "Fechar chat" : "Conversar com o Mentor";
}

function setChatFullscreen(container, fullscreen) {
    const card = container.querySelector("[data-mentor-chat-card]");
    if (!card) return;
    card.classList.toggle("is-fullscreen", fullscreen);
    document.body.classList.toggle("mentor-chat-fullscreen-open", fullscreen);
    const button = card.querySelector("[data-mentor-chat-expand]");
    if (button) button.textContent = fullscreen ? "Reduzir chat" : "Expandir chat";
    if (fullscreen) {
        setChatOpen(container, true);
        setTimeout(() => container.querySelector("[data-mentor-chat-input]")?.focus(), 60);
    }
}

async function sendTutorMessage(container, messages) {
    const input = container.querySelector("[data-mentor-chat-input]");
    const send = container.querySelector("[data-mentor-chat-send]");
    const message = input?.value?.trim();
    if (!message || !input || !send) return;

    messages.push({ role: "user", content: message, at: new Date().toISOString() });
    saveChat(messages);
    input.value = "";
    const messageBox = container.querySelector("[data-mentor-chat-messages]");
    renderChatMessages(messageBox, messages);
    send.disabled = true;
    input.disabled = true;

    const thinking = document.createElement("div");
    thinking.className = "mentor-ai-chat-message is-mentor mentor-ai-thinking";
    thinking.innerHTML = `<img src="assets/brand/mentor-ai-bot.png" alt="" class="mentor-ai-message-avatar"><div class="mentor-ai-message-bubble">Pensando...</div>`;
    messageBox.appendChild(thinking);
    messageBox.scrollTop = messageBox.scrollHeight;

    try {
        const result = await api.post("/mentor-ai/student/tutor", { mensagem: message });
        messages.push({ role: "assistant", content: result?.resposta || "Não consegui gerar uma resposta agora.", at: new Date().toISOString(), model: result?.model || null });
    } catch (error) {
        messages.push({ role: "assistant", content: error?.message || "Não consegui falar com a IA agora.", at: new Date().toISOString() });
    } finally {
        saveChat(messages);
        renderChatMessages(messageBox, messages);
        send.disabled = false;
        input.disabled = false;
        input.focus();
    }
}

export async function renderStudentMentorEdu(container, user, navigate) {
    const firstName = String(user?.nome || "Aluno").trim().split(/\s+/)[0] || "Aluno";
    const messages = loadChat();
    const settings = loadSettings();

    container.innerHTML = `
        <div class="mentor-ai-page">
            <header class="mentor-ai-page-head"><div><span class="mentor-ai-eyebrow">✨ Mentor Edu — Insights com IA</span><h2>Olá, ${esc(firstName)}! 👋</h2><p>Veja seus insights personalizados e escolha quando quer abrir cada detalhe.</p></div></header>

            <section class="mentor-ai-hero-card"><img src="assets/brand/mentor-ai-bot.png" alt="Ícone do Mentor Edu" class="mentor-ai-hero-bot"><div><strong>Seu resumo de aprendizado</strong><p data-mentor-summary-text>Estou analisando seus dados para personalizar suas recomendações.</p></div></section>

            <div class="mentor-ai-collapse-stack">
                ${accordionMarkup({ id:"profile", icon:"👤", title:"Seu perfil de aprendizagem", preview:"Seu estilo, ritmo e situação acadêmica.", content:'<div data-mentor-profile-slot="profile"><p class="mentor-empty-copy">Analisando seus dados...</p></div>' })}
                ${accordionMarkup({ id:"strengths", icon:"👍", title:"Pontos fortes", preview:"O que está funcionando bem nos seus estudos.", content:'<div data-mentor-profile-slot="strengths"><p class="mentor-empty-copy">Analisando seus dados...</p></div>' })}
                ${accordionMarkup({ id:"attention", icon:"🎯", title:"Pontos para melhorar", preview:"Onde vale concentrar mais esforço.", content:'<div data-mentor-profile-slot="attention"><p class="mentor-empty-copy">Analisando seus dados...</p></div>' })}
                ${accordionMarkup({ id:"suggestions", icon:"💡", title:"Sugestões do Mentor", preview:"Próximos passos recomendados para você.", content:'<div data-mentor-profile-slot="actions"><p class="mentor-empty-copy">Analisando seus dados...</p></div>' })}
                ${accordionMarkup({ id:"plan", icon:"📅", title:"Plano de estudos", preview:"Seu plano, plano indicado e sessões de estudo.", content:'<div class="mentor-ai-action-row"><button class="mentor-ai-mini-action" data-mentor-route="study-plans" type="button">Meu plano</button><button class="mentor-ai-mini-action" data-mentor-route="recommendations" type="button">Plano indicado</button><button class="mentor-ai-mini-action" data-mentor-route="study-sessions" type="button">Sessões de estudo</button></div>' })}
                ${accordionMarkup({ id:"recommendations", icon:"✨", title:"Recomendações da IA", preview:"Conteúdos e ações indicados com base no seu desempenho.", content:'<div data-mentor-profile-slot="actions"><p class="mentor-empty-copy">Analisando seus dados...</p></div>' })}
                ${accordionMarkup({ id:"alerts", icon:"🔔", title:"Alertas inteligentes", preview:"Avisos acadêmicos sem poluir sua tela inicial.", badge:"!", content:'<div data-mentor-profile-slot="alerts"><p class="mentor-empty-copy">Analisando seus dados...</p></div>' })}
                ${accordionMarkup({ id:"settings", icon:"⚙️", title:"Assistente flutuante", preview:"Controle as sugestões do Mentor enquanto navega.", content:`<label class="mentor-ai-setting-row"><span><strong>Sugestões flutuantes</strong><small>Mostrar a bolha “O que vamos fazer hoje?”</small></span><input data-mentor-floating-toggle type="checkbox" ${settings.floatingEnabled ? "checked" : ""}></label>` })}
            </div>

            <section class="mentor-ai-chat-card" data-mentor-chat-card>
                <header class="mentor-ai-chat-head"><div><strong>💬 Conversar com o Mentor</strong><p>Tire dúvidas, peça explicações e estude com acompanhamento da IA.</p></div><div class="mentor-ai-chat-head-actions"><button type="button" class="mentor-ai-chat-expand" data-mentor-chat-expand>Expandir chat</button><button type="button" class="mentor-ai-chat-open" data-mentor-chat-open>Conversar com o Mentor</button></div></header>
                <div class="mentor-ai-chat-body" data-mentor-chat-body hidden><div class="mentor-ai-chat-messages" data-mentor-chat-messages></div><form class="mentor-ai-chat-form" data-mentor-chat-form><textarea rows="1" data-mentor-chat-input placeholder="Digite sua pergunta..."></textarea><button type="submit" data-mentor-chat-send aria-label="Enviar">➤</button></form></div>
            </section>
        </div>`;

    bindCollapses(container);
    container.querySelectorAll("[data-mentor-route]").forEach(button => button.addEventListener("click", () => navigate(button.dataset.mentorRoute)));

    const messageBox = container.querySelector("[data-mentor-chat-messages]");
    renderChatMessages(messageBox, messages);

    container.addEventListener("click", event => {
        const prompt = event.target.closest("[data-mentor-prompt]");
        if (!prompt) return;
        setChatOpen(container, true);
        const input = container.querySelector("[data-mentor-chat-input]");
        if (input) { input.value = prompt.dataset.mentorPrompt; input.focus(); }
    });

    container.querySelector("[data-mentor-chat-open]")?.addEventListener("click", () => {
        const body = container.querySelector("[data-mentor-chat-body]");
        setChatOpen(container, !!body?.hidden);
    });
    container.querySelector("[data-mentor-chat-expand]")?.addEventListener("click", () => {
        const card = container.querySelector("[data-mentor-chat-card]");
        setChatFullscreen(container, !card?.classList.contains("is-fullscreen"));
    });
    container.querySelector("[data-mentor-chat-form]")?.addEventListener("submit", async event => {
        event.preventDefault();
        await sendTutorMessage(container, messages);
    });
    container.querySelector("[data-mentor-floating-toggle]")?.addEventListener("change", event => {
        const next = { ...settings, floatingEnabled: event.target.checked };
        saveSettings(next);
        document.getElementById("mentor-ai-floating")?.classList.toggle("mentor-ai-hidden", !next.floatingEnabled);
        const legacyToggle = document.getElementById("mentor-ai-floating-toggle");
        if (legacyToggle) legacyToggle.checked = next.floatingEnabled;
    });

    const escHandler = event => {
        if (event.key !== "Escape") return;
        const card = container.querySelector("[data-mentor-chat-card]");
        if (card?.classList.contains("is-fullscreen")) setChatFullscreen(container, false);
    };
    document.addEventListener("keydown", escHandler);

    try {
        const profile = await api.get("/mentor-ai/student/profile");
        fillProfile(container, profile);
    } catch (error) {
        container.querySelectorAll("[data-mentor-profile-slot]").forEach(slot => {
            slot.innerHTML = `<p class="mentor-empty-copy">${esc(error?.message || "Não foi possível carregar seus insights agora.")}</p>`;
        });
    }
}
