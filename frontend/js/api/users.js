import { api } from "./client.js";
export const getMe = () => api.get("/users/me");
export const listUsers = () => api.get("/users/");
export const updateMe = (data) => api.put("/users/me", data);
