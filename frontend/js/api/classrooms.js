import { api } from "./client.js";
export const getTeacherClassrooms = () => api.get("/teachers/me/classrooms");
export const listClassrooms = () => api.get("/classrooms");
export const getAdminClassrooms = () => api.get("/admin/classrooms");
