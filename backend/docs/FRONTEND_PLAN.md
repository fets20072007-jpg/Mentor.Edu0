# Mentor.Edu ? Plano do Frontend

## Decis?o tecnol?gica

O frontend continuar? utilizando:

- HTML5
- CSS3
- JavaScript ES Modules
- Fetch API
- LocalStorage para sess?o local

N?o ser? utilizado React ou outro framework nesta etapa.

Motivos:

- o frontend atual j? possui autentica??o funcional;
- n?o existem depend?ncias npm;
- implanta??o permanece simples;
- boa parte do design atual pode ser reutilizada;
- JavaScript modular ? suficiente para separar as funcionalidades.

---

# Estado atual

O frontend demonstrativo V3 j? possui:

- tela de login;
- POST /auth/login;
- GET /users/me;
- identifica??o autom?tica de perfil;
- sidebar;
- topbar;
- dashboards demonstrativos;
- telas para os quatro perfis;
- modo demonstra??o;
- CSS responsivo;
- componentes visuais b?sicos.

O principal problema atual ? estrutural:

`app.js`

concentra estado, autentica??o, navega??o, componentes e p?ginas.

A pr?xima etapa ser? modularizar essa estrutura.

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

# Autentica??o

Fluxo oficial:

Login
? POST /auth/login
? JWT
? GET /users/me
? identifica??o de tipo
? carregamento da interface correspondente

O usu?rio n?o selecionar? perfil.

Perfis reconhecidos:

- Aluno
- Professor
- Administracao
- Suporte

O token continuar? sendo enviado como:

Authorization: Bearer TOKEN

---

# Cliente da API

Todas as requisi??es ser?o centralizadas em:

`js/api/client.js`

Esse m?dulo ser? respons?vel por:

- URL base da API;
- token JWT;
- headers;
- tratamento de erro HTTP;
- respostas JSON;
- logout em caso de 401.

As p?ginas n?o dever?o chamar `fetch()` diretamente.

---

# Estado global

`state.js` armazenar?:

- usu?rio atual;
- perfil;
- token;
- p?gina atual;
- modo live/demo;
- informa??es tempor?rias da interface.

---

# Navega??o

A sidebar continuar? sendo gerada conforme o perfil.

O frontend poder? esconder op??es n?o autorizadas.

Por?m:

**a autoriza??o real continuar? sendo responsabilidade do backend.**

---

# Aluno

Menu planejado:

- Vis?o geral
- Disciplinas
- Avalia??es
- Notas
- Frequ?ncia
- Hist?rico
- Plano de estudos
- Biblioteca
- Hor?rios
- Notifica??es
- Chamados
- Perfil

Recursos de IA espec?ficos permanecer?o ocultos enquanto a integra??o
Gemini estiver pendente.

---

# Professor

Menu planejado:

- Vis?o geral
- Minhas turmas
- Disciplinas
- Avalia??es
- Corre??es
- Frequ?ncia
- Notas
- Banco de quest?es
- Desempenho
- Biblioteca
- Hor?rios
- Chamados
- Perfil

DT continuar? sendo uma condi??o do Professor, e n?o um perfil separado.

---

# Administra??o

Menu planejado:

- Vis?o geral
- Usu?rios
- Professores
- Alunos
- Turmas
- Disciplinas
- Matr?culas
- Diretores de Turma
- Hor?rios
- Avalia??es
- Perfil

---

# Suporte

Menu planejado:

- Vis?o geral
- Chamados
- Usu?rios
- Professores
- Estrutura da biblioteca
- Perfil

O Suporte n?o ter? p?ginas de conte?do pedag?gico.

---

# Componentes globais

## Sidebar

Caracter?sticas:

- fixa no desktop;
- recolh?vel no mobile;
- ?cones;
- perfil do usu?rio;
- badges din?micos;
- logout.

## Topbar

Dever? exibir:

- t?tulo da p?gina;
- notifica??es;
- avatar;
- estado da conex?o.

## Notifica??es

Badge atrav?s de:

`GET /notifications/me/unread-count`

## Chamados

Suporte poder? possuir badge atrav?s de:

`GET /tickets/support/pending-count`

---

# Dire??o visual

A interface continuar?:

- ampla;
- limpa;
- com sidebar lateral;
- cards maiores;
- tabelas espa?osas;
- responsiva;
- sem excesso de pequenos cart?es;
- foco em leitura acad?mica.

O design atual ser? utilizado como base, n?o descartado.

---

# Modo demonstra??o

Ser? mantido temporariamente.

Objetivo:

- apresenta??es;
- desenvolvimento visual sem backend;
- demonstra??o de todos os perfis.

O modo demonstra??o nunca substituir? as permiss?es reais do backend.

---

# IA

Status:

PENDENTE.

N?o bloquear? o frontend.

Funcionalidades explicitamente dependentes de Gemini dever?o permanecer
ocultas at? que o m?dulo esteja dispon?vel.

Recursos determin?sticos j? implementados no backend poder?o continuar
existindo normalmente.

---

# Cronograma do frontend

## Dia 15

Planejamento e arquitetura.

## Dia 16

Funda??o do frontend:

- modulariza??o;
- API client;
- autentica??o;
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
- Administra??o;
- Suporte.

## Dia 19

Refinamento:

- responsividade;
- feedback visual;
- loading;
- erros;
- estados vazios;
- acessibilidade;
- consist?ncia visual.

## Dia 20

Integra??o final:

- testes backend/frontend;
- corre??o de endpoints;
- testes por perfil;
- prepara??o para release.

---

# Regra principal

O frontend apresentar? os dados.

O backend continuar? sendo a fonte oficial de:

- autentica??o;
- permiss?es;
- regras acad?micas;
- valida??es;
- seguran?a.

---

# Status

Planejamento do frontend definido.

Pr?xima etapa:

**Dia 16 ? modulariza??o e constru??o da base real do frontend.**
