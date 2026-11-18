import { api } from "./client.js";
export const getMyGrades = () => api.get("/grades/me");
export const getAssessmentGrades = (id) => api.get(`/grades/assessment/${id}`);
