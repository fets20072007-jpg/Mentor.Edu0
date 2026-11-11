import { api } from "./client.js";
export const getMyEnrollment = () => api.get("/enrollments/me");
export const listEnrollments = () => api.get("/enrollments");
export const getClassroomEnrollments = (id) => api.get(`/enrollments/classroom/${id}`);
