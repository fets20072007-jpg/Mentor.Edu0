import { API_URL } from "../config.js";
import { ApiError } from "./client.js";

export async function login(email, password) {
    const body = new URLSearchParams();
    body.set("username", email.trim());
    body.set("password", password);

    let response;
    try {
        response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body,
        });
    } catch {
        throw new ApiError("Não foi possível conectar ao servidor. Verifique se o backend está ativo.");
    }

    let data = null;
    try { data = await response.json(); } catch { /* resposta vazia */ }
    if (!response.ok) throw new ApiError(data?.detail || "Credenciais inválidas.", response.status, data);
    return data;
}

export async function requestPasswordReset(email) {
    let response;
    try {
        response = await fetch(`${API_URL}/tickets/forgot-password`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email.trim() }),
        });
    } catch {
        throw new ApiError("Não foi possível enviar a solicitação ao suporte.");
    }
    let data = null; try { data = await response.json(); } catch {}
    if (!response.ok) throw new ApiError(data?.detail || "Não foi possível enviar a solicitação.", response.status, data);
    return data;
}
