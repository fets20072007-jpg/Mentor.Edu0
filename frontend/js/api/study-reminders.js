import { api } from "./client.js";

const LAST_SEEN_KEY = "mentorEdu.studyLastSeenAt";
const MIN_SYNC_GAP_MS = 30 * 1000;

let lastSyncAt = 0;
let listenersInstalled = false;

function readLastSeen() {
    try {
        return Number(localStorage.getItem(LAST_SEEN_KEY) || 0);
    } catch {
        return 0;
    }
}

function writeLastSeen(value = Date.now()) {
    try {
        localStorage.setItem(LAST_SEEN_KEY, String(value));
    } catch {
        // Sem armazenamento local, o restante do app continua funcionando.
    }
}

export async function syncStudyReminders({ force = false } = {}) {
    const now = Date.now();

    if (!force && now - lastSyncAt < MIN_SYNC_GAP_MS) {
        return null;
    }

    lastSyncAt = now;

    const previous = readLastSeen();
    const awaySeconds = previous > 0
        ? Math.max(0, Math.floor((now - previous) / 1000))
        : 0;

    // Atualiza antes da chamada para evitar duplicação após reload.
    writeLastSeen(now);

    try {
        return await api.post(
            "/notifications/me/study-reminder-sync",
            {
                away_seconds: awaySeconds,
                client_now: new Date(now).toISOString(),
            }
        );
    } catch (error) {
        console.warn(
            "[Mentor 9B.3] sincronização indisponível:",
            error?.message || error
        );
        return null;
    }
}

async function ensureServiceWorker() {
    if (!("serviceWorker" in navigator)) return null;

    try {
        // Local Live Server: /frontend/sw.js
        // Render/FastAPI:      /sw.js
        return await navigator.serviceWorker.register("./sw.js");
    } catch (error) {
        console.warn(
            "[Mentor 9B.3] Service Worker não pôde ser registrado:",
            error?.message || error
        );
        return null;
    }
}

export function installStudyReminderPresence() {
    if (listenersInstalled) return;
    listenersInstalled = true;

    ensureServiceWorker();

    const onReturn = () => {
        if (!document.hidden) {
            syncStudyReminders({ force: true });
        }
    };

    window.addEventListener("focus", onReturn);
    document.addEventListener("visibilitychange", onReturn);

    window.setInterval(() => {
        if (!document.hidden) {
            writeLastSeen(Date.now());
        }
    }, 60 * 1000);
}
