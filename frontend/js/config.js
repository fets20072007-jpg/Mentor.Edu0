const isLocalFrontend = ["127.0.0.1", "localhost"].includes(window.location.hostname) && window.location.port === "5500";
const DEFAULT_API_URL = isLocalFrontend ? "http://127.0.0.1:8000" : window.location.origin;
export const API_URL = (localStorage.getItem("mentor_api_url") || DEFAULT_API_URL).replace(/\/$/, "");

export const FEATURES = Object.freeze({
    socialLogin: false,
    ai: false,
    demoMode: false,
});
