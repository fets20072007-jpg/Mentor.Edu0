from pathlib import Path
import sys

ROOT = Path.cwd()

PAGE = (
    ROOT
    / "frontend"
    / "js"
    / "pages"
    / "student"
    / "study-sessions.js"
)

CSS = (
    ROOT
    / "frontend"
    / "css"
    / "pages.css"
)

for path in (PAGE, CSS):
    if not path.exists():
        raise SystemExit(
            f"ERRO: arquivo necessário não encontrado: {path}"
        )

def read(path):
    return path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

page = read(PAGE)
css = read(CSS)

original_page = page
original_css = css

TIMER_JS = '\n// MENTOR_EDU_FOCUS_TIMER_V9A\nconst MENTOR_FOCUS_TIMER_KEY = "mentor_edu_focus_timer_v1";\n\nfunction mentorFocusNow() {\n    return Date.now();\n}\n\nfunction mentorFocusIsPageActive() {\n    return (\n        document.visibilityState === "visible"\n        && document.hasFocus()\n    );\n}\n\nfunction mentorFocusReadState() {\n    try {\n        const raw = localStorage.getItem(\n            MENTOR_FOCUS_TIMER_KEY,\n        );\n\n        if (!raw) return null;\n\n        const state = JSON.parse(raw);\n\n        if (!state?.sessionId) {\n            return null;\n        }\n\n        return state;\n    } catch {\n        return null;\n    }\n}\n\nfunction mentorFocusWriteState(state) {\n    try {\n        localStorage.setItem(\n            MENTOR_FOCUS_TIMER_KEY,\n            JSON.stringify(state),\n        );\n    } catch {\n        // O temporizador continua funcionando em memória.\n    }\n}\n\nfunction mentorFocusClearState() {\n    try {\n        localStorage.removeItem(\n            MENTOR_FOCUS_TIMER_KEY,\n        );\n    } catch {\n        // Sem ação.\n    }\n}\n\nfunction mentorFocusFormatMs(value) {\n    const total = Math.max(\n        0,\n        Math.floor(Number(value || 0) / 1000),\n    );\n\n    const hours = Math.floor(total / 3600);\n    const minutes = Math.floor(\n        (total % 3600) / 60,\n    );\n    const seconds = total % 60;\n\n    if (hours > 0) {\n        return [\n            String(hours).padStart(2, "0"),\n            String(minutes).padStart(2, "0"),\n            String(seconds).padStart(2, "0"),\n        ].join(":");\n    }\n\n    return [\n        String(minutes).padStart(2, "0"),\n        String(seconds).padStart(2, "0"),\n    ].join(":");\n}\n\nfunction mentorFocusRemainingMs(state) {\n    const plannedMs =\n        Number(state?.plannedMinutes || 0)\n        * 60\n        * 1000;\n\n    return Math.max(\n        0,\n        plannedMs - Number(state?.activeMs || 0),\n    );\n}\n\nfunction mentorFocusPlannedEnd(state) {\n    return (\n        Number(state?.startedAt || 0)\n        + Number(state?.plannedMinutes || 0)\n        * 60\n        * 1000\n    );\n}\n\nfunction mentorFocusUrgency(state) {\n    const remainingMs =\n        mentorFocusRemainingMs(state);\n\n    if (remainingMs <= 0) {\n        return {\n            level: "concluido",\n            label: "Concluído",\n            score: 0,\n        };\n    }\n\n    const now = mentorFocusNow();\n    const plannedEnd =\n        mentorFocusPlannedEnd(state);\n\n    if (now <= plannedEnd) {\n        return {\n            level: "em-dia",\n            label: "Em andamento",\n            score: 0,\n        };\n    }\n\n    const lateMinutes =\n        (now - plannedEnd) / 60000;\n\n    const remainingMinutes =\n        remainingMs / 60000;\n\n    const score = Math.max(\n        lateMinutes,\n        remainingMinutes,\n    );\n\n    if (score > 30) {\n        return {\n            level: "critico",\n            label: "Urgência crítica",\n            score,\n        };\n    }\n\n    if (score > 15) {\n        return {\n            level: "alto",\n            label: "Urgência alta",\n            score,\n        };\n    }\n\n    if (score > 5) {\n        return {\n            level: "medio",\n            label: "Urgência média",\n            score,\n        };\n    }\n\n    return {\n        level: "baixo",\n        label: "Lembrete",\n        score,\n    };\n}\n\nfunction mentorFocusNotificationBody(\n    state,\n    urgency,\n) {\n    const remainingMinutes = Math.ceil(\n        mentorFocusRemainingMs(state) / 60000,\n    );\n\n    const now = mentorFocusNow();\n    const lateMinutes = Math.max(\n        0,\n        Math.floor(\n            (\n                now\n                - mentorFocusPlannedEnd(state)\n            ) / 60000,\n        ),\n    );\n\n    if (urgency.level === "concluido") {\n        return (\n            `Você completou o tempo de foco de `\n            + `${state.title}.`\n        );\n    }\n\n    return (\n        `${state.title}: ainda faltam `\n        + `${remainingMinutes} min de foco. `\n        + (\n            lateMinutes > 0\n                ? `O horário previsto terminou há ${lateMinutes} min.`\n                : "Continue a sessão para cumprir o tempo planejado."\n        )\n    );\n}\n\nfunction mentorFocusCanNotify() {\n    return (\n        "Notification" in window\n        && Notification.permission === "granted"\n    );\n}\n\nasync function mentorFocusRequestNotifications() {\n    if (!("Notification" in window)) {\n        return "unsupported";\n    }\n\n    try {\n        return await Notification.requestPermission();\n    } catch {\n        return Notification.permission;\n    }\n}\n\nfunction mentorFocusNotify(\n    state,\n    urgency,\n) {\n    if (!mentorFocusCanNotify()) {\n        return;\n    }\n\n    const tag =\n        `mentor-study-session-${state.sessionId}`;\n\n    try {\n        new Notification(\n            urgency.level === "concluido"\n                ? "Sessão de estudo concluída"\n                : urgency.label,\n            {\n                body: mentorFocusNotificationBody(\n                    state,\n                    urgency,\n                ),\n                tag,\n                renotify: true,\n                requireInteraction:\n                    urgency.level === "critico",\n            },\n        );\n    } catch {\n        // Notificação do SO é complementar.\n    }\n}\n\nfunction mentorFocusRestoreGap(state) {\n    if (!state) return state;\n\n    const now = mentorFocusNow();\n    const lastTick =\n        Number(state.lastTickAt || now);\n\n    if (\n        state.status === "running"\n        && now > lastTick\n    ) {\n        state.awayMs =\n            Number(state.awayMs || 0)\n            + (now - lastTick);\n\n        state.lastTickAt = now;\n        mentorFocusWriteState(state);\n    }\n\n    return state;\n}\n\nfunction mentorFocusSessionLabel(session) {\n    return (\n        `${session?.materia || "Matéria"}`\n        + (\n            session?.assunto\n                ? ` · ${session.assunto}`\n                : ""\n        )\n    );\n}\n\nfunction mentorFocusTimerPanel(current) {\n    const pending = (current || [])\n        .filter(item => !item?.concluida);\n\n    const state = mentorFocusRestoreGap(\n        mentorFocusReadState(),\n    );\n\n    if (!pending.length && !state) {\n        return `\n            <section class="mentor-focus-shell">\n                <div class="mentor-focus-title">\n                    <div>\n                        <span>FOCO</span>\n                        <strong>Temporizador de estudo</strong>\n                        <p>Registre uma sessão pendente para iniciar o acompanhamento.</p>\n                    </div>\n                </div>\n            </section>\n        `;\n    }\n\n    const selectedId =\n        Number(state?.sessionId || pending[0]?.id || 0);\n\n    const options = pending\n        .map(session => `\n            <option\n                value="${session.id}"\n                ${\n                    Number(session.id) === selectedId\n                        ? "selected"\n                        : ""\n                }\n            >\n                ${escapeHtml(mentorFocusSessionLabel(session))}\n                · ${escapeHtml(session.duracao_minutos)} min\n            </option>\n        `)\n        .join("");\n\n    const hasTimer = Boolean(state);\n    const remainingMs =\n        hasTimer\n            ? mentorFocusRemainingMs(state)\n            : 0;\n\n    const urgency =\n        hasTimer\n            ? mentorFocusUrgency(state)\n            : {\n                level: "em-dia",\n                label: "Pronto",\n            };\n\n    return `\n        <section\n            class="mentor-focus-shell is-${escapeHtml(urgency.level)}"\n            data-focus-shell\n        >\n            <div class="mentor-focus-title">\n                <div>\n                    <span>FOCO</span>\n                    <strong>Temporizador de estudo</strong>\n                    <p>\n                        O Mentor conta apenas o tempo em que esta página está ativa.\n                        Se você sair da aba, o período fica registrado como tempo fora.\n                    </p>\n                </div>\n\n                <span\n                    class="mentor-focus-urgency"\n                    data-focus-urgency\n                >\n                    ${escapeHtml(urgency.label)}\n                </span>\n            </div>\n\n            <div class="mentor-focus-picker">\n                <label>\n                    Sessão\n                    <select\n                        data-focus-session\n                        ${hasTimer ? "disabled" : ""}\n                    >\n                        ${options}\n                    </select>\n                </label>\n\n                <button\n                    type="button"\n                    class="mini-button mini-button--primary"\n                    data-focus-start\n                    ${hasTimer ? "hidden" : ""}\n                >\n                    Iniciar foco\n                </button>\n\n                <button\n                    type="button"\n                    class="mini-button"\n                    data-focus-pause\n                    ${hasTimer ? "" : "hidden"}\n                >\n                    ${\n                        state?.status === "paused"\n                            ? "Retomar"\n                            : "Pausar"\n                    }\n                </button>\n\n                <button\n                    type="button"\n                    class="mini-button mini-button--danger"\n                    data-focus-stop\n                    ${hasTimer ? "" : "hidden"}\n                >\n                    Encerrar\n                </button>\n\n                <button\n                    type="button"\n                    class="mini-button"\n                    data-focus-notifications\n                >\n                    ${\n                        mentorFocusCanNotify()\n                            ? "Notificações ativas"\n                            : "Ativar notificações"\n                    }\n                </button>\n            </div>\n\n            <div class="mentor-focus-clock">\n                <div>\n                    <span>Tempo pendente</span>\n                    <strong data-focus-remaining>\n                        ${\n                            hasTimer\n                                ? mentorFocusFormatMs(remainingMs)\n                                : "--:--"\n                        }\n                    </strong>\n                </div>\n\n                <div>\n                    <span>Foco computado</span>\n                    <strong data-focus-active>\n                        ${\n                            hasTimer\n                                ? mentorFocusFormatMs(state.activeMs)\n                                : "00:00"\n                        }\n                    </strong>\n                </div>\n\n                <div>\n                    <span>Tempo fora da aba</span>\n                    <strong data-focus-away>\n                        ${\n                            hasTimer\n                                ? mentorFocusFormatMs(state.awayMs)\n                                : "00:00"\n                        }\n                    </strong>\n                </div>\n            </div>\n\n            <div\n                class="mentor-focus-message"\n                data-focus-message\n            ></div>\n        </section>\n    `;\n}\n\nfunction bindFocusTimer(\n    container,\n    current,\n) {\n    const shell = container.querySelector(\n        "[data-focus-shell]",\n    );\n\n    if (!shell) return;\n\n    const select = shell.querySelector(\n        "[data-focus-session]",\n    );\n\n    const startButton = shell.querySelector(\n        "[data-focus-start]",\n    );\n\n    const pauseButton = shell.querySelector(\n        "[data-focus-pause]",\n    );\n\n    const stopButton = shell.querySelector(\n        "[data-focus-stop]",\n    );\n\n    const notificationButton = shell.querySelector(\n        "[data-focus-notifications]",\n    );\n\n    const remaining = shell.querySelector(\n        "[data-focus-remaining]",\n    );\n\n    const active = shell.querySelector(\n        "[data-focus-active]",\n    );\n\n    const away = shell.querySelector(\n        "[data-focus-away]",\n    );\n\n    const urgencyNode = shell.querySelector(\n        "[data-focus-urgency]",\n    );\n\n    const message = shell.querySelector(\n        "[data-focus-message]",\n    );\n\n    let state = mentorFocusRestoreGap(\n        mentorFocusReadState(),\n    );\n\n    let intervalId = null;\n\n    const sessionForState = () => {\n        if (!state) return null;\n\n        return (current || []).find(\n            item =>\n                Number(item.id)\n                === Number(state.sessionId),\n        ) || null;\n    };\n\n    const syncState = () => {\n        if (!state) return;\n\n        const now = mentorFocusNow();\n        const lastTick =\n            Number(state.lastTickAt || now);\n\n        const delta = Math.max(\n            0,\n            Math.min(\n                now - lastTick,\n                60 * 1000,\n            ),\n        );\n\n        if (state.status === "running") {\n            if (mentorFocusIsPageActive()) {\n                state.activeMs =\n                    Number(state.activeMs || 0)\n                    + delta;\n            } else {\n                state.awayMs =\n                    Number(state.awayMs || 0)\n                    + delta;\n            }\n        } else if (\n            state.status === "paused"\n            && now > lastTick\n        ) {\n            state.awayMs =\n                Number(state.awayMs || 0)\n                + delta;\n        }\n\n        state.lastTickAt = now;\n    };\n\n    const renderState = () => {\n        if (!state) return;\n\n        const pendingMs =\n            mentorFocusRemainingMs(state);\n\n        const urgency =\n            mentorFocusUrgency(state);\n\n        if (remaining) {\n            remaining.textContent =\n                mentorFocusFormatMs(pendingMs);\n        }\n\n        if (active) {\n            active.textContent =\n                mentorFocusFormatMs(state.activeMs);\n        }\n\n        if (away) {\n            away.textContent =\n                mentorFocusFormatMs(state.awayMs);\n        }\n\n        if (urgencyNode) {\n            urgencyNode.textContent =\n                urgency.label;\n        }\n\n        shell.className =\n            `mentor-focus-shell is-${urgency.level}`;\n\n        if (\n            urgency.level !== "em-dia"\n            && urgency.level !== state.lastUrgency\n        ) {\n            mentorFocusNotify(\n                state,\n                urgency,\n            );\n\n            state.lastUrgency =\n                urgency.level;\n        }\n\n        if (message) {\n            if (urgency.level === "concluido") {\n                message.innerHTML = `\n                    <strong>Tempo de foco cumprido.</strong>\n                    <span>\n                        Agora você pode marcar a sessão como concluída na lista abaixo.\n                    </span>\n                `;\n            } else if (\n                ["baixo", "medio", "alto", "critico"]\n                    .includes(urgency.level)\n            ) {\n                const lateMinutes = Math.max(\n                    0,\n                    Math.floor(\n                        (\n                            mentorFocusNow()\n                            - mentorFocusPlannedEnd(state)\n                        ) / 60000,\n                    ),\n                );\n\n                const pendingMinutes = Math.ceil(\n                    pendingMs / 60000,\n                );\n\n                message.innerHTML = `\n                    <strong>\n                        ${escapeHtml(urgency.label)}\n                    </strong>\n                    <span>\n                        Horário previsto encerrado há\n                        ${lateMinutes} min.\n                        Ainda faltam\n                        ${pendingMinutes} min\n                        de foco ativo.\n                    </span>\n                `;\n            } else {\n                message.innerHTML = `\n                    <strong>Sessão em andamento.</strong>\n                    <span>\n                        O tempo só conta como foco enquanto o Mentor.Edu estiver ativo na tela.\n                    </span>\n                `;\n            }\n        }\n\n        mentorFocusWriteState(state);\n    };\n\n    const tick = () => {\n        if (!state) return;\n\n        syncState();\n        renderState();\n    };\n\n    const startInterval = () => {\n        if (intervalId) {\n            clearInterval(intervalId);\n        }\n\n        intervalId = setInterval(\n            tick,\n            1000,\n        );\n    };\n\n    startButton?.addEventListener(\n        "click",\n        () => {\n            const id = Number(\n                select?.value || 0,\n            );\n\n            const session = (current || []).find(\n                item =>\n                    Number(item.id) === id,\n            );\n\n            if (!session) {\n                showToast(\n                    "Selecione uma sessão pendente.",\n                    "error",\n                );\n                return;\n            }\n\n            const now = mentorFocusNow();\n\n            state = {\n                sessionId: Number(session.id),\n                title: mentorFocusSessionLabel(session),\n                plannedMinutes: Math.max(\n                    1,\n                    Number(session.duracao_minutos || 30),\n                ),\n                startedAt: now,\n                lastTickAt: now,\n                activeMs: 0,\n                awayMs: 0,\n                status: "running",\n                lastUrgency: "em-dia",\n            };\n\n            mentorFocusWriteState(state);\n\n            showToast(\n                "Temporizador iniciado.",\n                "success",\n            );\n\n            const renderCurrent =\n                container.querySelector(\n                    "[data-focus-shell]",\n                );\n\n            if (renderCurrent) {\n                // A renderização completa ocorrerá no próximo carregamento.\n                location.reload();\n            }\n        },\n    );\n\n    pauseButton?.addEventListener(\n        "click",\n        () => {\n            if (!state) return;\n\n            syncState();\n\n            if (state.status === "paused") {\n                state.status = "running";\n                state.lastTickAt =\n                    mentorFocusNow();\n\n                pauseButton.textContent =\n                    "Pausar";\n            } else {\n                state.status = "paused";\n                state.lastTickAt =\n                    mentorFocusNow();\n\n                pauseButton.textContent =\n                    "Retomar";\n            }\n\n            mentorFocusWriteState(state);\n            renderState();\n        },\n    );\n\n    stopButton?.addEventListener(\n        "click",\n        () => {\n            if (!state) return;\n\n            const ok = window.confirm(\n                "Encerrar este temporizador de foco?"\n            );\n\n            if (!ok) return;\n\n            mentorFocusClearState();\n            state = null;\n\n            if (intervalId) {\n                clearInterval(intervalId);\n            }\n\n            showToast(\n                "Temporizador encerrado.",\n            );\n\n            location.reload();\n        },\n    );\n\n    notificationButton?.addEventListener(\n        "click",\n        async () => {\n            const permission =\n                await mentorFocusRequestNotifications();\n\n            if (permission === "granted") {\n                notificationButton.textContent =\n                    "Notificações ativas";\n\n                showToast(\n                    "Notificações do temporizador ativadas.",\n                    "success",\n                );\n            } else if (\n                permission === "unsupported"\n            ) {\n                showToast(\n                    "Este navegador não oferece notificações deste tipo.",\n                    "error",\n                );\n            } else {\n                showToast(\n                    "Permissão de notificações não concedida.",\n                    "error",\n                );\n            }\n        },\n    );\n\n    if (state) {\n        const currentSession =\n            sessionForState();\n\n        if (\n            currentSession?.concluida\n        ) {\n            mentorFocusClearState();\n            state = null;\n            return;\n        }\n\n        renderState();\n        startInterval();\n    }\n\n    const onVisibility = () => {\n        if (!state) return;\n\n        syncState();\n        mentorFocusWriteState(state);\n    };\n\n    document.addEventListener(\n        "visibilitychange",\n        onVisibility,\n    );\n\n    window.addEventListener(\n        "blur",\n        onVisibility,\n    );\n\n    window.addEventListener(\n        "focus",\n        onVisibility,\n    );\n\n    window.addEventListener(\n        "beforeunload",\n        onVisibility,\n        {\n            once: true,\n        },\n    );\n}\n'
TIMER_CSS = '\n/* MENTOR_EDU_FOCUS_TIMER_V9A */\n.mentor-focus-shell {\n    margin: 14px 0;\n    padding: 18px;\n    border: 1px solid #ddd6fe;\n    border-radius: 18px;\n    background:\n        linear-gradient(\n            180deg,\n            #ffffff 0%,\n            #fcfaff 100%\n        );\n}\n\n.mentor-focus-title {\n    display: flex;\n    align-items: flex-start;\n    justify-content: space-between;\n    gap: 16px;\n}\n\n.mentor-focus-title > div > span {\n    display: block;\n    margin-bottom: 4px;\n    color: #7c3aed;\n    font-size: 10px;\n    font-weight: 900;\n    letter-spacing: .08em;\n}\n\n.mentor-focus-title strong {\n    display: block;\n    color: #241b2f;\n    font-size: 17px;\n}\n\n.mentor-focus-title p {\n    max-width: 720px;\n    margin: 5px 0 0;\n    color: #776d80;\n    font-size: 11px;\n    line-height: 1.55;\n}\n\n.mentor-focus-urgency {\n    flex: 0 0 auto;\n    padding: 7px 10px;\n    border-radius: 999px;\n    background: #ede9fe;\n    color: #6d28d9;\n    font-size: 9px;\n    font-weight: 900;\n    text-transform: uppercase;\n}\n\n.mentor-focus-shell.is-baixo {\n    border-color: #fde68a;\n}\n\n.mentor-focus-shell.is-baixo .mentor-focus-urgency {\n    background: #fef3c7;\n    color: #92400e;\n}\n\n.mentor-focus-shell.is-medio {\n    border-color: #fdba74;\n}\n\n.mentor-focus-shell.is-medio .mentor-focus-urgency {\n    background: #ffedd5;\n    color: #c2410c;\n}\n\n.mentor-focus-shell.is-alto,\n.mentor-focus-shell.is-critico {\n    border-color: #fca5a5;\n}\n\n.mentor-focus-shell.is-alto .mentor-focus-urgency,\n.mentor-focus-shell.is-critico .mentor-focus-urgency {\n    background: #fee2e2;\n    color: #b91c1c;\n}\n\n.mentor-focus-shell.is-concluido {\n    border-color: #86efac;\n}\n\n.mentor-focus-shell.is-concluido .mentor-focus-urgency {\n    background: #dcfce7;\n    color: #166534;\n}\n\n.mentor-focus-picker {\n    display: flex;\n    flex-wrap: wrap;\n    align-items: end;\n    gap: 9px;\n    margin-top: 16px;\n}\n\n.mentor-focus-picker label {\n    display: grid;\n    min-width: min(100%, 320px);\n    gap: 5px;\n    color: #665d70;\n    font-size: 10px;\n    font-weight: 800;\n}\n\n.mentor-focus-picker select {\n    min-height: 36px;\n    padding: 0 10px;\n    border: 1px solid #ddd3e8;\n    border-radius: 10px;\n    background: #fff;\n    color: #2e2636;\n    font: inherit;\n}\n\n.mentor-focus-clock {\n    display: grid;\n    grid-template-columns:\n        repeat(3, minmax(0, 1fr));\n    gap: 10px;\n    margin-top: 15px;\n}\n\n.mentor-focus-clock > div {\n    padding: 13px;\n    border: 1px solid #eee8f4;\n    border-radius: 13px;\n    background: #fff;\n}\n\n.mentor-focus-clock span {\n    display: block;\n    color: #817788;\n    font-size: 9px;\n    font-weight: 800;\n    text-transform: uppercase;\n}\n\n.mentor-focus-clock strong {\n    display: block;\n    margin-top: 5px;\n    color: #2f2637;\n    font-size: 22px;\n    font-variant-numeric: tabular-nums;\n}\n\n.mentor-focus-message {\n    display: flex;\n    gap: 8px;\n    margin-top: 12px;\n    padding: 10px 12px;\n    border-radius: 11px;\n    background: #f7f3fb;\n    color: #655b6f;\n    font-size: 10px;\n}\n\n.mentor-focus-message strong {\n    color: #3b3046;\n}\n\n@media (max-width: 700px) {\n    .mentor-focus-title {\n        display: grid;\n    }\n\n    .mentor-focus-urgency {\n        justify-self: start;\n    }\n\n    .mentor-focus-clock {\n        grid-template-columns: 1fr;\n    }\n\n    .mentor-focus-picker {\n        align-items: stretch;\n    }\n\n    .mentor-focus-picker label,\n    .mentor-focus-picker button {\n        width: 100%;\n    }\n}\n'

# 1) Insere motor do temporizador antes do formulário.
if "MENTOR_EDU_FOCUS_TIMER_V9A" not in page:
    anchor = "function sessionForm()"

    pos = page.find(anchor)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei sessionForm em study-sessions.js. "
            "Nenhuma alteração foi salva."
        )

    page = (
        page[:pos]
        + TIMER_JS.strip()
        + "\n\n"
        + page[pos:]
    )

# 2) Mostra painel do temporizador entre formulário e lista.
if "${focusTimerPanel(current)}" not in page:
    old = "${sessionForm()}${surface("

    if old not in page:
        raise SystemExit(
            "ERRO: não encontrei o ponto para exibir o temporizador. "
            "Nenhuma alteração foi salva."
        )

    page = page.replace(
        old,
        "${sessionForm()}${mentorFocusTimerPanel(current)}${surface(",
        1,
    )

# 3) Conecta o timer ao bind da página.
if "bindFocusTimer(" not in page[
    page.find("const bind = current => {") :
]:
    old = (
        '    const bind = current => {\n'
        '        const form = container.querySelector("[data-session-form]");'
    )

    new = (
        '    const bind = current => {\n'
        '        bindFocusTimer(container, current);\n'
        '        const form = container.querySelector("[data-session-form]");'
    )

    if old not in page:
        raise SystemExit(
            "ERRO: não encontrei o bind atual de study-sessions.js. "
            "Nenhuma alteração foi salva."
        )

    page = page.replace(
        old,
        new,
        1,
    )

# 4) CSS.
if "MENTOR_EDU_FOCUS_TIMER_V9A" not in css:
    css = (
        css.rstrip()
        + "\n\n"
        + TIMER_CSS.strip()
        + "\n"
    )

# 5) Validação.
checks = {
    "motor timer": (
        "MENTOR_EDU_FOCUS_TIMER_V9A"
        in page
    ),
    "painel": (
        "mentorFocusTimerPanel(current)"
        in page
    ),
    "bind": (
        "bindFocusTimer(container, current)"
        in page
    ),
    "visibilidade": (
        "visibilitychange"
        in page
    ),
    "notificações": (
        "Notification.requestPermission"
        in page
        and "mentor-study-session-"
        in page
    ),
    "deduplicação": (
        "tag,"
        in page
        and "lastUrgency"
        in page
    ),
    "urgência": (
        "Urgência crítica"
        in page
        and "Urgência alta"
        in page
        and "Urgência média"
        in page
    ),
    "css": (
        "MENTOR_EDU_FOCUS_TIMER_V9A"
        in css
    ),
}

failed = [
    name
    for name, ok in checks.items()
    if not ok
]

if failed:
    raise SystemExit(
        "ERRO: validação da Etapa 9A falhou. "
        "Nenhuma alteração foi salva: "
        + ", ".join(failed)
    )

if (
    page == original_page
    and css == original_css
):
    print(
        "ETAPA 9A já está aplicada. "
        "Nenhuma alteração necessária."
    )
    sys.exit(0)

# 6) Backups.
page_backup = PAGE.with_name(
    PAGE.name
    + ".backup_etapa9a_timer"
)

css_backup = CSS.with_name(
    CSS.name
    + ".backup_etapa9a_timer"
)

if not page_backup.exists():
    page_backup.write_text(
        original_page,
        encoding="utf-8",
    )

if not css_backup.exists():
    css_backup.write_text(
        original_css,
        encoding="utf-8",
    )

PAGE.write_text(
    page,
    encoding="utf-8",
)

CSS.write_text(
    css,
    encoding="utf-8",
)

print()
print("======================================================")
print(" MENTOR.EDU - ETAPA 9A SESSÃO MONITORADA APLICADA")
print("======================================================")
print()
print("Incluído:")
print("- temporizador por sessão pendente")
print("- tempo de foco real na página")
print("- tempo fora da aba")
print("- persistência após recarregar/navegar")
print("- urgência progressiva quando o horário termina")
print("- notificação do navegador com substituição por sessão")
print()
print("Níveis:")
print("- Lembrete")
print("- Urgência média")
print("- Urgência alta")
print("- Urgência crítica")
print()
print("Observação:")
print("- esta versão mede atividade no Mentor.Edu")
print("- não lê o tempo de tela global do sistema operacional")
print()
print("Use Ctrl + F5 e abra Sessões de estudo.")
