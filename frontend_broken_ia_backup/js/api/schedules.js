import { api } from "./client.js";
export const getMySchedule = () => api.get("/schedules/me");
export const listSchedules = () => api.get("/schedules");
