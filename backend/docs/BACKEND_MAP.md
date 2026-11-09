# Mentor.Edu ? Mapa do Backend

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

Possui acesso aos pr?prios dados acad?micos:

- avalia??es;
- respostas;
- notas;
- frequ?ncia;
- disciplinas;
- matr?cula;
- hor?rios;
- hist?rico acad?mico;
- biblioteca;
- notifica??es;
- chamados;
- plano de estudos;
- sess?es de estudo;
- desempenho;
- recomenda??es.

### Professor

Respons?vel pelo trabalho pedag?gico:

- disciplinas em que atua;
- turmas relacionadas ?s disciplinas;
- avalia??es;
- quest?es;
- corre??es;
- notas;
- frequ?ncia;
- an?lise de desempenho;
- biblioteca pedag?gica;
- banco de quest?es.

### Diretor de Turma ? DT

DT n?o ? um perfil separado.

? um professor definido em:

`Classroom.teacher_id`

O DT pode possuir acesso de leitura ampliado aos dados
acad?micos dos estudantes da pr?pria turma.

### Administra??o

Respons?vel pela gest?o institucional:

- usu?rios;
- professores;
- alunos;
- turmas;
- disciplinas;
- matr?culas;
- DT;
- hor?rios;
- avalia??es;
- vis?o acad?mica institucional.

### Suporte

Respons?vel por fun??es operacionais:

- cria??o institucional de usu?rios;
- professores;
- chamados;
- estrutura da biblioteca.

O Suporte n?o possui acesso ao conte?do pedag?gico dos alunos.

---

# M?dulos ativos

## Autentica??o

Prefixo:

`/auth`

Principal endpoint:

- `POST /auth/login`

---

## Usu?rios

Prefixo:

`/users`

Principais fun??es:

- cadastro institucional;
- listagem;
- perfil atual;
- edi??o do perfil;
- desativa??o l?gica da conta.

A exclus?o f?sica do usu?rio n?o ? utilizada.

---

## Professores

Prefixo:

`/teachers`

Fun??es:

- listagem;
- turmas do professor autenticado;
- turmas de um professor espec?fico.

---

## Turmas

Prefixo:

`/classrooms`

Fun??es:

- cadastro;
- listagem;
- defini??o de DT;
- professores da turma.

---

## Disciplinas

Prefixo:

`/subjects`

A disciplina pertence a uma turma e possui um professor respons?vel.

O aluno n?o seleciona disciplinas individualmente.

Fluxo:

Aluno
? matr?cula ativa
? turma
? disciplinas da turma

---

## Matr?culas

Prefixo:

`/enrollments`

Respons?vel pelo v?nculo:

Aluno
? Turma

Existe apenas uma matr?cula ativa utilizada como refer?ncia
acad?mica principal.

---

## Frequ?ncia

Prefixo:

`/attendance`

Possui:

- lan?amento por professor;
- consulta do aluno;
- resumo;
- pend?ncias do professor;
- consulta por turma;
- justificativa;
- edi??o limitada.

A edi??o realizada pelo professor possui regra temporal de 24 horas.

---

## Avalia??es

Prefixo:

`/assessments`

? um dos maiores m?dulos do sistema.

Possui:

- cria??o;
- edi??o;
- quest?es;
- resultados;
- hist?rico;
- resumo;
- evolu??o;
- an?lise de dificuldade;
- desempenho por estudante;
- configura??o de disponibilidade.

Campos de libera??o:

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
- hist?rico pr?prio;
- pend?ncias do professor;
- revis?o manual.

Quest?es subjetivas podem receber avalia??o parcial.

---

## Notas

Prefixo:

`/grades`

Possui:

- registro;
- notas do aluno;
- notas por avalia??o;
- vis?o administrativa;
- edi??o;
- consulta individual.

---

## Hist?rico acad?mico

Prefixo:

`/academic-record`

Permite:

- aluno consultar o pr?prio hist?rico;
- professor/DT consultar alunos autorizados;
- Administra??o consultar institucionalmente.

---

## Analytics

Prefixo:

`/analytics`

Atualmente possui c?lculo de m?dia acad?mica.

Outros m?dulos relacionados:

- `/performance`
- `/dashboard`
- `/recommendations`

---

## Biblioteca

Prefixo:

`/library`

Estrutura ativa:

Book
? Chapter
? Exercise / Video / PDF / PracticalExample

Tamb?m existe banco de quest?es do professor.

### Permiss?es

Aluno, Professor e Administra??o:

- leitura pedag?gica.

Professor:

- cria??o de conte?dos pedag?gicos autorizados.

Suporte:

- administra??o estrutural de livros/cap?tulos;
- sem acesso ao conte?do pedag?gico protegido.

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

Possui valida??o de conflito de turma e professor.

---

## Notifica??es

Prefixo:

`/notifications`

Possui:

- notifica??es do usu?rio;
- contagem de n?o lidas;
- marcar todas como lidas;
- marcar individualmente.

---

## Chamados

Prefixo:

`/tickets`

Usu?rios podem criar chamados.

Suporte possui:

- fila de chamados;
- contagem de pendentes;
- atualiza??o de status;
- solu??o.

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

- mat?ria;
- assunto;
- dura??o;
- dificuldade percebida;
- conclus?o;
- observa??es.

---

## Hist?rico de aprendizagem

Prefixo:

`/learning-history`

M?dulo ativo.

Endpoints registrados:

- gera??o;
- consulta do pr?prio aluno.

---

# IA

Status:

**PENDENTE ? depend?ncia externa**

O m?dulo Gemini/IA ser? retomado quando o componente
desenvolvido pelo colaborador estiver dispon?vel.

A aus?ncia da IA n?o bloqueia o desenvolvimento do frontend.

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

N?o remover sem uma migra??o espec?fica.

---

# Routers n?o registrados

Atualmente n?o est?o inclu?dos na aplica??o:

- `app.router.ai.chat`
- `app.router.education.books`
- `app.router.education.lesson_plan`
- `app.router.education.questions`

Eles devem ser tratados como candidatos a c?digo legado ou
funcionalidade futura.

N?o remover automaticamente.

---

# Seguran?a

O backend possui:

- JWT;
- valida??o de usu?rio ativo;
- login com mensagem gen?rica;
- desativa??o l?gica de conta;
- permiss?es por perfil;
- bloqueio pedag?gico para Suporte;
- Swagger/OpenAPI desativados em produ??o;
- configura??o sens?vel via `.env`.

Auditoria de seguran?a conclu?da no Dia 11.

---

# Estado atual

Backend estrutural principal:

**PRONTO PARA INTEGRA??O COM O FRONTEND**

Exce??o:

**IA/Gemini permanece pendente.**
