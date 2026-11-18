import { api } from "./client.js";
export const getMyStudySessions = () => api.get("/study-sessions/");
export const createStudySession = data => api.post("/study-sessions/", data);
export const updateStudySession = (id, data) => api.put(`/study-sessions/${id}`, data);
export const deleteStudySession = id => api.delete(`/study-sessions/${id}`);

// MENTOR_EDU_FOCUS_API_V9B1
export async function syncStudyFocusAlert(payload) {
    return api.post(
        "/mentor-ai/student/focus-alert",
        payload,
    );
}

export async function getStudyFocusAlerts() {
    return api.get(
        "/mentor-ai/student/focus-alerts",
    );
}

export async function clearStudyFocusAlert(sessionId) {
    return api.post(
        "/mentor-ai/student/focus-alert/clear",
        {
            session_id: sessionId,
        },
    );
}

// MENTOR_EDU_WEB_PUSH_API_V9B2
export async function getStudyPushConfig() {
    return api.get("/mentor-ai/student/push/config");
}

export async function saveStudyPushSubscription(subscription) {
    return api.post("/mentor-ai/student/push/subscribe", subscription);
}

export async function removeStudyPushSubscription(endpoint) {
    return api.post(
        "/mentor-ai/student/push/unsubscribe",
        { endpoint },
    );
}
