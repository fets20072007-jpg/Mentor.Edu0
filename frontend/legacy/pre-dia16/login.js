const API_URL = "http://127.0.0.1:8000";


const loginForm =
    document.getElementById("loginForm");

const emailInput =
    document.getElementById("email");

const passwordInput =
    document.getElementById("password");

const loginButton =
    document.getElementById("loginButton");

const loginMessage =
    document.getElementById("loginMessage");

const togglePassword =
    document.getElementById("togglePassword");


/* =====================================================
   MOSTRAR / ESCONDER SENHA
===================================================== */

togglePassword.addEventListener(
    "click",
    () => {

        const isPassword =
            passwordInput.type === "password";

        passwordInput.type =
            isPassword
                ? "text"
                : "password";

        togglePassword.textContent =
            isPassword
                ? "Ocultar"
                : "Ver";
    }
);


/* =====================================================
   MENSAGEM
===================================================== */

function showMessage(
    message,
    type
) {

    loginMessage.textContent =
        message;

    loginMessage.className =
        `login-message ${type}`;
}


/* =====================================================
   LOGIN
===================================================== */

loginForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        loginMessage.className =
            "login-message";

        const email =
            emailInput.value.trim();

        const password =
            passwordInput.value;


        if (!email || !password) {

            showMessage(
                "Preencha o e-mail e a senha.",
                "error"
            );

            return;
        }


        loginButton.disabled = true;

        loginButton.textContent =
            "Entrando...";


        try {

            /* ==========================================
               OAuth2PasswordRequestForm
            ========================================== */

            const formData =
                new URLSearchParams();

            formData.append(
                "username",
                email
            );

            formData.append(
                "password",
                password
            );


            const response = await fetch(
                `${API_URL}/auth/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/x-www-form-urlencoded"
                    },

                    body: formData
                }
            );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Não foi possível realizar o login."
                );
            }


            /* ==========================================
               SALVA TOKEN
            ========================================== */

            localStorage.setItem(
                "access_token",
                data.access_token
            );


            /* ==========================================
               BUSCA USUÁRIO LOGADO
            ========================================== */

            const userResponse =
                await fetch(
                    `${API_URL}/users/me`,
                    {
                        headers: {
                            Authorization:
                                `Bearer ${data.access_token}`
                        }
                    }
                );


            if (!userResponse.ok) {

                localStorage.removeItem(
                    "access_token"
                );

                throw new Error(
                    "Não foi possível carregar o perfil."
                );
            }


            const user =
                await userResponse.json();


            localStorage.setItem(
                "mentor_user",
                JSON.stringify(user)
            );


            showMessage(
                `Bem-vindo, ${user.nome}!`,
                "success"
            );


            /* ==========================================
               REDIRECIONA
            ========================================== */

            setTimeout(
                () => {

                    window.location.href =
                        "dashboard.html";

                },
                500
            );

        }

        catch (error) {

            showMessage(
                error.message,
                "error"
            );

        }

        finally {

            loginButton.disabled =
                false;

            loginButton.textContent =
                "Entrar";
        }
    }
);