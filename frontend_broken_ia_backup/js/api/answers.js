import { api } from "./client.js";
export const getMyAnswers = () => api.get("/answers/me");
export const getPendingReviews = () => api.get("/answers/teacher/pending");
export const answerQuestion = (questionId, data) => api.post(`/answers/questions/${questionId}`, data);
