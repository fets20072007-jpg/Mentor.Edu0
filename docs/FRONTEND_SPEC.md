# Mentor.Edu — Especificação Oficial do Frontend

## 1. Objetivo deste documento

Este arquivo é a referência principal para o desenvolvimento do frontend do Mentor.Edu.

Ele reúne:

- decisões visuais aprovadas;
- identidade por perfil;
- comportamento da navegação;
- estrutura técnica do frontend;
- integração com o backend existente;
- regras de permissão que não podem ser quebradas;
- telas prioritárias;
- estados de carregamento, vazio e erro;
- decisões que ainda estão pendentes.

Sempre que houver conflito entre protótipos antigos e este documento, este documento deve prevalecer para o frontend novo.

---

# 2. Estado atual do projeto

## Backend

O backend principal está concluído para integração com o frontend, desconsiderando apenas a futura integração de IA.

Stack atual:

- FastAPI;
- SQLAlchemy;
- SQLite;
- JWT;
- OAuth2 Password Flow;
- Pydantic;
- Uvicorn.

O backend possui cerca de 145 rotas registradas e já cobre os principais fluxos acadêmicos, institucionais e operacionais.

## IA

Status:

**PENDENTE — aguardando implementação do colaborador.**

A IA não bloqueia o desenvolvimento do frontend.

Nenhuma tela deve depender obrigatoriamente da IA para funcionar nesta etapa.

---

# 3. Situação real do frontend recebido no ZIP

O ZIP contém mais de uma geração de frontend.

## Fluxo atualmente utilizado por `index.html`

O fluxo ativo atual usa:

- `frontend/index.html`
- `frontend/dashboard.html`
- `frontend/css/style.css`
- `frontend/js/login.js`
- `frontend/js/dashboard.js`

O `index.html` referencia `css/style.css` e `js/login.js`.

O `dashboard.html` referencia `css/style.css` e `js/dashboard.js`.

## Protótipos paralelos encontrados

Também existem:

- `frontend/app.js`
- `frontend/styles.css`
- `frontend/src/app.js`
- `frontend/src/styles.css`

Esses arquivos representam versões/protótipos paralelos e **não devem ser misturados automaticamente com o fluxo oficial atual**.

Antes de remover qualquer um deles, deverá existir checkpoint no Git e confirmação de que nenhuma funcionalidade útil ficou apenas nesses arquivos.

---

# 4. Decisão tecnológica do frontend

O frontend continuará, nesta fase, com:

- HTML5;
- CSS3;
- JavaScript ES Modules;
- Fetch API;
- LocalStorage para sessão local.

Não será usado React/Vite agora.

Motivos:

- o projeto já possui frontend funcional em HTML/CSS/JS;
- o login já está integrado ao backend;
- não há necessidade de reescrever a base apenas para trocar de tecnologia;
- JavaScript modular é suficiente para organizar o sistema;
- implantação e execução local permanecem simples.

---

# 5. Estrutura técnica alvo

A estrutura final recomendada é:

```text
frontend/
├── index.html
├── dashboard.html
├── assets/
│   ├── brand/
│   │   └── logo-mentor-edu.png
│   └── icons/
├── css/
│   ├── tokens.css
│   ├── base.css
│   ├── layout.css
│   ├── components.css
│   ├── pages.css
│   └── responsive.css
└── js/
    ├── main.js
    ├── config.js
    ├── state.js
    ├── core/
    │   ├── router.js
    │   ├── permissions.js
    │   └── session.js
    ├── api/
    │   ├── client.js
    │   ├── auth.js
    │   ├── users.js
    │   ├── classrooms.js
    │   ├── subjects.js
    │   ├── enrollments.js
    │   ├── assessments.js
    │   ├── answers.js
    │   ├── grades.js
    │   ├── attendance.js
    │   ├── schedules.js
    │   ├── library.js
    │   ├── notifications.js
    │   └── tickets.js
    ├── components/
    │   ├── sidebar.js
    │   ├── topbar.js
    │   ├── toast.js
    │   ├── modal.js
    │   ├── card.js
    │   ├── table.js
    │   ├── badge.js
    │   ├── empty-state.js
    │   └── loading.js
    └── pages/
        ├── shared/
        ├── student/
        ├── teacher/
        ├── admin/
        └── support/
```

Regra técnica:

**As páginas não devem chamar `fetch()` diretamente.**

Toda requisição deve passar pelo cliente central em `js/api/client.js`.

---

# 6. Identidade oficial do Mentor.Edu

## Nome

Usar exatamente:

**Mentor.Edu**

Regras:

- manter o ponto;
- `M` maiúsculo;
- `E` maiúsculo;
- `d` minúsculo;
- `u` minúsculo.

## Logo oficial

A logo escolhida é a versão minimalista quadrada com:

- personagem/mentor simples;
- óculos;
- linguagem educacional;
- composição limpa;
- aparência amigável;
- leitura boa em tamanhos pequenos;
- wordmark `Mentor.Edu` proporcional ao ícone.

Uso recomendado:

- login;
- topo da sidebar;
- favicon/ícone adaptado futuramente;
- loading institucional;
- material de apresentação.

Não criar uma nova logo sem necessidade.

---

# 7. Princípios visuais gerais

O sistema deve parecer:

- moderno;
- minimalista;
- acadêmico;
- organizado;
- profissional;
- leve;
- com bastante espaço em branco;
- sem excesso de informação na home.

## Regra principal das dashboards

A dashboard inicial deve funcionar como **porta de entrada**, não como página de relatório completo.

Evitar:

- listas longas;
- tabelas gigantes;
- excesso de gráficos;
- muitos números simultâneos;
- várias pendências abertas na tela;
- conteúdo detalhado que poderia estar em uma tela própria.

Preferir:

- ícone;
- título curto;
- informação resumida opcional;
- ação `Ver`.

Quando o usuário quiser detalhes, ele clica em:

**Ver**

Isso abre a página/subpágina específica.

---

# 8. Sistema visual por perfil

Cada perfil terá identidade própria sem parecer outro sistema.

A estrutura, tipografia, espaçamento, componentes e comportamento permanecem consistentes.

A cor muda para ajudar o usuário a reconhecer o contexto.

## Administração

Identidade:

- azul escuro/navy;
- visual institucional;
- sidebar escura;
- área principal clara;
- sensação de controle e gestão.

Sugestão de tokens:

```css
--admin-primary: #18375F;
--admin-primary-strong: #102A4C;
--admin-primary-soft: #EAF1F8;
--admin-accent: #2E6FA8;
```

## Aluno

Identidade:

- fundo bege/claro;
- sidebar roxa;
- visual acolhedor;
- foco em organização pessoal.

Sugestão:

```css
--student-bg: #F5EFE4;
--student-surface: #FFFDFC;
--student-primary: #6D4BC3;
--student-primary-strong: #5635A6;
--student-primary-soft: #EFE9FC;
```

## Professor

Identidade:

- verde inspirado no IF;
- visual pedagógico/profissional;
- dashboard simples;
- ações de sala de aula em destaque.

Sugestão:

```css
--teacher-primary: #278447;
--teacher-primary-strong: #176A35;
--teacher-primary-soft: #E8F5EC;
--teacher-accent: #42A85F;
```

## Suporte

O design do Suporte fica livre, mas deve seguir a mesma linguagem visual.

Direção escolhida:

- grafite/slate;
- acento ciano/azul técnico;
- aparência operacional;
- sem aparência pedagógica.

Sugestão:

```css
--support-primary: #1F2937;
--support-primary-strong: #111827;
--support-accent: #0891B2;
--support-soft: #ECFEFF;
```

---

# 9. Login oficial

O login aprovado usa a linguagem visual azul apresentada nos designs.

## Estrutura

Desktop:

- área institucional/branding;
- logo Mentor.Edu;
- texto curto de apresentação;
- formulário limpo;
- e-mail;
- senha;
- botão Entrar.

Não perguntar o perfil.

Fluxo correto:

```text
Login
→ POST /auth/login
→ JWT
→ GET /users/me
→ identificar tipo
→ abrir painel correspondente
```

## Login social

Desejo visual do produto:

- Google;
- Microsoft.

Porém, o backend atual **não possui integração OAuth Google/Microsoft pronta**.

Regra:

- não simular login social falso;
- não criar botão que pareça funcional sem backend correspondente;
- os botões podem ser preparados visualmente e controlados por feature flag;
- só ativar quando houver endpoints e credenciais OAuth oficiais.

Sugestão futura:

```text
Continuar com Google
Continuar com Microsoft
```

Contas institucionais Microsoft/Hotmail poderão ser suportadas quando o fluxo OAuth estiver implementado no backend.

---

# 10. Layout global autenticado

Todas as áreas autenticadas devem compartilhar:

- sidebar fixa no desktop;
- sidebar recolhível no mobile;
- topbar;
- avatar;
- nome e perfil;
- notificações;
- título da página;
- área principal ampla.

## Dashboard

A dashboard inicial deve ter poucos elementos.

Formato recomendado:

1. saudação curta;
2. 3–4 indicadores realmente úteis, se necessário;
3. grade de atalhos com ícones;
4. cada atalho com `Ver`;
5. nenhum relatório detalhado aberto por padrão.

---

# 11. Sidebar e subtópicos

A sidebar é uma parte central do produto.

Ela não deve listar dezenas de funções no mesmo nível.

Usar grupos recolhíveis com subtópicos quando fizer sentido.

Exemplo:

```text
Avaliações
  ├── Minhas avaliações
  ├── Criar avaliação
  ├── Correções
  └── Resultados
```

O clique no grupo pode:

- expandir/recolher;
- manter o grupo ativo;
- destacar o subtópico selecionado.

No mobile, abrir em drawer lateral.

---

# 12. Dashboard da Administração — aprovado

## Cor

Azul escuro.

## Home

Manter minimalista.

Pode mostrar:

- Usuários;
- Turmas;
- Avaliações;
- Chamados abertos;
- gráfico institucional resumido;
- Ações rápidas.

Conteúdos como:

- pendências;
- atenção;
- atualizações recentes;
- relatórios detalhados;

não devem ficar totalmente expostos na tela inicial.

Devem aparecer como módulo compacto com:

- ícone;
- título;
- botão `Ver`.

## Sidebar recomendada

```text
Início

Pessoas
  ├── Usuários
  ├── Alunos
  └── Professores

Acadêmico
  ├── Turmas
  ├── Disciplinas
  ├── Matrículas
  ├── Diretores de Turma
  └── Horários

Avaliações
  ├── Avaliações
  ├── Frequência
  └── Notas

Relatórios
  ├── Resumo institucional
  ├── Turmas
  └── Avaliações

Perfil
```

## Backend principal

- `GET /admin/summary`
- `GET /admin/teachers`
- `GET /admin/students`
- `GET /admin/classrooms`
- `GET /admin/assessments`
- `POST /classrooms`
- `GET /classrooms`
- `PATCH /classrooms/{classroom_id}/dt`
- `GET /classrooms/{classroom_id}/teachers`
- `POST /subjects`
- `GET /subjects`
- `PATCH /subjects/{subject_id}/teacher`
- `POST /enrollments`
- `GET /enrollments`
- `PATCH /enrollments/student/{student_id}/classroom`
- CRUD de horários via `/schedules`.

---

# 13. Dashboard do Aluno — aprovado

## Cor

- fundo bege;
- sidebar roxa.

## Home

Priorizar:

- saudação;
- visão acadêmica resumida;
- cards minimalistas;
- ações com `Ver`.

Não abrir automaticamente detalhes de:

- próximas atividades;
- desempenho por disciplina;
- avaliações;
- frequência;
- notas;
- biblioteca;
- horários;
- recomendações.

Esses itens devem ser módulos compactos.

Exemplo:

```text
[ícone] Avaliações       Ver
[ícone] Notas            Ver
[ícone] Frequência       Ver
[ícone] Horários         Ver
[ícone] Biblioteca       Ver
[ícone] Histórico        Ver
```

## Sidebar recomendada

```text
Início

Minha vida acadêmica
  ├── Disciplinas
  ├── Avaliações
  ├── Notas
  ├── Frequência
  └── Histórico

Organização
  ├── Plano de estudos
  ├── Sessões de estudo
  └── Horários

Conteúdo
  └── Biblioteca

Comunicação
  ├── Notificações
  └── Chamados

Perfil
```

## Backend principal

Dashboard:

- `GET /dashboard/me`
- `GET /performance/me`
- `GET /notifications/me/unread-count`
- `GET /assessments/summary/me`

Acadêmico:

- `GET /subjects/me`
- `GET /enrollments/me`
- `GET /grades/me`
- `GET /attendance/me`
- `GET /attendance/me/summary`
- `GET /academic-record/me`
- `GET /schedules/me`

Avaliações:

- `GET /assessments/`
- `GET /assessments/{assessment_id}`
- `GET /assessments/{assessment_id}/questions`
- `GET /assessments/{assessment_id}/availability/me`
- `GET /assessments/{assessment_id}/submission/me`
- `POST /answers/questions/{question_id}`
- `GET /assessments/{assessment_id}/results/me`
- `GET /assessments/{assessment_id}/answer-key/me`

---

# 14. Dashboard do Professor — aprovado

## Cor

Verde inspirado no IF.

## Home

Pode conter uma visão curta de:

- turmas;
- avaliações;
- frequência;
- correções pendentes.

Mas evitar listas detalhadas.

Módulos como:

- Minhas turmas;
- Avaliações;
- Banco de questões;
- Frequência;
- Notas;
- Desempenho;
- Biblioteca;
- Horários;
- Pendências;

ficam em cards com:

- ícone;
- nome;
- `Ver`.

## Sidebar recomendada

```text
Início

Turmas
  ├── Minhas turmas
  ├── Minhas disciplinas
  └── Alunos

Avaliações
  ├── Avaliações
  ├── Criar avaliação
  ├── Correções
  ├── Resultados
  └── Banco de questões

Acompanhamento
  ├── Frequência
  ├── Notas
  ├── Desempenho
  └── Histórico de aluno

Recursos
  ├── Biblioteca
  └── Horários

Comunicação
  └── Chamados

Perfil
```

## DT

Diretor de Turma **não é um perfil separado**.

É uma condição adicional do Professor.

Quando o backend indicar que o professor é DT de uma turma, algumas telas podem liberar leitura ampliada daquela turma.

O frontend não deve conceder essas permissões por conta própria.

## Backend principal

- `GET /teachers/me/classrooms`
- `GET /subjects/me`
- `GET /enrollments/classroom/{classroom_id}`
- `POST /assessments`
- `GET /assessments/`
- `PATCH /assessments/{assessment_id}`
- `POST /assessments/{assessment_id}/questions`
- `GET /assessments/{assessment_id}/questions/teacher`
- `PATCH /assessments/{assessment_id}/access`
- `GET /answers/teacher/pending`
- `PATCH /answers/{answer_id}/review`
- `POST /grades`
- `GET /grades/assessment/{assessment_id}`
- `PATCH /grades/{grade_id}`
- `POST /attendance/`
- `GET /attendance/teacher/me`
- `GET /attendance/teacher/pending`
- `PATCH /attendance/{attendance_id}`
- endpoints de análise de desempenho do professor.

---

# 15. Dashboard do Suporte — especificação proposta

O Suporte deverá seguir o mesmo padrão minimalista.

## Home

Mostrar apenas atalhos operacionais:

```text
[ícone] Chamados pendentes     Ver
[ícone] Usuários               Ver
[ícone] Professores            Ver
[ícone] Estrutura da biblioteca Ver
[ícone] Meu perfil             Ver
```

Um pequeno indicador de chamados pendentes pode aparecer na home e como badge na sidebar.

Não mostrar:

- notas;
- desempenho acadêmico;
- respostas de alunos;
- conteúdo pedagógico protegido;
- histórico acadêmico.

## Sidebar recomendada

```text
Início

Atendimento
  ├── Chamados
  └── Pendentes

Contas
  ├── Usuários
  └── Professores

Biblioteca
  ├── Livros
  └── Capítulos

Perfil
```

## Backend principal

- `GET /tickets/support/pending-count`
- `GET /tickets`
- `PATCH /tickets/{ticket_id}/status`
- `GET /users/`
- `POST /users/register`
- `GET /teachers`
- `POST /library/books`
- `POST /library/books/{book_id}/chapters`

Regra crítica:

**Suporte não acessa conteúdo pedagógico protegido.**

---

# 16. Componentes reutilizáveis obrigatórios

## Card de atalho

Conteúdo:

- ícone;
- título;
- opcionalmente uma informação curta;
- ação `Ver`.

## Card de indicador

Usar apenas quando o número realmente ajuda a leitura rápida.

Exemplos:

- avaliações abertas;
- chamados pendentes;
- turmas ativas.

## Tabelas

Usar em páginas internas, não na home quando possível.

Características:

- cabeçalho claro;
- filtros;
- busca quando necessário;
- paginação se houver muitos registros;
- ações no final da linha;
- estado vazio.

## Modal

Usar para ações curtas:

- confirmação;
- edição simples;
- seleção.

Não colocar fluxos acadêmicos longos dentro de modais.

## Toast

Usar para:

- sucesso;
- erro;
- alerta;
- confirmação de ação.

---

# 17. Estados obrigatórios de interface

Toda página conectada ao backend deverá prever:

## Loading

Nunca deixar tela em branco durante requisição.

## Empty state

Exemplo:

```text
Nenhuma avaliação encontrada.
```

Adicionar ação útil quando fizer sentido.

## Erro

Mostrar mensagem compreensível ao usuário.

Não exibir traceback ou detalhes internos do backend.

## 401

Ao receber 401:

- limpar sessão local;
- redirecionar para login.

## 403

Mostrar acesso negado sem quebrar a aplicação.

## 404

Mostrar recurso não encontrado.

---

# 18. Cliente central da API

Criar um cliente único.

Responsabilidades:

- URL base;
- Bearer token;
- JSON;
- FormData quando necessário;
- tratamento de erros;
- logout automático em 401.

Exemplo conceitual:

```js
api.get('/users/me')
api.post('/assessments', body)
api.patch('/grades/1', body)
```

Evitar chamadas `fetch()` espalhadas em cada página.

---

# 19. Sessão e segurança no frontend

O frontend pode ocultar menus conforme o perfil.

Mas isso é apenas UX.

A segurança verdadeira pertence ao backend.

Nunca assumir que esconder um botão equivale a bloquear acesso.

O perfil deve vir de:

`GET /users/me`

Não confiar em um perfil escolhido pelo usuário no navegador.

---

# 20. Notificações e badges

Notificações do usuário:

`GET /notifications/me/unread-count`

Mostrar badge discreto na topbar/sidebar.

Suporte:

`GET /tickets/support/pending-count`

Mostrar badge no grupo Chamados.

Badges devem ser dinâmicos.

---

# 21. Biblioteca

## Aluno / Professor / Administração

Podem navegar pela biblioteca pedagógica conforme permissões do backend.

Estrutura visual:

```text
Livros
→ Capítulos
→ Conteúdos
   ├── Exercícios
   ├── Vídeos
   ├── PDFs
   └── Exemplos
```

## Suporte

Foco em estrutura operacional permitida:

- livros;
- capítulos.

Não apresentar automaticamente conteúdo pedagógico protegido ao Suporte.

---

# 22. Avaliações

A interface deve respeitar:

- abertura;
- encerramento;
- liberação de prova;
- liberação de resultado;
- liberação de gabarito.

O aluno não deve ver informações antes da autorização fornecida pelo backend.

Professor terá páginas específicas para:

- criar;
- editar;
- questões;
- correções;
- resultados;
- liberação.

---

# 23. Frequência

Aluno:

- visão pessoal;
- resumo;
- justificativas.

Professor:

- lançamento;
- pendências;
- turma;
- edição respeitando regra de 24h.

Administração:

- visão institucional autorizada.

---

# 24. Perfil

Todos os perfis terão página de perfil.

Endpoints:

- `GET /users/me`
- `PUT /users/me`
- `DELETE /users/me`

O `DELETE /users/me` realiza desativação lógica da conta no backend.

A interface deve deixar claro que a conta será desativada.

---

# 25. Responsividade

Prioridade inicial:

1. desktop;
2. notebook;
3. tablet;
4. mobile.

No mobile:

- sidebar vira drawer;
- cards empilham;
- tabelas usam scroll horizontal ou visual alternativo;
- ações principais permanecem acessíveis;
- evitar textos muito pequenos.

---

# 26. Acessibilidade mínima

Obrigatório:

- contraste adequado;
- foco visível no teclado;
- labels em formulários;
- `aria-label` em botões apenas com ícone;
- não depender apenas de cor para status;
- botões com área clicável confortável;
- mensagens de erro legíveis.

---

# 27. IA no frontend

Status:

**não implementar integração definitiva agora.**

Quando o backend de IA estiver pronto:

- adicionar cliente próprio;
- adicionar telas/atalhos autorizados;
- preservar as mesmas regras de acesso;
- nunca enviar ao modelo dados que o usuário não poderia consultar pelo backend normal.

Enquanto isso:

- ocultar módulos exclusivamente dependentes de IA;
- manter recursos determinísticos existentes.

---

# 28. O que deve ser preservado do frontend atual

Preservar como base funcional:

- login real;
- `POST /auth/login`;
- `GET /users/me`;
- token Bearer;
- redirecionamento para dashboard;
- logout;
- lógica de perfil;
- estrutura de sidebar/topbar que puder ser reaproveitada;
- chamadas já compatíveis com endpoints reais.

Reescrever apenas onde necessário para:

- modularizar;
- aplicar o novo design;
- remover duplicação;
- conectar endpoints adicionais;
- melhorar estados de interface.

---

# 29. O que não deve ser feito

Não:

- reescrever o backend sem necessidade;
- criar novas regras de permissão no frontend;
- usar dados fake no fluxo live sem identificar claramente;
- ativar Google/Microsoft sem backend OAuth;
- criar dashboard poluída;
- misturar os três protótipos de frontend encontrados no ZIP;
- apagar código antigo antes de checkpoint e auditoria;
- criar um perfil separado chamado DT;
- permitir ao aluno escolher disciplinas individualmente;
- permitir ao Suporte consultar conteúdo pedagógico protegido.

---

# 30. Ordem oficial de implementação

## Etapa 1 — Fundação

- definir arquivos canônicos;
- centralizar API client;
- estado;
- sessão;
- roteamento interno;
- sidebar;
- topbar;
- tokens visuais;
- componentes básicos.

## Etapa 2 — Login

- aplicar design azul aprovado;
- integrar autenticação existente;
- preparar visualmente Google/Microsoft sem ativar OAuth falso.

## Etapa 3 — Aluno

- dashboard minimalista bege/roxa;
- navegação;
- telas acadêmicas;
- integração real.

## Etapa 4 — Professor

- dashboard verde;
- turmas;
- avaliações;
- frequência;
- notas;
- correções;
- análise.

## Etapa 5 — Administração

- dashboard azul escuro;
- gestão institucional;
- turmas;
- disciplinas;
- matrícula;
- DT;
- horários.

## Etapa 6 — Suporte

- dashboard slate/ciano;
- chamados;
- usuários;
- professores;
- estrutura da biblioteca.

## Etapa 7 — Refinamento

- loading;
- erros;
- empty states;
- responsividade;
- acessibilidade;
- badges;
- feedback visual.

## Etapa 8 — Integração final

- testes por perfil;
- teste de permissões;
- correção de endpoints;
- release.

---

# 31. Critérios de aprovação visual

Uma tela está aprovada quando:

- respeita a paleta do perfil;
- usa a logo oficial;
- não apresenta informação demais;
- usa `Ver` para conteúdo detalhado;
- sidebar está organizada por grupos e subtópicos;
- não duplica funcionalidades;
- funciona em desktop e mobile;
- possui loading/erro/vazio;
- está conectada ao endpoint real quando disponível;
- não viola permissões do backend.

---

# 32. Fontes de verdade do desenvolvimento

Ordem de prioridade:

1. regras do backend e permissões;
2. este `FRONTEND_SPEC.md`;
3. `FRONTEND_API_GUIDE.md`;
4. `BACKEND_MAP.md`;
5. designs aprovados na conversa;
6. protótipos antigos apenas como referência de código/visual.

---

# 33. Status final desta especificação

## Aprovado

- logo;
- identidade Administração;
- identidade Aluno;
- identidade Professor;
- direção do Suporte;
- login azul;
- dashboards minimalistas;
- sidebar com subtópicos;
- cards de acesso com `Ver`;
- backend como fonte oficial de permissão;
- HTML/CSS/JavaScript modular como stack desta fase.

## Pendente

- IA;
- OAuth Google;
- OAuth Microsoft;
- designs detalhados das páginas internas além das dashboards;
- refinamentos mobile finais.

## Próximo passo

**Iniciar a fundação do frontend real e conectar os componentes aos endpoints existentes do backend, usando esta especificação como referência.**

---

# 34. Implementação — Dia 16 iniciada

Base modular implementada no frontend real:

- login azul integrado a `POST /auth/login`;
- identificação automática via `GET /users/me`;
- sessão JWT centralizada;
- cliente HTTP em `js/api/client.js`;
- sidebar agrupada com subtópicos por perfil;
- topbar compartilhada;
- badge de notificações via `GET /notifications/me/unread-count`;
- paleta por perfil aplicada por tokens CSS;
- dashboards iniciais minimalistas para Aluno, Professor, Administração e Suporte;
- cards de acesso usando `Ver`;
- layout responsivo inicial;
- protótipos antigos preservados em `frontend/legacy/pre-dia16/`;
- OAuth Google/Microsoft continua desativado por feature flag até existir backend oficial;
- IA continua desativada e não bloqueia o frontend.

As telas internas continuam sendo implementadas nas próximas etapas.

---

# 35. Referências visuais oficiais — atualização do Dia 16

A camada visual do frontend deve seguir as imagens aprovadas e preservadas em:

- `frontend/docs/visual-references/login.png`;
- `frontend/docs/visual-references/dashboard-admin.png`;
- `frontend/docs/visual-references/dashboard-aluno.png`;
- `frontend/docs/visual-references/dashboard-professor.png`.

Regras consolidadas nesta atualização:

- o login usa a mesma lógica visual da referência azul/ciano em duas colunas;
- Google e Microsoft permanecem visíveis no design, porém desativados enquanto OAuth não existir no backend;
- o perfil é identificado automaticamente após `POST /auth/login` + `GET /users/me`;
- dashboards são minimalistas e funcionam como portas de entrada para os módulos;
- a tela inicial não deve exibir listas extensas, gráficos densos ou detalhes de pendências;
- cards do painel principal exibem principalmente ícone, nome curto e ação `Ver`;
- detalhes são carregados apenas ao entrar no módulo correspondente;
- Administração mantém azul-escuro;
- Aluno mantém fundo bege e sidebar roxa;
- Professor mantém verde inspirado na identidade do IF;
- Suporte segue a mesma linguagem, com combinação slate/ciano;
- sidebar mantém subtópicos recolhíveis sempre que a navegação comportar agrupamento;
- topbar segue a referência com título, busca, ano, notificações e identificação do usuário;
- o visual nunca substitui as permissões reais definidas no backend.

A implementação desta etapa prioriza fidelidade visual às referências sem alterar contratos ou regras de autorização da API.
