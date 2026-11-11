import { api } from './client.js';

export const getAdminTeachers = () => api.get('/admin/teachers');
export const listTeacherProfiles = () => api.get('/teachers');
export const getAdminStudents = () => api.get('/admin/students');
export const getAdminSummary = () => api.get('/admin/summary');
export const getAdminAssessments = () => api.get('/admin/assessments');
export const getAdminClassrooms = () => api.get('/admin/classrooms');
export const getClassroomTeachers = id => api.get(`/classrooms/${id}/teachers`);

export const registerUser = data => api.post('/users/register', data);
export const createClassroom = data => api.post('/classrooms', data);
export const setClassroomDt = (id, teacher_id) => api.patch(`/classrooms/${id}/dt`, { teacher_id });
export const createSubject = data => api.post('/subjects', data);
export const changeSubjectTeacher = (id, teacher_id) => api.patch(`/subjects/${id}/teacher`, { teacher_id });
export const createEnrollment = data => api.post('/enrollments', data);
export const transferEnrollment = (studentId, classroom_id) => api.patch(`/enrollments/student/${studentId}/classroom`, { classroom_id });
export const createSchedule = data => api.post('/schedules', data);
export const updateSchedule = (id, data) => api.patch(`/schedules/${id}`, data);
export const deleteSchedule = id => api.delete(`/schedules/${id}`);
