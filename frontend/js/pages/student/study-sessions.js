import { getStudyPushConfig, saveStudyPushSubscription, removeStudyPushSubscription } from "../../api/study-sessions.js";
import { syncStudyFocusAlert, getStudyFocusAlerts, clearStudyFocusAlert } from "../../api/study-sessions.js";
import { getMyStudySessions, createStudySession, updateStudySession, deleteStudySession } from "../../api/study-sessions.js";
import { escapeHtml } from "../../core/format.js";
import { pageHeader, surface, emptyBlock, statusPill } from "../shared/page-ui.js";
import { showToast } from "../../components/toast.js";

// MENTOR_EDU_SESSION_HANDOFF_V8
const MENTOR_SESSION_PREFILL_KEY = "mentor_edu_session_prefill_v1";

function readMentorSessionPrefill() {
    try {
        const raw = sessionStorage.getItem(
            MENTOR_SESSION_PREFILL_KEY,
        );

        if (!raw) return null;

        sessionStorage.removeItem(
            MENTOR_SESSION_PREFILL_KEY,
        );

        const data = JSON.parse(raw);
        const suggestion = String(
            data?.suggestion || "",
        ).trim();

        return suggestion
            ? { suggestion }
            : null;
    } catch {
        try {
            sessionStorage.removeItem(
                MENTOR_SESSION_PREFILL_KEY,
            );
        } catch {
            // Sem ação.
        }

        return null;
    }
}

function applyMentorSessionPrefill(container) {
    const data = readMentorSessionPrefill();

    if (!data) return;

    const form = container.querySelector(
        "[data-session-form]",
    );

    if (!form) return;

    const subject = form.elements?.materia;
    const topic = form.elements?.assunto;
    const duration = form.elements?.duracao_minutos;
    const notes = form.elements?.observacoes;

    if (topic) {
        topic.value = data.suggestion;
    }

    if (duration && !duration.value) {
        duration.value = "30";
    }

    if (notes) {
        notes.value =
            "Sessão iniciada a partir de uma sugestão do Mentor.Edu.";
    }

    form.hidden = false;

    form.scrollIntoView({
        behavior: "smooth",
        block: "center",
    });

    setTimeout(() => {
        subject?.focus();
    }, 250);

    showToast(
        "Sugestão do Mentor carregada. Informe a matéria e registre a sessão.",
        "success",
    );
}

// MENTOR_EDU_FOCUS_TIMER_V9A
const MENTOR_FOCUS_TIMER_KEY = "mentor_edu_focus_timer_v1";

function mentorFocusNow() {
    return Date.now();
}

function mentorFocusIsPageActive() {
    return (
        document.visibilityState === "visible"
        && document.hasFocus()
    );
}

function mentorFocusReadState() {
    try {
        const raw = localStorage.getItem(
            MENTOR_FOCUS_TIMER_KEY,
        );

        if (!raw) return null;

        const state = JSON.parse(raw);

        if (!state?.sessionId) {
            return null;
        }

        return state;
    } catch {
        return null;
    }
}

function mentorFocusWriteState(state) {
    try {
        localStorage.setItem(
            MENTOR_FOCUS_TIMER_KEY,
            JSON.stringify(state),
        );
    } catch {
        // O temporizador continua funcionando em memória.
    }
}

function mentorFocusClearState() {
    try {
        localStorage.removeItem(
            MENTOR_FOCUS_TIMER_KEY,
        );
    } catch {
        // Sem ação.
    }
}

function mentorFocusFormatMs(value) {
    const total = Math.max(
        0,
        Math.floor(Number(value || 0) / 1000),
    );

    const hours = Math.floor(total / 3600);
    const minutes = Math.floor(
        (total % 3600) / 60,
    );
    const seconds = total % 60;

    if (hours > 0) {
        return [
            String(hours).padStart(2, "0"),
            String(minutes).padStart(2, "0"),
            String(seconds).padStart(2, "0"),
        ].join(":");
    }

    return [
        String(minutes).padStart(2, "0"),
        String(seconds).padStart(2, "0"),
    ].join(":");
}

function mentorFocusRemainingMs(state) {
    const plannedMs =
        Number(state?.plannedMinutes || 0)
        * 60
        * 1000;

    return Math.max(
        0,
        plannedMs - Number(state?.activeMs || 0),
    );
}

function mentorFocusPlannedEnd(state) {
    return (
        Number(state?.startedAt || 0)
        + Number(state?.plannedMinutes || 0)
        * 60
        * 1000
    );
}

function mentorFocusUrgency(state) {
    const remainingMs =
        mentorFocusRemainingMs(state);

    if (remainingMs <= 0) {
        return {
            level: "concluido",
            label: "Concluído",
            score: 0,
        };
    }

    const now = mentorFocusNow();
    const plannedEnd =
        mentorFocusPlannedEnd(state);

    if (now <= plannedEnd) {
        return {
            level: "em-dia",
            label: "Em andamento",
            score: 0,
        };
    }

    const lateMinutes =
        (now - plannedEnd) / 60000;

    const remainingMinutes =
        remainingMs / 60000;

    const score = Math.max(
        lateMinutes,
        remainingMinutes,
    );

    if (score > 30) {
        return {
            level: "critico",
            label: "Urgência crítica",
            score,
        };
    }

    if (score > 15) {
        return {
            level: "alto",
            label: "Urgência alta",
            score,
        };
    }

    if (score > 5) {
        return {
            level: "medio",
            label: "Urgência média",
            score,
        };
    }

    return {
        level: "baixo",
        label: "Lembrete",
        score,
    };
}

function mentorFocusNotificationBody(
    state,
    urgency,
) {
    const remainingMinutes = Math.ceil(
        mentorFocusRemainingMs(state) / 60000,
    );

    const now = mentorFocusNow();
    const lateMinutes = Math.max(
        0,
        Math.floor(
            (
                now
                - mentorFocusPlannedEnd(state)
            ) / 60000,
        ),
    );

    if (urgency.level === "concluido") {
        return (
            `Você completou o tempo de foco de `
            + `${state.title}.`
        );
    }

    return (
        `${state.title}: ainda faltam `
        + `${remainingMinutes} min de foco. `
        + (
            lateMinutes > 0
                ? `O horário previsto terminou há ${lateMinutes} min.`
                : "Continue a sessão para cumprir o tempo planejado."
        )
    );
}

function mentorFocusCanNotify() {
    return (
        "Notification" in window
        && Notification.permission === "granted"
    );
}

async function mentorFocusRequestNotifications() {
    if (!("Notification" in window)) {
        return "unsupported";
    }

    try {
        return await Notification.requestPermission();
    } catch {
        return Notification.permission;
    }
}

function mentorFocusNotify(
    state,
    urgency,
) {
    if (!mentorFocusCanNotify()) {
        return;
    }

    const tag =
        `mentor-study-session-${state.sessionId}`;

    try {
        new Notification(
            urgency.level === "concluido"
                ? "Sessão de estudo concluída"
                : urgency.label,
            {
                body: mentorFocusNotificationBody(
                    state,
                    urgency,
                ),
                tag,
                renotify: true,
                requireInteraction:
                    urgency.level === "critico",
            },
        );
    } catch {
        // Notificação do SO é complementar.
    }
}

function mentorFocusRestoreGap(state) {
    if (!state) return state;

    const now = mentorFocusNow();
    const lastTick =
        Number(state.lastTickAt || now);

    if (
        state.status === "running"
        && now > lastTick
    ) {
        state.awayMs =
            Number(state.awayMs || 0)
            + (now - lastTick);

        state.lastTickAt = now;
        mentorFocusWriteState(state);
    }

    return state;
}

function mentorFocusSessionLabel(session) {
    return (
        `${session?.materia || "Matéria"}`
        + (
            session?.assunto
                ? ` · ${session.assunto}`
                : ""
        )
    );
}

// MENTOR_EDU_FOCUS_BACKEND_V9B1
function mentorFocusLateMinutes(state) {
    return Math.max(
        0,
        Math.floor(
            (
                mentorFocusNow()
                - mentorFocusPlannedEnd(state)
            ) / 60000,
        ),
    );
}

function mentorFocusBackendPayload(state) {
    return {
        session_id: Number(state?.sessionId || 0),
        title: String(
            state?.title || "Sessão de estudo",
        ),
        planned_minutes: Number(
            state?.plannedMinutes || 0,
        ),
        active_ms: Math.floor(
            Number(state?.activeMs || 0),
        ),
        away_ms: Math.floor(
            Number(state?.awayMs || 0),
        ),
        remaining_minutes: Math.ceil(
            mentorFocusRemainingMs(state) / 60000,
        ),
        late_minutes: mentorFocusLateMinutes(state),
    };
}

async function mentorFocusSyncBackend(state) {
    if (!state?.sessionId) return null;

    try {
        return await syncStudyFocusAlert(
            mentorFocusBackendPayload(state),
        );
    } catch (error) {
        console.warn(
            "[Mentor Edu] Falha ao sincronizar alerta de foco:",
            error,
        );
        return null;
    }
}

async function mentorFocusClearBackend(sessionId) {
    if (!sessionId) return;

    try {
        await clearStudyFocusAlert(sessionId);
    } catch (error) {
        console.warn(
            "[Mentor Edu] Falha ao limpar alerta de foco:",
            error,
        );
    }
}

function mentorFocusServerLabel(level) {
    if (level === "critico") return "CRÍTICO";
    if (level === "alto") return "ALTO";
    if (level === "medio") return "MÉDIO";
    return "LEMBRETE";
}

function mentorFocusBackendAlertMarkup(item) {
    const allowed = [
        "baixo",
        "medio",
        "alto",
        "critico",
    ];

    const level = allowed.includes(item?.level)
        ? item.level
        : "baixo";

    return `
        <article
            class="mentor-focus-server-alert is-${level}"
        >
            <span>
                ${mentorFocusServerLabel(level)}
            </span>

            <div>
                <strong>
                    ${escapeHtml(
                        item?.title || "Sessão pendente",
                    )}
                </strong>

                <p>
                    ${escapeHtml(
                        item?.message
                        || "Há tempo de foco pendente.",
                    )}
                </p>
            </div>
        </article>
    `;
}

async function mentorFocusLoadBackendAlerts(shell) {
    const target = shell?.querySelector(
        "[data-focus-server-alerts]",
    );

    if (!target) return;

    try {
        const data = await getStudyFocusAlerts();

        const items =
            Array.isArray(data?.alertas)
                ? data.alertas
                : [];

        if (!items.length) {
            target.hidden = true;
            target.innerHTML = "";
            return;
        }

        target.hidden = false;
        target.innerHTML = `
            <div class="mentor-focus-server-title">
                <strong>Pendências sincronizadas</strong>
                <span>${items.length}</span>
            </div>

            <div class="mentor-focus-server-list">
                ${items
                    .map(mentorFocusBackendAlertMarkup)
                    .join("")}
            </div>
        `;
    } catch (error) {
        console.warn(
            "[Mentor Edu] Falha ao carregar alertas persistentes:",
            error,
        );
    }
}

// MENTOR_EDU_WEB_PUSH_V9B2
function mentorPushBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, "+")
        .replace(/_/g, "/");
    const rawData = window.atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

async function mentorPushCurrentSubscription() {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
        return null;
    }
    try {
        const registration = await navigator.serviceWorker.ready;
        return await registration.pushManager.getSubscription();
    } catch {
        return null;
    }
}

async function mentorPushEnable() {
    if (
        !("serviceWorker" in navigator)
        || !("PushManager" in window)
        || !("Notification" in window)
    ) {
        throw new Error("Este navegador não oferece Web Push.");
    }

    const config = await getStudyPushConfig();
    if (!config?.enabled || !config?.public_key) {
        throw new Error("Web Push ainda não está configurado no servidor.");
    }

    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
        throw new Error("Permissão de notificações não concedida.");
    }

    const registration = await navigator.serviceWorker.ready;
    let subscription = await registration.pushManager.getSubscription();

    if (!subscription) {
        subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: mentorPushBase64ToUint8Array(config.public_key),
        });
    }

    const payload = subscription.toJSON();
    payload.device_label = (navigator.userAgent || "Navegador").slice(0, 180);
    await saveStudyPushSubscription(payload);
    return subscription;
}

async function mentorPushDisable() {
    const subscription = await mentorPushCurrentSubscription();
    if (!subscription) return;
    try {
        await removeStudyPushSubscription(subscription.endpoint);
    } finally {
        await subscription.unsubscribe();
    }
}

async function mentorPushRefreshButton(button) {
    if (!button) return;
    const subscription = await mentorPushCurrentSubscription();
    if (subscription) {
        button.textContent = "Push em segundo plano ativo";
        button.dataset.pushEnabled = "true";
    } else {
        button.textContent = "Ativar push em segundo plano";
        button.dataset.pushEnabled = "false";
    }
}

// MENTOR_EDU_SESSION_MENTOR_HELP_V9C
const MENTOR_SESSION_HELP_KEY =
    "mentor_edu_session_help_context_v1";

function mentorSessionHelpSelected(
    container,
    current,
) {
    const items = Array.isArray(current)
        ? current
        : [];

    const timerState =
        typeof mentorFocusReadState === "function"
            ? mentorFocusReadState()
            : null;

    if (timerState?.sessionId) {
        const active = items.find(
            item =>
                Number(item?.id)
                === Number(timerState.sessionId),
        );

        if (active) {
            return {
                session: active,
                timerState,
            };
        }
    }

    const select = container.querySelector(
        "[data-focus-session]",
    );

    const selectedId = Number(
        select?.value || 0,
    );

    if (selectedId) {
        const selected = items.find(
            item =>
                Number(item?.id)
                === selectedId,
        );

        if (selected) {
            return {
                session: selected,
                timerState: null,
            };
        }
    }

    const pending = items.find(
        item => !item?.concluida,
    );

    if (pending) {
        return {
            session: pending,
            timerState: null,
        };
    }

    return null;
}

function mentorSessionHelpContext(
    container,
    current,
) {
    const selected =
        mentorSessionHelpSelected(
            container,
            current,
        );

    if (!selected?.session) {
        return null;
    }

    const session = selected.session;
    const timer = selected.timerState;

    const plannedMinutes = Number(
        session?.duracao_minutos
        ?? timer?.plannedMinutes
        ?? 0,
    );

    const activeMs = Number(
        timer?.activeMs
        ?? 0,
    );

    const awayMs = Number(
        timer?.awayMs
        ?? 0,
    );

    const remainingMs =
        timer
        && typeof mentorFocusRemainingMs === "function"
            ? mentorFocusRemainingMs(timer)
            : Math.max(
                0,
                plannedMinutes
                * 60
                * 1000
                - activeMs,
            );

    return {
        source: "study-sessions",
        createdAt: Date.now(),

        session_id:
            Number(session?.id || 0),

        materia:
            String(
                session?.materia
                || "Não informada",
            ).trim(),

        assunto:
            String(
                session?.assunto
                || "Não informado",
            ).trim(),

        duracao_minutos:
            plannedMinutes,

        dificuldade:
            session?.dificuldade
            ?? session?.nivel_dificuldade
            ?? null,

        observacoes:
            String(
                session?.observacoes
                || "",
            ).trim(),

        concluida:
            Boolean(session?.concluida),

        timer_status:
            String(
                timer?.status
                || "não iniciado",
            ),

        foco_computado_minutos:
            Math.floor(
                activeMs / 60000,
            ),

        tempo_fora_minutos:
            Math.floor(
                awayMs / 60000,
            ),

        tempo_pendente_minutos:
            Math.ceil(
                remainingMs / 60000,
            ),
    };
}

function mentorSessionHelpMarkup() {
    return `
        <div
            class="mentor-session-help-cta"
            data-mentor-session-help-wrap
        >
            <button
                type="button"
                class="mentor-session-help-button"
                data-mentor-session-help
            >
                <span aria-hidden="true">✦</span>
                <span>
                    Pedir ajuda ao Mentor para esta sessão
                </span>
            </button>

            <p>
                O Mentor usará disciplina, conteúdo,
                dificuldade e tempo disponível para orientar seu estudo.
            </p>
        </div>
    `;
}

function bindMentorSessionHelp(
    container,
    current,
) {
    let wrap = container.querySelector(
        "[data-mentor-session-help-wrap]",
    );

    if (!wrap) {
        container.insertAdjacentHTML(
            "beforeend",
            mentorSessionHelpMarkup(),
        );

        wrap = container.querySelector(
            "[data-mentor-session-help-wrap]",
        );
    }

    const button = wrap?.querySelector(
        "[data-mentor-session-help]",
    );

    if (!button) return;

    const selected =
        mentorSessionHelpSelected(
            container,
            current,
        );

    button.disabled = !selected;

    if (!selected) {
        button.title =
            "Crie uma sessão pendente para pedir orientação ao Mentor.";
    } else {
        button.title =
            "Abrir o Mentor já com o contexto desta sessão.";
    }

    button.addEventListener(
        "click",
        () => {
            const context =
                mentorSessionHelpContext(
                    container,
                    current,
                );

            if (!context) {
                showToast(
                    "Selecione ou crie uma sessão antes de pedir ajuda ao Mentor.",
                    "error",
                );
                return;
            }

            try {
                sessionStorage.setItem(
                    MENTOR_SESSION_HELP_KEY,
                    JSON.stringify(context),
                );
            } catch {
                showToast(
                    "Não foi possível preparar o contexto da sessão.",
                    "error",
                );
                return;
            }

            location.hash =
                "#/mentor-edu";
        },
    );
}

function mentorFocusTimerPanel(current) {
    const pending = (current || [])
        .filter(item => !item?.concluida);

    const state = mentorFocusRestoreGap(
        mentorFocusReadState(),
    );

    if (!pending.length && !state) {
        return `
            <section class="mentor-focus-shell">
                <div class="mentor-focus-title">
                    <div>
                        <span>FOCO</span>
                        <strong>Temporizador de estudo</strong>
                        <p>Registre uma sessão pendente para iniciar o acompanhamento.</p>
                    </div>
                </div>
            </section>
        `;
    }

    const selectedId =
        Number(state?.sessionId || pending[0]?.id || 0);

    const options = pending
        .map(session => `
            <option
                value="${session.id}"
                ${
                    Number(session.id) === selectedId
                        ? "selected"
                        : ""
                }
            >
                ${escapeHtml(mentorFocusSessionLabel(session))}
                · ${escapeHtml(session.duracao_minutos)} min
            </option>
        `)
        .join("");

    const hasTimer = Boolean(state);
    const remainingMs =
        hasTimer
            ? mentorFocusRemainingMs(state)
            : 0;

    const urgency =
        hasTimer
            ? mentorFocusUrgency(state)
            : {
                level: "em-dia",
                label: "Pronto",
            };

    return `
        <section
            class="mentor-focus-shell is-${escapeHtml(urgency.level)}"
            data-focus-shell
        >
            <div class="mentor-focus-title">
                <div>
                    <span>FOCO</span>
                    <strong>Temporizador de estudo</strong>
                    <p>
                        O Mentor conta apenas o tempo em que esta página está ativa.
                        Se você sair da aba, o período fica registrado como tempo fora.
                    </p>
                </div>

                <span
                    class="mentor-focus-urgency"
                    data-focus-urgency
                >
                    ${escapeHtml(urgency.label)}
                </span>
            </div>

            <div class="mentor-focus-picker">
                <label>
                    Sessão
                    <select
                        data-focus-session
                        ${hasTimer ? "disabled" : ""}
                    >
                        ${options}
                    </select>
                </label>

                <button
                    type="button"
                    class="mini-button mini-button--primary"
                    data-focus-start
                    ${hasTimer ? "hidden" : ""}
                >
                    Iniciar foco
                </button>

                <button
                    type="button"
                    class="mini-button"
                    data-focus-pause
                    ${hasTimer ? "" : "hidden"}
                >
                    ${
                        state?.status === "paused"
                            ? "Retomar"
                            : "Pausar"
                    }
                </button>

                <button
                    type="button"
                    class="mini-button mini-button--danger"
                    data-focus-stop
                    ${hasTimer ? "" : "hidden"}
                >
                    Encerrar
                </button>

                <button
                    type="button"
                    class="mini-button"
                    data-focus-notifications
                >
                    ${
                        mentorFocusCanNotify()
                            ? "Notificações ativas"
                            : "Ativar notificações"
                    }
                </button>

                <button
                    type="button"
                    class="mini-button"
                    data-focus-push
                >
                    Ativar push em segundo plano
                </button>
            </div>

            <div class="mentor-focus-clock">
                <div>
                    <span>Tempo pendente</span>
                    <strong data-focus-remaining>
                        ${
                            hasTimer
                                ? mentorFocusFormatMs(remainingMs)
                                : "--:--"
                        }
                    </strong>
                </div>

                <div>
                    <span>Foco computado</span>
                    <strong data-focus-active>
                        ${
                            hasTimer
                                ? mentorFocusFormatMs(state.activeMs)
                                : "00:00"
                        }
                    </strong>
                </div>

                <div>
                    <span>Tempo fora da aba</span>
                    <strong data-focus-away>
                        ${
                            hasTimer
                                ? mentorFocusFormatMs(state.awayMs)
                                : "00:00"
                        }
                    </strong>
                </div>
            </div>

            <div
                class="mentor-focus-message"
                data-focus-message
            ></div>
        </section>
    `;
}

function bindFocusTimer(
    container,
    current,
) {
    const shell = container.querySelector(
        "[data-focus-shell]",
    );

    if (!shell) return;

    const select = shell.querySelector(
        "[data-focus-session]",
    );

    const startButton = shell.querySelector(
        "[data-focus-start]",
    );

    const pauseButton = shell.querySelector(
        "[data-focus-pause]",
    );

    const stopButton = shell.querySelector(
        "[data-focus-stop]",
    );

    const notificationButton = shell.querySelector(
        "[data-focus-notifications]",
    );

    const pushButton = shell.querySelector(
        "[data-focus-push]",
    );

    mentorPushRefreshButton(pushButton);

    pushButton?.addEventListener(
        "click",
        async () => {
            pushButton.disabled = true;
            try {
                const currentPush = await mentorPushCurrentSubscription();
                if (currentPush) {
                    const confirmDisable = window.confirm(
                        "Desativar os lembretes push neste dispositivo?"
                    );
                    if (confirmDisable) {
                        await mentorPushDisable();
                        showToast("Push desativado neste dispositivo.");
                    }
                } else {
                    await mentorPushEnable();
                    showToast("Push em segundo plano ativado.", "success");
                }
            } catch (error) {
                showToast(
                    error?.message || "Não foi possível configurar o push.",
                    "error",
                );
            } finally {
                pushButton.disabled = false;
                mentorPushRefreshButton(pushButton);
            }
        },
    );

    const remaining = shell.querySelector(
        "[data-focus-remaining]",
    );

    const active = shell.querySelector(
        "[data-focus-active]",
    );

    const away = shell.querySelector(
        "[data-focus-away]",
    );

    const urgencyNode = shell.querySelector(
        "[data-focus-urgency]",
    );

    const message = shell.querySelector(
        "[data-focus-message]",
    );

    let state = mentorFocusRestoreGap(
        mentorFocusReadState(),
    );

    let intervalId = null;

    const sessionForState = () => {
        if (!state) return null;

        return (current || []).find(
            item =>
                Number(item.id)
                === Number(state.sessionId),
        ) || null;
    };

    const syncState = () => {
        if (!state) return;

        const now = mentorFocusNow();
        const lastTick =
            Number(state.lastTickAt || now);

        const delta = Math.max(
            0,
            Math.min(
                now - lastTick,
                60 * 1000,
            ),
        );

        if (state.status === "running") {
            if (mentorFocusIsPageActive()) {
                state.activeMs =
                    Number(state.activeMs || 0)
                    + delta;
            } else {
                state.awayMs =
                    Number(state.awayMs || 0)
                    + delta;
            }
        } else if (
            state.status === "paused"
            && now > lastTick
        ) {
            state.awayMs =
                Number(state.awayMs || 0)
                + delta;
        }

        state.lastTickAt = now;
    };

    const renderState = () => {
        if (!state) return;

        const pendingMs =
            mentorFocusRemainingMs(state);

        const urgency =
            mentorFocusUrgency(state);

        if (remaining) {
            remaining.textContent =
                mentorFocusFormatMs(pendingMs);
        }

        if (active) {
            active.textContent =
                mentorFocusFormatMs(state.activeMs);
        }

        if (away) {
            away.textContent =
                mentorFocusFormatMs(state.awayMs);
        }

        if (urgencyNode) {
            urgencyNode.textContent =
                urgency.label;
        }

        shell.className =
            `mentor-focus-shell is-${urgency.level}`;

        if (
            urgency.level !== "em-dia"
            && urgency.level !== state.lastUrgency
        ) {
            mentorFocusNotify(
                state,
                urgency,
            );

            state.lastUrgency =
                urgency.level;
        }

        if (message) {
            if (urgency.level === "concluido") {
                message.innerHTML = `
                    <strong>Tempo de foco cumprido.</strong>
                    <span>
                        Agora você pode marcar a sessão como concluída na lista abaixo.
                    </span>
                `;
            } else if (
                ["baixo", "medio", "alto", "critico"]
                    .includes(urgency.level)
            ) {
                const lateMinutes = Math.max(
                    0,
                    Math.floor(
                        (
                            mentorFocusNow()
                            - mentorFocusPlannedEnd(state)
                        ) / 60000,
                    ),
                );

                const pendingMinutes = Math.ceil(
                    pendingMs / 60000,
                );

                message.innerHTML = `
                    <strong>
                        ${escapeHtml(urgency.label)}
                    </strong>
                    <span>
                        Horário previsto encerrado há
                        ${lateMinutes} min.
                        Ainda faltam
                        ${pendingMinutes} min
                        de foco ativo.
                    </span>
                `;
            } else {
                message.innerHTML = `
                    <strong>Sessão em andamento.</strong>
                    <span>
                        O tempo só conta como foco enquanto o Mentor.Edu estiver ativo na tela.
                    </span>
                `;
            }
        }

        const backendNow = mentorFocusNow();

        const shouldSyncBackend = (
            backendNow
            - Number(state.lastBackendSyncAt || 0)
            >= 30000
        ) || (
            urgency.level
            !== state.lastBackendLevel
        );

        if (shouldSyncBackend) {
            state.lastBackendSyncAt = backendNow;
            state.lastBackendLevel = urgency.level;

            mentorFocusSyncBackend(state).then(() => {
                mentorFocusLoadBackendAlerts(shell);
            });
        }

        mentorFocusWriteState(state);
    };

    const tick = () => {
        if (!state) return;

        syncState();
        renderState();
    };

    const startInterval = () => {
        if (intervalId) {
            clearInterval(intervalId);
        }

        intervalId = setInterval(
            tick,
            1000,
        );
    };

    startButton?.addEventListener(
        "click",
        () => {
            const id = Number(
                select?.value || 0,
            );

            const session = (current || []).find(
                item =>
                    Number(item.id) === id,
            );

            if (!session) {
                showToast(
                    "Selecione uma sessão pendente.",
                    "error",
                );
                return;
            }

            const now = mentorFocusNow();

            state = {
                sessionId: Number(session.id),
                title: mentorFocusSessionLabel(session),
                plannedMinutes: Math.max(
                    1,
                    Number(session.duracao_minutos || 30),
                ),
                startedAt: now,
                lastTickAt: now,
                activeMs: 0,
                awayMs: 0,
                status: "running",
                lastUrgency: "em-dia",
            };

            mentorFocusWriteState(state);

            showToast(
                "Temporizador iniciado.",
                "success",
            );

            const renderCurrent =
                container.querySelector(
                    "[data-focus-shell]",
                );

            if (renderCurrent) {
                // A renderização completa ocorrerá no próximo carregamento.
                location.reload();
            }
        },
    );

    pauseButton?.addEventListener(
        "click",
        () => {
            if (!state) return;

            syncState();

            if (state.status === "paused") {
                state.status = "running";
                state.lastTickAt =
                    mentorFocusNow();

                pauseButton.textContent =
                    "Pausar";
            } else {
                state.status = "paused";
                state.lastTickAt =
                    mentorFocusNow();

                pauseButton.textContent =
                    "Retomar";
            }

            mentorFocusWriteState(state);
            renderState();
        },
    );

    stopButton?.addEventListener(
        "click",
        () => {
            if (!state) return;

            const ok = window.confirm(
                "Encerrar este temporizador de foco?"
            );

            if (!ok) return;

                        const closingSessionId = state.sessionId;
            mentorFocusClearBackend(closingSessionId).then(() => {
                mentorFocusLoadBackendAlerts(shell);
            });

mentorFocusClearState();
            state = null;

            if (intervalId) {
                clearInterval(intervalId);
            }

            showToast(
                "Temporizador encerrado.",
            );

            location.reload();
        },
    );

    notificationButton?.addEventListener(
        "click",
        async () => {
            const permission =
                await mentorFocusRequestNotifications();

            if (permission === "granted") {
                notificationButton.textContent =
                    "Notificações ativas";

                showToast(
                    "Notificações do temporizador ativadas.",
                    "success",
                );
            } else if (
                permission === "unsupported"
            ) {
                showToast(
                    "Este navegador não oferece notificações deste tipo.",
                    "error",
                );
            } else {
                showToast(
                    "Permissão de notificações não concedida.",
                    "error",
                );
            }
        },
    );

    if (state) {
        const currentSession =
            sessionForState();

        if (
            currentSession?.concluida
        ) {
            mentorFocusClearState();
            state = null;
            return;
        }

        renderState();
        startInterval();
    }

    const onVisibility = () => {
        if (!state) return;

        syncState();
        mentorFocusWriteState(state);
    };

    document.addEventListener(
        "visibilitychange",
        onVisibility,
    );

    window.addEventListener(
        "blur",
        onVisibility,
    );

    window.addEventListener(
        "focus",
        onVisibility,
    );

    window.addEventListener(
        "beforeunload",
        onVisibility,
        {
            once: true,
        },
    );
}

function sessionForm() {
    return `<form class="inline-form" data-session-form hidden><div class="form-grid"><label>Matéria<input name="materia" required></label><label>Assunto<input name="assunto" required></label><label>Duração (min)<input name="duracao_minutos" type="number" min="1" required value="30"></label><label>Dificuldade sentida<select name="dificuldade_sentida"><option value="">Não informar</option><option value="1">1 - Muito baixa</option><option value="2">2</option><option value="3">3 - Média</option><option value="4">4</option><option value="5">5 - Muito alta</option></select></label><label>Data<input name="data_sessao" type="date"></label><label class="form-span-2">Observações<textarea name="observacoes" rows="3"></textarea></label></div><div class="form-actions"><button class="mini-button" type="button" data-cancel-session>Cancelar</button><button class="mini-button mini-button--primary" type="submit">Registrar sessão</button></div></form>`;
}

// MENTOR_EDU_SESSION_REFLECTION_V10A_V2
function mentor10ReflectionTimerData(session) {
    let state = null;

    try {
        if (
            typeof mentorFocusReadState
            === "function"
        ) {
            state = mentorFocusReadState();
        }
    } catch {
        state = null;
    }

    if (
        !state
        || Number(state.sessionId)
            !== Number(session?.id)
    ) {
        return {
            foco_minutos: 0,
            tempo_fora_minutos: 0,
        };
    }

    return {
        foco_minutos: Math.floor(
            Number(state.activeMs || 0)
            / 60000,
        ),

        tempo_fora_minutos: Math.floor(
            Number(state.awayMs || 0)
            / 60000,
        ),
    };
}


async function mentor10SaveReflection(payload) {
    const module = await import(
        "../../api/study-sessions.js"
    );

    return module.saveStudySessionReflectionV10A(
        payload,
    );
}


function mentor10ReflectionMarkup(session) {
    const initialDifficulty = Number(
        session?.dificuldade_sentida
        ?? session?.dificuldade
        ?? 0,
    );

    return `
        <div
            class="mentor10-reflection-backdrop"
            data-mentor10-reflection
        >
            <section
                class="mentor10-reflection-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="mentor10-reflection-title"
            >
                <header class="mentor10-reflection-head">
                    <div>
                        <span>FECHAMENTO DA SESSÃO</span>

                        <h3 id="mentor10-reflection-title">
                            Como foi seu estudo?
                        </h3>

                        <p>
                            ${escapeHtml(
                                session?.materia
                                || "Sessão"
                            )}
                            ${session?.assunto
                                ? ` · ${escapeHtml(session.assunto)}`
                                : ""
                            }
                        </p>
                    </div>

                    <button
                        type="button"
                        data-mentor10-close
                        aria-label="Fechar"
                    >
                        ×
                    </button>
                </header>

                <form
                    class="mentor10-reflection-form"
                    data-mentor10-form
                >
                    <div class="mentor10-reflection-grid">
                        <label>
                            Dificuldade antes

                            <input
                                type="text"
                                value="${
                                    initialDifficulty
                                    ? `${initialDifficulty}/5`
                                    : "Não informada"
                                }"
                                disabled
                            >
                        </label>

                        <label>
                            Dificuldade agora

                            <select
                                name="dificuldade_final"
                                required
                            >
                                <option value="">
                                    Selecione
                                </option>
                                <option value="1">1 - Muito baixa</option>
                                <option value="2">2 - Baixa</option>
                                <option value="3">3 - Média</option>
                                <option value="4">4 - Alta</option>
                                <option value="5">5 - Muito alta</option>
                            </select>
                        </label>

                        <label>
                            Quanto você entendeu?

                            <select
                                name="compreensao_final"
                                required
                            >
                                <option value="">
                                    Selecione
                                </option>
                                <option value="1">1 - Muito pouco</option>
                                <option value="2">2 - Pouco</option>
                                <option value="3">3 - Razoavelmente</option>
                                <option value="4">4 - Bem</option>
                                <option value="5">5 - Muito bem</option>
                            </select>
                        </label>

                        <label>
                            Objetivo da sessão

                            <select
                                name="objetivo_status"
                                required
                            >
                                <option value="cumprido">
                                    Cumpri
                                </option>
                                <option
                                    value="parcial"
                                    selected
                                >
                                    Cumpri parcialmente
                                </option>
                                <option value="nao_cumprido">
                                    Não cumpri
                                </option>
                            </select>
                        </label>

                        <label class="mentor10-reflection-wide">
                            O que ainda ficou difícil?

                            <textarea
                                name="dificuldade_restante"
                                rows="3"
                                placeholder="Opcional. Ex.: ainda confundo os conceitos principais."
                            ></textarea>
                        </label>
                    </div>

                    <div class="mentor10-reflection-note">
                        <strong>
                            Seu fechamento ajudará o Mentor
                            a adaptar os próximos estudos.
                        </strong>
                        <span>
                            A próxima parte da Etapa 10
                            fará uma checagem curta do conteúdo.
                        </span>
                    </div>

                    <footer class="mentor10-reflection-actions">
                        <button
                            type="button"
                            class="mini-button"
                            data-mentor10-cancel
                        >
                            Voltar
                        </button>

                        <button
                            type="submit"
                            class="mini-button mini-button--primary"
                        >
                            Salvar e concluir
                        </button>
                    </footer>
                </form>
            </section>
        </div>
    `;
}


function mentor10CloseReflection(container) {
    container
        .querySelector(
            "[data-mentor10-reflection]"
        )
        ?.remove();
}


function mentor10OpenReflection(
    container,
    session,
    current,
    render,
) {
    mentor10CloseReflection(container);

    container.insertAdjacentHTML(
        "beforeend",
        mentor10ReflectionMarkup(session),
    );

    const modal = container.querySelector(
        "[data-mentor10-reflection]"
    );

    const form = modal?.querySelector(
        "[data-mentor10-form]"
    );

    const close = () => {
        mentor10CloseReflection(container);
    };

    modal
        ?.querySelector("[data-mentor10-close]")
        ?.addEventListener(
            "click",
            close,
        );

    modal
        ?.querySelector("[data-mentor10-cancel]")
        ?.addEventListener(
            "click",
            close,
        );

    modal?.addEventListener(
        "click",
        event => {
            if (event.target === modal) {
                close();
            }
        },
    );

    form?.addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            const submit = form.querySelector(
                'button[type="submit"]'
            );

            if (submit) {
                submit.disabled = true;
            }

            const data = new FormData(form);

            const timer = mentor10ReflectionTimerData(
                session,
            );

            const payload = {
                session_id: Number(session.id),

                materia: String(
                    session.materia
                    || ""
                ),

                assunto: String(
                    session.assunto
                    || ""
                ),

                dificuldade_inicial: Number(
                    session.dificuldade_sentida
                    ?? session.dificuldade
                    ?? 0
                ) || null,

                dificuldade_final: Number(
                    data.get("dificuldade_final")
                ),

                compreensao_final: Number(
                    data.get("compreensao_final")
                ),

                objetivo_status: String(
                    data.get("objetivo_status")
                    || "parcial"
                ),

                dificuldade_restante: String(
                    data.get("dificuldade_restante")
                    || ""
                ).trim() || null,

                duracao_planejada: Number(
                    session.duracao_minutos
                    || 0
                ),

                foco_minutos: timer.foco_minutos,

                tempo_fora_minutos:
                    timer.tempo_fora_minutos,
            };

            try {
                await mentor10SaveReflection(
                    payload,
                );

                const saved = await updateStudySession(
                    Number(session.id),
                    {
                        concluida: true,
                    },
                );

                try {
                    const state =
                        typeof mentorFocusReadState
                        === "function"
                            ? mentorFocusReadState()
                            : null;

                    if (
                        state
                        && Number(state.sessionId)
                            === Number(session.id)
                    ) {
                        if (
                            typeof mentorFocusClearState
                            === "function"
                        ) {
                            mentorFocusClearState();
                        }

                        if (
                            typeof mentorFocusClearBackend
                            === "function"
                        ) {
                            mentorFocusClearBackend(
                                session.id
                            );
                        }
                    }
                } catch {
                    // Não impede o fechamento.
                }

                const next = current.map(
                    item =>
                        Number(item.id)
                        === Number(session.id)
                            ? saved
                            : item,
                );

                showToast(
                    "Sessão concluída e aprendizado registrado.",
                    "success",
                );

                close();
                render(next);

                mentor10BOpenOffer(
                    container,
                    session,
                    reflectionPayload
                );

            } catch (error) {
                if (submit) {
                    submit.disabled = false;
                }

                showToast(
                    error?.message
                    || "Não foi possível concluir a sessão.",
                    "error",
                );
            }
        },
    );
}


function bindMentor10Reflection(
    container,
    current,
    render,
) {
    container.__mentor10Current = current;
    container.__mentor10Render = render;

    if (container.__mentor10CaptureInstalled) {
        return;
    }

    container.__mentor10CaptureInstalled = true;

    container.addEventListener(
        "click",
        event => {
            const button = event.target.closest(
                "[data-toggle-session]"
            );

            if (
                !button
                || !container.contains(button)
            ) {
                return;
            }

            const id = Number(
                button.dataset.toggleSession
                || 0
            );

            const list = Array.isArray(
                container.__mentor10Current
            )
                ? container.__mentor10Current
                : [];

            const session = list.find(
                item =>
                    Number(item.id) === id
            );

            if (
                !session
                || session.concluida
            ) {
                return;
            }

            // Intercepta somente "Concluir".
            // "Reabrir" continua com o fluxo original.
            event.preventDefault();
            event.stopPropagation();

            if (
                typeof event.stopImmediatePropagation
                === "function"
            ) {
                event.stopImmediatePropagation();
            }

            mentor10OpenReflection(
                container,
                session,
                list,
                container.__mentor10Render,
            );
        },
        true,
    );
}

// MENTOR_EDU_SESSION_CHECK_V10B
async function mentor10BApi() {
  return import("../../api/study-sessions.js");
}

function mentor10BClose(container) {
  container.querySelector("[data-mentor10b-modal]")?.remove();
}

function mentor10BOfferMarkup(session) {
  return `
    <div class="mentor10b-backdrop" data-mentor10b-modal>
      <section class="mentor10b-modal mentor10b-offer" role="dialog" aria-modal="true">
        <div class="mentor10b-icon">✦</div>
        <span class="mentor10b-kicker">MENTOR</span>
        <h3>Verificação rápida?</h3>
        <p>Sua sessão foi concluída. O Mentor pode conferir agora se o conteúdo realmente ficou claro.</p>
        <div class="mentor10b-session">
          <strong>${escapeHtml(session?.materia || "Sessão")}</strong>
          <span>${escapeHtml(session?.assunto || "Conteúdo estudado")}</span>
        </div>
        <div class="mentor10b-meta"><span>2 questões</span><span>≈ 2 minutos</span><span>Resultado salvo</span></div>
        <div class="mentor10b-actions">
          <button type="button" class="mini-button" data-mentor10b-skip>Agora não</button>
          <button type="button" class="mini-button mini-button--primary" data-mentor10b-start>Verificar aprendizado</button>
        </div>
      </section>
    </div>
  `;
}

function mentor10BQuestionsMarkup(session, questions) {
  return `
    <div class="mentor10b-backdrop" data-mentor10b-modal>
      <section class="mentor10b-modal" role="dialog" aria-modal="true">
        <header class="mentor10b-head">
          <div>
            <span>VERIFICAÇÃO DO MENTOR</span>
            <h3>${escapeHtml(session?.materia || "Sessão")} · ${escapeHtml(session?.assunto || "Conteúdo")}</h3>
            <p>Duas perguntas rápidas sobre o que você acabou de estudar.</p>
          </div>
          <div class="mentor10b-progress">2 questões</div>
        </header>
        <form class="mentor10b-form" data-mentor10b-form>
          ${questions.map((q, i) => `
            <article class="mentor10b-question">
              <div class="mentor10b-number">${String(i + 1).padStart(2, "0")}</div>
              <div class="mentor10b-question-body">
                <h4>${escapeHtml(q.enunciado)}</h4>
                <div class="mentor10b-options">
                  ${Object.entries(q.alternativas).map(([letter, value]) => `
                    <label>
                      <input type="radio" name="q_${q.id}" value="${escapeHtml(letter)}" required>
                      <span class="mentor10b-letter">${escapeHtml(letter)}</span>
                      <span>${escapeHtml(value)}</span>
                    </label>
                  `).join("")}
                </div>
              </div>
            </article>
          `).join("")}
          <div class="mentor10b-actions">
            <button type="button" class="mini-button" data-mentor10b-close>Fazer depois</button>
            <button type="submit" class="mini-button mini-button--primary">Conferir respostas</button>
          </div>
        </form>
      </section>
    </div>
  `;
}

function mentor10BResultMarkup(result) {
  const score = Number(result?.score || 0);
  const total = Number(result?.total || 2);
  const details = Array.isArray(result?.details) ? result.details : [];
  const title = score === total
    ? "Conteúdo bem compreendido"
    : score > 0
      ? "Bom resultado, com um ponto a revisar"
      : "Vamos reforçar um pouco";

  return `
    <div class="mentor10b-backdrop" data-mentor10b-modal>
      <section class="mentor10b-modal mentor10b-result" role="dialog" aria-modal="true">
        <span class="mentor10b-kicker">RESULTADO</span>
        <div class="mentor10b-score">${score}/${total}</div>
        <h3>${escapeHtml(title)}</h3>
        <p>${escapeHtml(result?.feedback || "")}</p>
        <div class="mentor10b-result-list">
          ${details.map((detail, i) => `
            <div class="mentor10b-result-item ${detail.correta ? "is-correct" : "is-wrong"}">
              <strong>Questão ${i + 1} · ${detail.correta ? "Correta" : "Revisar"}</strong>
              ${detail.correta ? "" : `<span>Resposta correta: ${escapeHtml(detail.resposta_correta || "")}</span>`}
              ${detail.explicacao ? `<small>${escapeHtml(detail.explicacao)}</small>` : ""}
            </div>
          `).join("")}
        </div>
        <div class="mentor10b-note">Este resultado será usado na Etapa 10C para melhorar suas próximas sugestões.</div>
        <div class="mentor10b-actions">
          <button type="button" class="mini-button mini-button--primary" data-mentor10b-finish>Concluir</button>
        </div>
      </section>
    </div>
  `;
}

async function mentor10BOpenOffer(container, session, reflectionPayload) {
  mentor10BClose(container);
  container.insertAdjacentHTML("beforeend", mentor10BOfferMarkup(session));
  const modal = container.querySelector("[data-mentor10b-modal]");

  modal?.querySelector("[data-mentor10b-skip]")?.addEventListener("click", () => mentor10BClose(container));
  modal?.querySelector("[data-mentor10b-start]")?.addEventListener("click", async event => {
    const button = event.currentTarget;
    button.disabled = true;
    try {
      const api = await mentor10BApi();
      const response = await api.startStudySessionCheckV10B({
        session_id: Number(session.id),
        materia: String(session.materia || ""),
        assunto: String(session.assunto || ""),
        dificuldade_inicial: reflectionPayload?.dificuldade_inicial ?? null,
        dificuldade_final: reflectionPayload?.dificuldade_final ?? null,
      });
      mentor10BClose(container);
      mentor10BOpenQuestions(container, session, response?.questions || []);
    } catch (error) {
      mentor10BClose(container);
      showToast(error?.message || "A IA não conseguiu gerar a verificação agora. A sessão continua concluída.", "error");
    }
  });
}

function mentor10BOpenQuestions(container, session, questions) {
  if (!Array.isArray(questions) || questions.length !== 2) {
    showToast("O Mentor não conseguiu montar duas questões válidas.", "error");
    return;
  }

  container.insertAdjacentHTML("beforeend", mentor10BQuestionsMarkup(session, questions));
  const modal = container.querySelector("[data-mentor10b-modal]");
  const form = modal?.querySelector("[data-mentor10b-form]");

  modal?.querySelector("[data-mentor10b-close]")?.addEventListener("click", () => mentor10BClose(container));

  form?.addEventListener("submit", async event => {
    event.preventDefault();
    const data = new FormData(form);
    const answers = {};
    for (const question of questions) {
      answers[String(question.id)] = String(data.get(`q_${question.id}`) || "");
    }

    const submit = form.querySelector('button[type="submit"]');
    if (submit) submit.disabled = true;

    try {
      const api = await mentor10BApi();
      const result = await api.submitStudySessionCheckV10B({
        session_id: Number(session.id),
        answers,
      });
      mentor10BClose(container);
      container.insertAdjacentHTML("beforeend", mentor10BResultMarkup(result));
      container.querySelector("[data-mentor10b-finish]")?.addEventListener("click", () => mentor10BClose(container));
    } catch (error) {
      if (submit) submit.disabled = false;
      showToast(error?.message || "Não foi possível corrigir a verificação.", "error");
    }
  });
}

// MENTOR_EDU_ADAPTIVE_STUDY_V10C_V2
async function mentor10CLoadAdaptive() {
    const module = await import(
        "../../api/study-sessions.js"
    );

    return module.getAdaptiveStudyV10C();
}


function mentor10CMarkup(data) {
    const next = data?.next_action;

    if (!next) {
        return "";
    }

    const reasons = Array.isArray(
        next.motivos
    )
        ? next.motivos
        : [];

    return `
        <section class="mentor10c-next">
            <div class="mentor10c-badge">
                ADAPTAÇÃO DO MENTOR
            </div>

            <div class="mentor10c-headline">
                <div>
                    <span>
                        ${escapeHtml(
                            next.rotulo
                            || "Próximo passo"
                        )}
                    </span>

                    <h4>
                        ${escapeHtml(
                            next.materia
                            || "Conteúdo"
                        )}
                        ·
                        ${escapeHtml(
                            next.assunto
                            || ""
                        )}
                    </h4>
                </div>

                <strong
                    class="mentor10c-level mentor10c-level--${
                        escapeHtml(
                            next.nivel
                            || "baixa"
                        )
                    }"
                >
                    ${
                        next.nivel === "consolidado"
                            ? "Consolidado"
                            : `Prioridade ${escapeHtml(
                                next.nivel
                                || "baixa"
                            )}`
                    }
                </strong>
            </div>

            <p>
                ${escapeHtml(
                    next.recomendacao
                    || ""
                )}
            </p>

            ${
                reasons.length
                    ? `
                        <div class="mentor10c-reasons">
                            ${reasons.map(
                                item => `
                                    <span>
                                        ${escapeHtml(item)}
                                    </span>
                                `
                            ).join("")}
                        </div>
                    `
                    : ""
            }
        </section>
    `;
}


async function mentor10CInject(container) {
    const result = container.querySelector(
        ".mentor10b-result"
    );

    if (!result) {
        return;
    }

    let target = result.querySelector(
        "[data-mentor10c-target]"
    );

    if (!target) {
        target = document.createElement(
            "div"
        );

        target.setAttribute(
            "data-mentor10c-target",
            ""
        );

        const actions = result.querySelector(
            ".mentor10b-actions"
        );

        if (actions) {
            actions.before(target);
        } else {
            result.appendChild(target);
        }
    }

    if (
        target.dataset.loaded === "1"
        || target.dataset.loading === "1"
    ) {
        return;
    }

    target.dataset.loading = "1";

    try {
        const data =
            await mentor10CLoadAdaptive();

        target.innerHTML =
            mentor10CMarkup(data);

        target.dataset.loaded = "1";
    } catch {
        target.innerHTML = "";
    } finally {
        target.dataset.loading = "0";
    }
}


function mentor10CInstallObserver(
    container,
) {
    if (container.__mentor10CObserver) {
        mentor10CInject(container);
        return;
    }

    const observer = new MutationObserver(
        () => {
            mentor10CInject(
                container
            );
        },
    );

    observer.observe(
        container,
        {
            childList: true,
            subtree: true,
        },
    );

    container.__mentor10CObserver = observer;

    mentor10CInject(container);
}

// MENTOR_EDU_PEDAGOGICAL_MEMORY_V11A
async function mentor11ALoadMemory() {
    const module = await import(
        "../../api/study-sessions.js"
    );

    return module.getPedagogicalMemoryV11A();
}


function mentor11AMemoryMarkup(memory) {
    if (!memory?.has_data) {
        return `
            <section class="mentor11a-memory">
                <div class="mentor11a-memory-head">
                    <div>
                        <span>MEMÓRIA PEDAGÓGICA</span>
                        <h3>Seu perfil está começando a ser construído</h3>
                    </div>

                    <strong>11A</strong>
                </div>

                <p>
                    Conclua algumas sessões com autoavaliação
                    e verificação para o Mentor identificar
                    padrões reais do seu aprendizado.
                </p>
            </section>
        `;
    }

    const indicators = (
        memory.indicadores
        || {}
    );

    const patterns = Array.isArray(
        memory.padroes
    )
        ? memory.padroes
        : [];

    const attention = Array.isArray(
        memory.conteudos_atencao
    )
        ? memory.conteudos_atencao
        : [];

    const strengths = Array.isArray(
        memory.conteudos_fortes
    )
        ? memory.conteudos_fortes
        : [];

    const metric = (
        label,
        value,
        suffix = ""
    ) => `
        <div class="mentor11a-metric">
            <span>${escapeHtml(label)}</span>
            <strong>
                ${
                    value === null
                    || value === undefined
                        ? "—"
                        : `${escapeHtml(value)}${suffix}`
                }
            </strong>
        </div>
    `;

    return `
        <section class="mentor11a-memory">
            <div class="mentor11a-memory-head">
                <div>
                    <span>MEMÓRIA PEDAGÓGICA</span>
                    <h3>O que o Mentor já aprendeu sobre seus estudos</h3>
                </div>

                <strong>
                    Confiança ${escapeHtml(
                        memory.confianca
                        || "baixa"
                    )}
                </strong>
            </div>

            <p class="mentor11a-summary">
                ${escapeHtml(
                    memory.resumo
                    || ""
                )}
            </p>

            <div class="mentor11a-metrics">
                ${metric(
                    "Sessões",
                    memory.sessoes_analisadas
                )}

                ${metric(
                    "Checagens",
                    memory.checagens_analisadas
                )}

                ${metric(
                    "Compreensão média",
                    indicators.compreensao_media,
                    "/5"
                )}

                ${metric(
                    "Acerto nas checagens",
                    indicators.acerto_checagens_percentual,
                    "%"
                )}

                ${metric(
                    "Foco x planejado",
                    indicators.foco_sobre_planejado_percentual,
                    "%"
                )}
            </div>

            ${
                patterns.length
                    ? `
                        <div class="mentor11a-section">
                            <h4>Padrões observados</h4>

                            <div class="mentor11a-patterns">
                                ${patterns.map(
                                    item => `
                                        <article>
                                            <strong>
                                                ${escapeHtml(
                                                    item.titulo
                                                    || ""
                                                )}
                                            </strong>

                                            <span>
                                                ${escapeHtml(
                                                    item.descricao
                                                    || ""
                                                )}
                                            </span>
                                        </article>
                                    `
                                ).join("")}
                            </div>
                        </div>
                    `
                    : ""
            }

            <div class="mentor11a-columns">
                <div class="mentor11a-section">
                    <h4>Pontos de atenção</h4>

                    ${
                        attention.length
                            ? attention.slice(
                                0,
                                3
                            ).map(
                                item => `
                                    <div class="mentor11a-topic">
                                        <strong>
                                            ${escapeHtml(
                                                item.materia
                                                || ""
                                            )}
                                        </strong>

                                        <span>
                                            ${escapeHtml(
                                                item.assunto
                                                || ""
                                            )}
                                        </span>
                                    </div>
                                `
                            ).join("")
                            : `
                                <span class="mentor11a-empty">
                                    Nenhum ponto recorrente identificado ainda.
                                </span>
                            `
                    }
                </div>

                <div class="mentor11a-section">
                    <h4>Conteúdos fortes</h4>

                    ${
                        strengths.length
                            ? strengths.slice(
                                0,
                                3
                            ).map(
                                item => `
                                    <div class="mentor11a-topic">
                                        <strong>
                                            ${escapeHtml(
                                                item.materia
                                                || ""
                                            )}
                                        </strong>

                                        <span>
                                            ${escapeHtml(
                                                item.assunto
                                                || ""
                                            )}
                                        </span>
                                    </div>
                                `
                            ).join("")
                            : `
                                <span class="mentor11a-empty">
                                    O Mentor ainda está reunindo evidências.
                                </span>
                            `
                    }
                </div>
            </div>

            <footer class="mentor11a-foot">
                Baseado apenas em dados pedagógicos das suas sessões.
                Sem diagnóstico psicológico ou comportamental.
            </footer>
        </section>
    `;
}


async function mentor11ARenderMemory(
    container,
) {
    let target = container.querySelector(
        "[data-mentor11a-memory]"
    );

    if (!target) {
        target = document.createElement(
            "div"
        );

        target.setAttribute(
            "data-mentor11a-memory",
            ""
        );

        container.prepend(
            target
        );
    }

    if (
        target.dataset.loading === "1"
    ) {
        return;
    }

    target.dataset.loading = "1";

    try {
        const memory =
            await mentor11ALoadMemory();

        target.innerHTML =
            mentor11AMemoryMarkup(
                memory
            );

    } catch {
        target.innerHTML = "";
    } finally {
        target.dataset.loading = "0";
    }
}

export async function renderStudentStudySessions(container) {
    const sessions = await getMyStudySessions();
    const render = current => {
        container.innerHTML = `${pageHeader("Sessões de estudo", "Registre o que estudou e acompanhe sua rotina.", `<button class="mini-button mini-button--primary" type="button" data-new-session>Nova sessão</button>`)}${sessionForm()}${mentorFocusTimerPanel(current)}${surface(current.length ? `<div class="compact-list">${current.map(session => `<article class="compact-row compact-row--actions"><div><strong>${escapeHtml(session.materia)} · ${escapeHtml(session.assunto)}</strong><p>${escapeHtml(session.duracao_minutos)} min${session.data_sessao ? ` · ${escapeHtml(session.data_sessao)}` : ""}${session.dificuldade_sentida ? ` · dificuldade ${escapeHtml(session.dificuldade_sentida)}/5` : ""}</p>${session.observacoes ? `<p>${escapeHtml(session.observacoes)}</p>` : ""}</div><div class="row-actions">${statusPill(session.concluida ? "Concluída" : "Pendente", session.concluida ? "success" : "warning")}<button class="mini-button" type="button" data-toggle-session="${session.id}">${session.concluida ? "Reabrir" : "Concluir"}</button><button class="mini-button mini-button--danger" type="button" data-delete-session="${session.id}">Excluir</button></div></article>`).join("")}</div>` : emptyBlock("Nenhuma sessão registrada", "Registre sua primeira sessão de estudo para começar o acompanhamento.", "clock"))}`;
        bind(current);
    };
    const bind = current => {
        bindFocusTimer(container, current);
        bindMentor10Reflection(container, current, render);
        mentor10CInstallObserver(container);
        bindMentorSessionHelp(container, current);
        const form = container.querySelector("[data-session-form]");
        container.querySelector("[data-new-session]")?.addEventListener("click", () => { form.hidden = false; form.scrollIntoView({ behavior: "smooth", block: "center" }); });
        container.querySelector("[data-cancel-session]")?.addEventListener("click", () => { form.hidden = true; form.reset(); });
        form?.addEventListener("submit", async event => {
            event.preventDefault();
            const data = new FormData(form);
            const payload = {
                materia: String(data.get("materia") || "").trim(),
                assunto: String(data.get("assunto") || "").trim(),
                duracao_minutos: Number(data.get("duracao_minutos")),
                dificuldade_sentida: data.get("dificuldade_sentida") ? Number(data.get("dificuldade_sentida")) : null,
                concluida: false,
                data_sessao: data.get("data_sessao") || null,
                observacoes: String(data.get("observacoes") || "").trim() || null,
            };
            const submit = form.querySelector('button[type="submit"]'); submit.disabled = true;
            try { const saved = await createStudySession(payload); current.unshift(saved); showToast("Sessão registrada."); render(current); }
            catch (error) { submit.disabled = false; showToast(error.message || "Não foi possível registrar a sessão.", "error"); }
        });
        container.querySelectorAll("[data-toggle-session]").forEach(button => button.addEventListener("click", async () => {
            const id = Number(button.dataset.toggleSession); const item = current.find(session => session.id === id); if (!item) return;
            button.disabled = true;
            try { const saved = await updateStudySession(id, { concluida: !item.concluida }); const next = current.map(session => session.id === id ? saved : session); showToast(saved.concluida ? "Sessão concluída." : "Sessão reaberta."); render(next); }
            catch (error) { button.disabled = false; showToast(error.message || "Não foi possível atualizar a sessão.", "error"); }
        }));
        container.querySelectorAll("[data-delete-session]").forEach(button => button.addEventListener("click", async () => {
            if (!window.confirm("Excluir esta sessão de estudo?")) return;
            const id = Number(button.dataset.deleteSession); button.disabled = true;
            try { await deleteStudySession(id); showToast("Sessão excluída."); render(current.filter(item => item.id !== id)); }
            catch (error) { button.disabled = false; showToast(error.message || "Não foi possível excluir a sessão.", "error"); }
        }));
    };
    render([...sessions]);
    applyMentorSessionPrefill(container);
}
