import { FEATURES } from "./config.js";
import { login } from "./api/auth.js";
import { getMe } from "./api/users.js";
import { clearSession, hasSession, setSession } from "./core/session.js";

function showLoginMessage(message, type = "error") {
    const target = document.getElementById("loginMessage");
    if (!target) return;

    target.textContent = message;
    target.className = `form-message is-visible ${type === "success" ? "is-success" : "is-error"}`;
}

async function bootLogin() {
    console.info("[Mentor.Edu] Login V2.2 iniciado.");

    if (hasSession()) {
        try {
            await getMe();
            location.replace("dashboard.html");
            return;
        } catch (error) {
            console.warn("[Mentor.Edu] Sessão antiga inválida.", error);
            clearSession();
        }
    }

    const social = document.getElementById("socialLoginArea");
    if (social) {
        social.hidden = false;

        social.querySelectorAll("[data-provider]").forEach(button => {
            button.disabled = !FEATURES.socialLogin;

            if (!FEATURES.socialLogin) {
                button.title = "Integração institucional em preparação.";
            }
        });
    }

    const password = document.getElementById("password");
    const toggle = document.getElementById("togglePassword");

    toggle?.addEventListener("click", () => {
        if (!password) return;

        const visible = password.type === "text";
        password.type = visible ? "password" : "text";
        toggle.setAttribute(
            "aria-label",
            visible ? "Mostrar senha" : "Ocultar senha",
        );
    });

    document.getElementById("forgotPassword")?.addEventListener("click", () => {
        showLoginMessage(
            "Para redefinir a senha, procure o suporte da sua instituição.",
            "success",
        );
    });

    const form = document.getElementById("loginForm");
    const button = document.getElementById("loginButton");

    if (!form) {
        console.error("[Mentor.Edu] #loginForm não encontrado.");
        return;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const email = document.getElementById("email")?.value?.trim() || "";
        const pass = password?.value || "";

        if (!email || !pass) {
            showLoginMessage("Preencha o e-mail e a senha.");
            return;
        }

        if (button) {
            button.disabled = true;
            button.textContent = "Entrando...";
        }

        showLoginMessage("Autenticando...", "success");

        try {
            const auth = await login(email, pass);

            if (!auth?.access_token) {
                throw new Error("O servidor não retornou o token de acesso.");
            }

            const persistent = Boolean(
                document.getElementById("rememberMe")?.checked,
            );

            setSession(auth.access_token, null, { persistent });

            const user = await getMe();

            setSession(auth.access_token, user, { persistent });

            showLoginMessage(
                `Bem-vindo, ${user?.nome || "usuário"}!`,
                "success",
            );

            location.replace("dashboard.html");
        } catch (error) {
            console.error("[Mentor.Edu] Falha no login:", error);
            clearSession();

            showLoginMessage(
                error?.message || "Não foi possível entrar.",
            );
        } finally {
            if (button) {
                button.disabled = false;
                button.textContent = "Entrar";
            }
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootLogin, { once: true });
} else {
    bootLogin();
}
