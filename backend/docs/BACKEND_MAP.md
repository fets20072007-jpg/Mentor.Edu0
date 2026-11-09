# Mentor.Edu — Mapa do Backend

## Status

Mapeamento realizado no Dia 13 do desenvolvimento.

- Total de rotas: **145**
- GET: **100**
- POST: **22**
- PATCH: **15**
- PUT: **3**
- DELETE: **5**
- Routers Python: **38**
- Services Python: **47**
- Schemas Python: **53**

---

## Perfis do sistema

### Aluno

Possui acesso aos próprios dados acadêmicos:

- avaliações;
- respostas;
- notas;
- frequência;
- disciplinas;
- matrícula;
- horários;
- histórico acadêmico;
- biblioteca;
- notificações;
- chamados;
- plano de estudos;
- sessões de estudo;
- desempenho;
- recomendações.

### Professor

Responsável pelo trabalho pedagógico:

- disciplinas em que atua;
- turmas relacionadas às disciplinas;
- avaliações;
- questões;
- correções;
- notas;
- frequência;
- análise de desempenho;
- biblioteca pedagógica;
- banco de questões.

### Diretor de Turma — DT

DT não ? um perfil separado.

É um professor definido em:

`Classroom.teacher_id`

O DT pode possuir acesso de leitura ampliado aos dados
acadêmicos dos estudantes da pr?pria turma.

### Administração

Responsável pela gestão institucional:

- usuários;
- professores;
- alunos;
- turmas;
- disciplinas;
- matrículas;
- DT;
- horários;
- avaliações;
- visão acadêmica institucional.

### Suporte

Responsável por funções operacionais:

- criação institucional de usuários;
- professores;
- chamados;
- estrutura da biblioteca.

O Suporte não possui acesso ao conteúdo pedagógico dos alunos.

---

# Módulos ativos

## Autenticação

Prefixo:

`/auth`

Principal endpoint:

- `POST /auth/login`

---

## Usuários

Prefixo:

`/users`

Principais funções:

- cadastro institucional;
- listagem;
- perfil atual;
- edição do perfil;
- desativação lógica da conta.

A exclusão física do usuário não ? utilizada.

---

## Professores

Prefixo:

`/teachers`

Fun??es:

- listagem;
- turmas do professor autenticado;
- turmas de um professor específico.

---

## Turmas

Prefixo:

`/classrooms`

Fun??es:

- cadastro;
- listagem;
- definição de DT;
- professores da turma.

---

## Disciplinas

Prefixo:

`/subjects`

A disciplina pertence a uma turma e possui um professor responsável.

O aluno não seleciona disciplinas individualmente.

Fluxo:

Aluno
? matrícula ativa
→ turma
→ disciplinas da turma

---

## Matr?culas

Prefixo:

`/enrollments`

Responsável pelo vínculo:

Aluno
→ Turma

Existe apenas uma matrícula ativa utilizada como refer?ncia
acadêmica principal.

---

## Frequ?ncia

Prefixo:

`/attendance`

Possui:

- lançamento por professor;
- consulta do aluno;
- resumo;
- pendências do professor;
- consulta por turma;
- justificativa;
- edição limitada.

A edição realizada pelo professor possui regra temporal de 24 horas.

---

## Avalia??es

Prefixo:

`/assessments`

É um dos maiores módulos do sistema.

Possui:

- criação;
- edição;
- questões;
- resultados;
- histórico;
- resumo;
- evolução;
- análise de dificuldade;
- desempenho por estudante;
- configuração de disponibilidade.

Campos de liberação:

- `data_abertura`
- `data_encerramento`
- `liberar_resultado`
- `liberar_prova`
- `liberar_gabarito`

---

## Respostas

Prefixo:

`/answers`

Possui:

- resposta do aluno;
- histórico próprio;
- pendências do professor;
- revisão manual.

Questáes subjetivas podem receber avaliação parcial.

---

## Notas

Prefixo:

`/grades`

Possui:

- registro;
- notas do aluno;
- notas por avaliação;
- visão administrativa;
- edição;
- consulta individual.

---

## Hist?rico acadêmico

Prefixo:

`/academic-record`

Permite:

- aluno consultar o próprio histórico;
- professor/DT consultar alunos autorizados;
- Administração consultar institucionalmente.

---

## Analytics

Prefixo:

`/analytics`

Atualmente possui cálculo de média acadêmica.

Outros módulos relacionados:

- `/performance`
- `/dashboard`
- `/recommendations`

---

## Biblioteca

Prefixo:

`/library`

Estrutura ativa:

Book
→ Chapter
→ Exercise / Video / PDF / PracticalExample

Também existe banco de questões do professor.

### Permissões

Aluno, Professor e Administração:

- leitura pedagógica.

Professor:

- criação de conteúdos pedagógicos autorizados.

Suporte:

- administração estrutural de livros/cap?tulos;
- sem acesso ao conteúdo pedagógico protegido.

---

## Hor?rios

Prefixo:

`/schedules`

Modelo:

`ClassSchedule`

Campos principais:

- dia da semana;
- hora inicial;
- hora final;
- disciplina;
- ativo.

Possui validação de conflito de turma e professor.

---

## Notifica??es

Prefixo:

`/notifications`

Possui:

- notificações do usuário;
- contagem de não lidas;
- marcar todas como lidas;
- marcar individualmente.

---

## Chamados

Prefixo:

`/tickets`

Usuários podem criar chamados.

Suporte possui:

- fila de chamados;
- contagem de pendentes;
- atualiza??o de status;
- solução.

---

## Plano de estudos

Prefixo:

`/study-plans`

M?dulo ativo.

Atualmente restrito ao aluno.

---

## Sess?es de estudo

Prefixo:

`/study-sessions`

M?dulo ativo.

Permite registrar:

- matéria;
- assunto;
- duração;
- dificuldade percebida;
- conclusão;
- observações.

---

## Hist?rico de aprendizagem

Prefixo:

`/learning-history`

M?dulo ativo.

Endpoints registrados:

- geração;
- consulta do próprio aluno.

---

# IA

Status:

**PENDENTE ? dependência externa**

O módulo Gemini/IA será retomado quando o componente
desenvolvido pelo colaborador estiver disponível.

A ausência da IA não bloqueia o desenvolvimento do frontend.

---

# Banco de dados

Tabelas principais ativas:

- users
- teachers
- classrooms
- subjects
- enrollments
- attendance
- assessments
- questions
- student_answers
- grades
- books
- chapters
- exercises
- videos
- pdf_materials
- practical_examples
- library_questions
- class_schedules
- notifications
- tickets
- study_plans
- study_sessions
- learning_history

---

# Estruturas candidatas a legado

## library_books

Existe no banco e possui model/schema, por?m nenhuma rota
registrada atualmente utiliza `LibraryBook`.

A biblioteca atualmente utiliza:

`Book`

Tabela:

`books`

Não remover sem uma migração espec?fica.

---

# Routers não registrados

Atualmente não estão incluídos na aplica??o:

- `app.router.ai.chat`
- `app.router.education.books`
- `app.router.education.lesson_plan`
- `app.router.education.questions`

Eles devem ser tratados como candidatos a c?digo legado ou
funcionalidade futura.

Não remover automaticamente.

---

# Segurança

O backend possui:

- JWT;
- validação de usuário ativo;
- login com mensagem genérica;
- desativação lógica de conta;
- permissões por perfil;
- bloqueio pedagógico para Suporte;
- Swagger/OpenAPI desativados em produção;
- configuração sensível via `.env`.

Auditoria de segurança conclu?da no Dia 11.

---

# Estado atual

Backend estrutural principal:

**PRONTO PARA INTEGRAÇÃO COM O FRONTEND**

Exceção:

**IA/Gemini permanece pendente.**
