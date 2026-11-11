import { api } from "./client.js";
export const getMyStudyPlans = () => api.get("/study-plans/me");
export const createStudyPlan = data => api.post("/study-plans/", data);
export const updateStudyPlan = (id, data) => api.put(`/study-plans/${id}`, data);
export const deleteStudyPlan = id => api.delete(`/study-plans/${id}`);
