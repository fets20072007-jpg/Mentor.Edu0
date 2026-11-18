import { api } from "./client.js";
export const getMyPerformance = () => api.get("/performance/me");
