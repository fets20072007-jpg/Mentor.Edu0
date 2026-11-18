const TOKEN_KEY = "mentor_token";
const LEGACY_TOKEN_KEY = "access_token";
const USER_KEY = "mentor_user";

function activeStorage() {
    if (sessionStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(LEGACY_TOKEN_KEY)) return sessionStorage;
    return localStorage;
}

export function getToken() {
    return sessionStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(LEGACY_TOKEN_KEY) || localStorage.getItem(TOKEN_KEY) || localStorage.getItem(LEGACY_TOKEN_KEY) || "";
}

export function setSession(token, user = null, { persistent = true } = {}) {
    const storage = persistent ? localStorage : sessionStorage;
    const other = persistent ? sessionStorage : localStorage;
    other.removeItem(TOKEN_KEY);
    other.removeItem(LEGACY_TOKEN_KEY);
    other.removeItem(USER_KEY);
    storage.setItem(TOKEN_KEY, token);
    storage.setItem(LEGACY_TOKEN_KEY, token);
    if (user) storage.setItem(USER_KEY, JSON.stringify(user));
}

export function setCachedUser(user) {
    activeStorage().setItem(USER_KEY, JSON.stringify(user));
}

export function getCachedUser() {
    try {
        return JSON.parse(activeStorage().getItem(USER_KEY) || "null");
    } catch {
        return null;
    }
}

export function clearSession() {
    [localStorage, sessionStorage].forEach(storage => {
        storage.removeItem(TOKEN_KEY);
        storage.removeItem(LEGACY_TOKEN_KEY);
        storage.removeItem(USER_KEY);
    });
}

export function hasSession() {
    return Boolean(getToken());
}
