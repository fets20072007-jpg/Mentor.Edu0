import { api } from "./client.js";

export const listBooks = () => api.get("/library/books");
export const getBook = id => api.get(`/library/books/${id}`);
export const createBook = data => api.post("/library/books", data);
export const listBookChapters = bookId => api.get(`/library/books/${bookId}/chapters`);
export const createBookChapter = (bookId, data) => api.post(`/library/books/${bookId}/chapters`, data);
