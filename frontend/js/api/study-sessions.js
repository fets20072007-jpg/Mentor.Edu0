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

// MENTOR_EDU_SESSION_REFLECTION_API_V10A_V2
export async function saveStudySessionReflectionV10A(
    payload,
) {
    return api.post(
        "/mentor-ai/student/session-reflection-v10a",
        payload,
    );
}

export async function getStudySessionReflectionsV10A() {
    return api.get(
        "/mentor-ai/student/session-reflections-v10a",
    );
}

// MENTOR_EDU_SESSION_CHECK_API_V10B
export async function startStudySessionCheckV10B(payload) {
  return api.post("/mentor-ai/student/session-check-v10b/start", payload);
}
export async function submitStudySessionCheckV10B(payload) {
  return api.post("/mentor-ai/student/session-check-v10b/submit", payload);
}
export async function getStudySessionCheckV10B(sessionId) {
  return api.get(`/mentor-ai/student/session-check-v10b/${sessionId}`);
}

// MENTOR_EDU_ADAPTIVE_STUDY_API_V10C_V2
export async function getAdaptiveStudyV10C() {
    return api.get(
        "/mentor-ai/student/adaptive-study-v10c",
    );
}
