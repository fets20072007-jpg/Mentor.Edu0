import { api } from "./client.js";
export const getMyStudySessions = () => api.get("/study-sessions/");
export const createStudySession = data => api.post("/study-sessions/", data);
export const updateStudySession = (id, data) => api.put(`/study-sessions/${id}`, data);
export const deleteStudySession = id => api.delete(`/study-sessions/${id}`);
