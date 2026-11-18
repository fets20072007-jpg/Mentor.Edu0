import { api } from "./client.js";

export const createTicket = data => api.post("/tickets", data);
export const getMyTickets = () => api.get("/tickets/me");
export const getTicketRecipients = () => api.get("/tickets/recipients");
export const getTicketInbox = () => api.get("/tickets/inbox");
export const respondToTicket = (id, data) => api.patch(`/tickets/${id}/respond`, data);
export const getSupportTickets = () => api.get("/tickets");
export const getPendingTicketCount = () => api.get("/tickets/support/pending-count");
export const updateTicketStatus = (id, data) => api.patch(`/tickets/${id}/status`, data);
