import { api } from "./client.js";
export const getMyAcademicRecord = () => api.get("/academic-record/me");
