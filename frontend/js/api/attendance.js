import { api } from "./client.js";
export const getMyAttendance = () => api.get("/attendance/me");
export const getMyAttendanceSummary = () => api.get("/attendance/me/summary");
export const justifyAttendance = (id, data) => api.patch(`/attendance/${id}/justify`, data);
export const getTeacherPendingAttendance = () => api.get("/attendance/teacher/pending");
