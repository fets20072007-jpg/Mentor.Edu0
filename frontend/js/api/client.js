import { API_URL } from "../config.js";
import { clearSession, getToken } from "../core/session.js";

export class ApiError extends Error {
    constructor(message, status = 0, data = null) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.data = data;
    }
}

function redirectToLogin() {
    clearSession();
    if (!location.pathname.endsWith("index.html") && !location.pathname.endsWith("/")) {
        location.replace("index.html");
    }
}

async function parseResponse(response) {
    if (response.status === 204) return null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) return response.json();
    return response.text();
}

export async function apiRequest(path, options = {}) {
    const headers = new Headers(options.headers || {});
    const token = getToken();

    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (options.body && !(options.body instanceof FormData) && !(options.body instanceof URLSearchParams) && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    let response;
    try {
        response = await fetch(`${API_URL}${path}`, { ...options, headers });
    } catch {
        throw new ApiError("Não foi possível conectar ao servidor. Verifique se o backend está ativo.");
    }

    const data = await parseResponse(response);

    if (response.status === 401) {
        redirectToLogin();
        throw new ApiError("Sua sessão expirou. Entre novamente.", 401, data);
    }

    if (!response.ok) {
        const detail = data && typeof data === "object" ? data.detail : null;
        throw new ApiError(detail || `Erro ${response.status} ao acessar o servidor.`, response.status, data);
    }

    return data;
}

export const api = {
    get: (path, options = {}) => apiRequest(path, { ...options, method: "GET" }),
    post: (path, body, options = {}) => apiRequest(path, { ...options, method: "POST", body: body instanceof URLSearchParams || body instanceof FormData ? body : JSON.stringify(body) }),
    put: (path, body, options = {}) => apiRequest(path, { ...options, method: "PUT", body: JSON.stringify(body) }),
    patch: (path, body, options = {}) => apiRequest(path, { ...options, method: "PATCH", body: JSON.stringify(body) }),
    delete: (path, options = {}) => apiRequest(path, { ...options, method: "DELETE" }),
};
