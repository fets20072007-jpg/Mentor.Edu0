# Mentor.Edu — Plano do Frontend

## Decisão tecnológica

O frontend continuará utilizando:

- HTML5
- CSS3
- JavaScript ES Modules
- Fetch API
- LocalStorage para sessão local

Não será utilizado React ou outro framework nesta etapa.

Motivos:

- o frontend atual já possui autenticação funcional;
- não existem dependências npm;
- implantação permanece simples;
- boa parte do design atual pode ser reutilizada;
- JavaScript modular é suficiente para separar as funcionalidades.

---

# Estado atual

O frontend demonstrativo V3 já possui:

- tela de login;
- POST /auth/login;
- GET /users/me;
- identificação automática de perfil;
- sidebar;
- topbar;
- dashboards demonstrativos;
- telas para os quatro perfis;
- modo demonstração;
- CSS responsivo;
- componentes visuais básicos.

O principal problema atual é estrutural:

`app.js`

concentra estado, autenticação, navegação, componentes e páginas.

A próxima etapa será modularizar essa estrutura.

---

# Arquitetura planejada

frontend/

    index.html

    css/
        tokens.css
        base.css
        layout.css
        components.css
        pages.css
        responsive.css

    js/
        main.js
        config.js
        state.js

        core/
            router.js
            permissions.js

        api/
            client.js
            auth.js
            users.js
            assessments.js
            attendance.js
            grades.js
            classrooms.js
            subjects.js
            enrollments.js
            schedules.js
            library.js
            notifications.js
            tickets.js

        components/
            sidebar.js
            topbar.js
            toast.js
            modal.js
            metric.js
            panel.js
            table.js
            status.js

        pages/

            shared/
                profile.js
                notifications.js
                tickets.js

            student/
                dashboard.js
                subjects.js
                assessments.js
                grades.js
                attendance.js
                record.js
                study.js
                library.js
                schedule.js

            teacher/
                dashboard.js
                classrooms.js
                assessments.js
                attendance.js
                grades.js
                question-bank.js
                analytics.js
                library.js

            admin/
                dashboard.js
                users.js
                teachers.js
                students.js
                classrooms.js
                subjects.js
                enrollments.js
                dt.js
                schedules.js

            support/
                dashboard.js
                tickets.js
                users.js
                library.js

        demo/
            demo-data.js

---

# Autenticação

Fluxo oficial:

Login
→ POST /auth/login
→ JWT
→ GET /users/me
→ identificação de tipo
→ carregamento da interface correspondente

O usuário não selecionará perfil.

Perfis reconhecidos:

- Aluno
- Professor
- Administracao
- Suporte

O token continuará sendo enviado como:

Authorization: Bearer TOKEN

---

# Cliente da API

Todas as requisições serão centralizadas em:

`js/api/client.js`

Esse módulo será responsável por:

- URL base da API;
- token JWT;
- headers;
- tratamento de erro HTTP;
- respostas JSON;
- logout em caso de 401.

As páginas não deverão chamar `fetch()` diretamente.

---

# Estado global

`state.js` armazenará:

- usuário atual;
- perfil;
- token;
- página atual;
- modo live/demo;
- informações temporárias da interface.

---

# Navegação

A sidebar continuará sendo gerada conforme o perfil.

O frontend poderá esconder opções não autorizadas.

Porém:

**a autorização real continuará sendo responsabilidade do backend.**

---

# Aluno

Menu planejado:

- Visão geral
- Disciplinas
- Avaliações
- Notas
- Frequência
- Histórico
- Plano de estudos
- Biblioteca
- Horários
- Notificações
- Chamados
- Perfil

Recursos de IA específicos permanecerão ocultos enquanto a integração
Gemini estiver pendente.

---

# Professor

Menu planejado:

- Visão geral
- Minhas turmas
- Disciplinas
- Avaliações
- Correções
- Frequência
- Notas
- Banco de questões
- Desempenho
- Biblioteca
- Horários
- Chamados
- Perfil

DT continuará sendo uma condição do Professor, e não um perfil separado.

---

# Administração

Menu planejado:

- Visão geral
- Usuários
- Professores
- Alunos
- Turmas
- Disciplinas
- Matrículas
- Diretores de Turma
- Horários
- Avaliações
- Perfil

---

# Suporte

Menu planejado:

- Visão geral
- Chamados
- Usuários
- Professores
- Estrutura da biblioteca
- Perfil

O Suporte não terá páginas de conteúdo pedagógico.

---

# Componentes globais

## Sidebar

Características:

- fixa no desktop;
- recolhível no mobile;
- ícones;
- perfil do usuário;
- badges dinâmicos;
- logout.

## Topbar

Deverá exibir:

- título da página;
- notificações;
- avatar;
- estado da conexão.

## Notificações

Badge através de:

`GET /notifications/me/unread-count`

## Chamados

Suporte poderá possuir badge através de:

`GET /tickets/support/pending-count`

---

# Direção visual

A interface continuará:

- ampla;
- limpa;
- com sidebar lateral;
- cards maiores;
- tabelas espaçosas;
- responsiva;
- sem excesso de pequenos cartões;
- foco em leitura acadêmica.

O design atual será utilizado como base, não descartado.

---

# Modo demonstração

Será mantido temporariamente.

Objetivo:

- apresentações;
- desenvolvimento visual sem backend;
- demonstração de todos os perfis.

O modo demonstração nunca substituirá as permissões reais do backend.

---

# IA

Status:

PENDENTE.

Não bloqueará o frontend.

Funcionalidades explicitamente dependentes de Gemini deverão permanecer
ocultas até que o módulo esteja disponível.

Recursos determinísticos já implementados no backend poderão continuar
existindo normalmente.

---

# Cronograma do frontend

## Dia 15

Planejamento e arquitetura.

## Dia 16

Fundação do frontend:

- modularização;
- API client;
- autenticação;
- state;
- router;
- sidebar;
- topbar;
- componentes compartilhados.

## Dia 17

Frontend do Aluno.

## Dia 18

Frontend de:

- Professor;
- Administração;
- Suporte.

## Dia 19

Refinamento:

- responsividade;
- feedback visual;
- loading;
- erros;
- estados vazios;
- acessibilidade;
- consistência visual.

## Dia 20

Integração final:

- testes backend/frontend;
- correção de endpoints;
- testes por perfil;
- preparação para release.

---

# Regra principal

O frontend apresentará os dados.

O backend continuará sendo a fonte oficial de:

- autenticação;
- permissões;
- regras acadêmicas;
- validações;
- segurança.

---

# Status

Planejamento do frontend definido.

Próxima etapa:

**Dia 16 — modularização e construção da base real do frontend.**
