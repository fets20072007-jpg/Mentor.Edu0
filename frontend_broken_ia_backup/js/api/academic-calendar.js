import { api } from './client.js';
export const listAcademicEvents = () => api.get('/academic-calendar');
export const createAcademicEvent = data => api.post('/academic-calendar', data);
export const deleteAcademicEvent = id => api.delete(`/academic-calendar/${id}`);
