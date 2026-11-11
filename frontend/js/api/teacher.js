import { api } from './client.js';

export const getTeacherClassrooms = () => api.get('/teachers/me/classrooms');
export const getTeacherAttendance = () => api.get('/attendance/teacher/me');
export const getTeacherPendingAttendance = () => api.get('/attendance/teacher/pending');
export const getClassroomAttendance = id => api.get(`/attendance/classroom/${id}`);
export const getClassroomAttendanceSummary = id => api.get(`/attendance/classroom/${id}/summary`);
export const registerAttendance = data => api.post('/attendance/', data);

export const createAssessment = data => api.post('/assessments', data);
export const updateAssessment = (id, data) => api.patch(`/assessments/${id}`, data);
export const getAssessmentResults = id => api.get(`/assessments/${id}/results`);
export const getTeacherAssessmentQuestions = id => api.get(`/assessments/${id}/questions/teacher`);
export const configureAssessmentAccess = (id, data) => api.patch(`/assessments/${id}/access`, data);

export const reviewAnswer = (id, percentual_professor) => api.patch(`/answers/${id}/review`, { percentual_professor });

export const createGrade = data => api.post('/grades', data);

export const getMyQuestionBank = () => api.get('/library/question-bank/me');
export const getSharedQuestionBank = () => api.get('/library/question-bank/shared');
export const createQuestionBankItem = data => api.post('/library/question-bank', data);
export const deleteQuestionBankItem = id => api.delete(`/library/question-bank/${id}`);

export const getTeacherClassroomSummary = () => api.get('/assessments/teacher/summary/classrooms');
export const getTeacherStudentDifficulties = () => api.get('/assessments/teacher/difficulties/students');
export const getTeacherStudentPerformance = () => api.get('/assessments/teacher/students/performance');
export const getTeacherQuestionDifficulties = () => api.get('/assessments/teacher/questions/difficulties');
export const updateAttendance = (id, data) => api.patch(`/attendance/${id}`, data);
export const justifyAttendanceTeacher = (id, data) => api.patch(`/attendance/${id}/justify`, data);
export const reviewAttendanceJustification = (id, data) => api.patch(`/attendance/${id}/justification/review`, data);
