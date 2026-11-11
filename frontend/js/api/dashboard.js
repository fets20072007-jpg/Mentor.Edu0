import { api } from "./client.js";
export const getStudentDashboard = () => api.get("/dashboard/me");
export const getAdminSummary = () => api.get("/admin/summary");
