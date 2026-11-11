import { api } from "./client.js";
export const getMySubjects = () => api.get("/subjects/me");
export const listSubjects = () => api.get("/subjects");
