import { api } from './client.js';
export function uploadFile(file) {
  const form = new FormData();
  form.append('file', file);
  return api.post('/uploads/file', form);
}
