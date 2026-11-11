import { api } from "./client.js";
export const getNotifications = () => api.get("/notifications/me");
export const getUnreadCount = () => api.get("/notifications/me/unread-count");
export const markAllRead = () => api.patch("/notifications/me/read-all", {});
export const markRead = (id) => api.patch(`/notifications/${id}/read`, {});
