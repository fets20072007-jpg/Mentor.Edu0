// MENTOR_EDU_SERVICE_WORKER_V9B2
self.addEventListener("push", event => {
    let payload = {};
    try {
        payload = event.data ? event.data.json() : {};
    } catch {
        payload = {
            body: event.data ? event.data.text() : "Você tem uma sessão de estudo pendente.",
        };
    }

    const title = payload.title || "Mentor.Edu";
    const options = {
        body: payload.body || "Há uma sessão de estudo pendente.",
        icon: payload.icon || "/assets/brand/mentor-ai-bot.png",
        badge: payload.badge || "/assets/brand/mentor-ai-bot.png",
        tag: payload.tag || "mentor-study-session",
        renotify: true,
        requireInteraction: Boolean(payload.requireInteraction),
        data: payload.data || { url: "/dashboard.html" },
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", event => {
    event.notification.close();
    const data = event.notification.data || {};
    const targetUrl = data.url || "/dashboard.html";

    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true })
            .then(windowClients => {
                for (const client of windowClients) {
                    if ("focus" in client) return client.focus();
                }
                if (clients.openWindow) return clients.openWindow(targetUrl);
                return null;
            }),
    );
});
