import { api } from "./client.js";
export const getStudyRecommendations = () => api.get("/recommendations/generate");
