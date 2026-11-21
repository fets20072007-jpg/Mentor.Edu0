self.addEventListener("install", () => {
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener("push", event => {
    let data = {};

    try {
        data = event.data ? event.data.json() : {};
    } catch {
        data = {
            title: "Mentor Edu",
            body: event.data
                ? event.data.text()
                : "Você tem uma nova notificação."
        };
    }

    const title = data.title || "Mentor Edu";

    const options = {
        body:
            data.body
            || data.message
            || "Você tem uma nova notificação.",
        icon:
            data.icon
            || "./assets/brand/logo-symbol.png",
        badge:
            data.badge
            || "./assets/brand/logo-symbol.png",
        tag:
            data.tag
            || "mentor-edu",
        renotify: true,
        data: {
            url:
                data.url
                || data.link
                || "./dashboard.html#/notifications"
        }
    };

    event.waitUntil(
        self.registration.showNotification(
            title,
            options,
        )
    );
});

self.addEventListener("notificationclick", event => {
    event.notification.close();

    const target =
        event.notification?.data?.url
        || "./dashboard.html#/notifications";

    event.waitUntil(
        self.clients.matchAll({
            type: "window",
            includeUncontrolled: true
        }).then(clients => {
            for (const client of clients) {
                if ("focus" in client) {
                    if ("navigate" in client) {
                        client.navigate(target);
                    }
                    return client.focus();
                }
            }

            return self.clients.openWindow(target);
        })
    );
});
