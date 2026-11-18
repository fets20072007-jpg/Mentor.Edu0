import { api } from "./client.js";

export const listAssessments = () => api.get("/assessments/");
export const getAssessment = id => api.get(`/assessments/${id}`);
export const getAssessmentQuestions = id => api.get(`/assessments/${id}/questions`);
export const getAssessmentAvailability = id => api.get(`/assessments/${id}/availability/me`);
export const getAssessmentResult = id => api.get(`/assessments/${id}/results/me`);
export const getAssessmentSubmission = id => api.get(`/assessments/${id}/submission/me`);
export const getAssessmentAnswerKey = id => api.get(`/assessments/${id}/answer-key/me`);
export const getMyAssessmentHistory = () => api.get("/assessments/history/me");
export const getMyAssessmentSummary = () => api.get("/assessments/summary/me");
export const getMySubjectAssessmentSummary = () => api.get("/assessments/summary/me/subjects");
export const getMyAssessmentEvolution = () => api.get("/assessments/summary/me/evolution");
export const getAdminAssessments = () => api.get("/admin/assessments");
