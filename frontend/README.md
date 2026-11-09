# Mentor.Edu — Frontend Demonstrativo V3

## O que mudou nesta versão

- **Tela inicial agora é um login normal**.
- O usuário **não escolhe o perfil** no fluxo principal.
- Após autenticar, o frontend consulta **`/users/me`** e identifica automaticamente se o usuário é:
  - Aluno
  - Professor
  - Administração
  - Suporte
- O modo demonstração continua existindo, mas ficou **secundário**.
- Interface refeita com layout mais estável: sidebar, topbar, cards, tabelas e dashboards por perfil.

## Como abrir

Na pasta `frontend`, execute:

```powershell
python -m http.server 5500
```

Abra no navegador:

```text
http://127.0.0.1:5500
```

## Backend

Fluxo de login usado pelo frontend:

- `POST /auth/login`
- `GET /users/me`

URL padrão da API:

```text
http://127.0.0.1:8000
```

## Observação

O modo demonstração existe apenas para apresentação. O fluxo correto do sistema é o login normal, com redirecionamento automático conforme o perfil retornado pelo backend.
