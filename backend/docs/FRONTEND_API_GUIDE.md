# Mentor.Edu ? Guia de Integra??o do Frontend

Este documento relaciona as principais telas do frontend
aos endpoints j? existentes no backend.

---

# Autentica??o

## Tela de Login

Usar:

`POST /auth/login`

Ap?s autentica??o:

`GET /users/me`

O frontend n?o deve solicitar que o usu?rio escolha seu perfil.

O perfil vem do backend.

Fluxo:

Login
? token JWT
? `/users/me`
? redirecionamento conforme `tipo`

---

# Aluno

## Dashboard

Endpoints principais:

- `GET /dashboard/me`
- `GET /performance/me`
- `GET /notifications/me/unread-count`
- `GET /assessments/summary/me`

---

## Disciplinas

- `GET /subjects/me`
- `GET /subjects/me/{subject_id}`

O aluno n?o escolhe disciplinas individualmente.

---

## Minha turma / matr?cula

- `GET /enrollments/me`

---

## Avalia??es

- `GET /assessments/`
- `GET /assessments/{assessment_id}`
- `GET /assessments/{assessment_id}/questions`
- `GET /assessments/{assessment_id}/availability/me`
- `GET /assessments/{assessment_id}/submission/me`

Responder quest?o:

- `POST /answers/questions/{question_id}`

---

## Resultado de avalia??o

- `GET /assessments/{assessment_id}/results/me`

Quando autorizado:

- `GET /assessments/{assessment_id}/answer-key/me`

---

## Hist?rico de avalia??es

- `GET /assessments/history/me`
- `GET /assessments/history/me/filter`

---

## Evolu??o

- `GET /assessments/summary/me`
- `GET /assessments/summary/me/subjects`
- `GET /assessments/summary/me/evolution`

---

## Notas

- `GET /grades/me`

---

## Frequ?ncia

- `GET /attendance/me`
- `GET /attendance/me/summary`
- `GET /attendance/{attendance_id}`
- `PATCH /attendance/{attendance_id}/justify`

---

## Hist?rico acad?mico

- `GET /academic-record/me`

---

## Hor?rios

- `GET /schedules/me`

---

## Biblioteca

Principais endpoints:

- `GET /library/books`
- `GET /library/books/disciplina/{disciplina}`
- `GET /library/books/{book_id}`
- `GET /library/books/{book_id}/chapters`
- `GET /library/chapters/{chapter_id}`
- `GET /library/chapters/{chapter_id}/exercises`
- `GET /library/chapters/{chapter_id}/videos`
- `GET /library/chapters/{chapter_id}/pdfs`
- `GET /library/chapters/{chapter_id}/examples`

---

## Plano de estudos

- `POST /study-plans/`
- `GET /study-plans/me`
- `PUT /study-plans/{plan_id}`
- `DELETE /study-plans/{plan_id}`

---

## Sess?es de estudo

- `POST /study-sessions/`
- `GET /study-sessions/`
- `GET /study-sessions/{session_id}`
- `PUT /study-sessions/{session_id}`
- `DELETE /study-sessions/{session_id}`

---

## Notifica??es

- `GET /notifications/me`
- `GET /notifications/me/unread-count`
- `PATCH /notifications/me/read-all`
- `PATCH /notifications/{notification_id}/read`

O frontend dever? exibir badge din?mico para notifica??es n?o lidas.

---

## Chamados

- `POST /tickets`
- `GET /tickets/me`

---

# Professor

## Minhas turmas

- `GET /teachers/me/classrooms`

---

## Minhas disciplinas

- `GET /subjects/me`
- `GET /subjects/me/{subject_id}`

---

## Alunos da turma

- `GET /enrollments/classroom/{classroom_id}`

A autoriza??o depende da atua??o do professor ou do v?nculo como DT.

---

## Frequ?ncia

- `POST /attendance/`
- `GET /attendance/teacher/me`
- `GET /attendance/teacher/pending`
- `GET /attendance/classroom/{classroom_id}`
- `GET /attendance/classroom/{classroom_id}/summary`
- `PATCH /attendance/{attendance_id}`

---

## Avalia??es

- `POST /assessments`
- `GET /assessments/`
- `GET /assessments/{assessment_id}`
- `PATCH /assessments/{assessment_id}`

---

## Quest?es da avalia??o

- `POST /assessments/{assessment_id}/questions`
- `PATCH /assessments/{assessment_id}/questions/{question_id}`
- `GET /assessments/{assessment_id}/questions/teacher`

---

## Libera??o da avalia??o

- `PATCH /assessments/{assessment_id}/access`

---

## Resultados

- `GET /assessments/{assessment_id}/results`
- `GET /assessments/{assessment_id}/results/students/{student_id}`

---

## Corre??o subjetiva

- `GET /answers/teacher/pending`
- `PATCH /answers/{answer_id}/review`

---

## Notas

- `POST /grades`
- `GET /grades/assessment/{assessment_id}`
- `PATCH /grades/{grade_id}`
- `GET /grades/{grade_id}`

---

## An?lise pedag?gica

- `GET /assessments/teacher/summary/classrooms`
- `GET /assessments/teacher/difficulties/students`
- `GET /assessments/teacher/students/performance`
- `GET /assessments/teacher/students/{student_id}/difficulties`
- `GET /assessments/teacher/questions/difficulties`
- `GET /assessments/teacher/students/{student_id}/analysis-data`

---

## Hist?rico de aluno

- `GET /academic-record/{student_id}`

O acesso depende da atua??o do professor ou v?nculo como DT.

---

## Banco de quest?es

- `POST /library/question-bank`
- `GET /library/question-bank/me`
- `GET /library/question-bank/shared`
- `GET /library/question-bank/{question_id}`
- `PATCH /library/question-bank/{question_id}`
- `DELETE /library/question-bank/{question_id}`

---

# Administra??o

## Dashboard

- `GET /admin/summary`

---

## Professores

- `GET /admin/teachers`
- `GET /admin/teachers/{user_id}`
- `GET /admin/teachers/{user_id}/summary`

Cadastro:

- `POST /users/register`

---

## Alunos

- `GET /admin/students`
- `GET /admin/students/{user_id}`
- `GET /admin/students/{user_id}/summary`

Cadastro:

- `POST /users/register`

---

## Turmas

- `POST /classrooms`
- `GET /classrooms`
- `GET /admin/classrooms`
- `GET /admin/classrooms/{classroom_id}`
- `GET /admin/classrooms/{classroom_id}/summary`

---

## Diretor de Turma

- `PATCH /classrooms/{classroom_id}/dt`

---

## Professores da turma

- `GET /classrooms/{classroom_id}/teachers`

---

## Disciplinas

- `POST /subjects`
- `GET /subjects`
- `PATCH /subjects/{subject_id}/teacher`

---

## Matr?culas

- `POST /enrollments`
- `GET /enrollments`
- `PATCH /enrollments/student/{student_id}/classroom`

---

## Hor?rios

- `POST /schedules`
- `GET /schedules`
- `GET /schedules/classroom/{classroom_id}`
- `PATCH /schedules/{schedule_id}`
- `DELETE /schedules/{schedule_id}`

---

## Avalia??es

- `GET /admin/assessments`
- `GET /admin/assessments/{assessment_id}`

---

## Frequ?ncia institucional

- `GET /attendance/`

---

## Notas institucionais

- `GET /grades/`

---

# Suporte

## Usu?rios

- `GET /users/`
- `POST /users/register`

O Suporte pode criar:

- Administra??o;
- Professor;
- Aluno.

---

## Professores

- `GET /teachers`

---

## Chamados

- `GET /tickets/support/pending-count`
- `GET /tickets`
- `PATCH /tickets/{ticket_id}/status`

---

## Estrutura da biblioteca

- `POST /library/books`
- `POST /library/books/{book_id}/chapters`

O Suporte n?o deve possuir acesso ao conte?do pedag?gico protegido.

---

# Componentes globais do frontend

## Badge de notifica??es

Usar:

`GET /notifications/me/unread-count`

---

## Perfil

Usar:

`GET /users/me`

Editar:

`PUT /users/me`

Desativar:

`DELETE /users/me`

---

## Chamados

Dispon?vel para usu?rios autenticados.

Criar:

`POST /tickets`

Consultar pr?prios:

`GET /tickets/me`

---

# IA

Ainda n?o integrar no frontend definitivo.

Status:

**Pendente de implementa??o pelo colaborador.**

As telas relacionadas podem inicialmente:

- ficar ocultas;
- ficar marcadas como futura funcionalidade;
- utilizar apenas os recursos determin?sticos j? existentes.

---

# Regra de integra??o

O frontend nunca deve decidir sozinho se um usu?rio possui
permiss?o para acessar um recurso.

A interface pode esconder bot?es, mas a autoriza??o oficial
sempre pertence ao backend.

---

# Estado para in?cio do frontend

O frontend pode come?ar utilizando:

1. autentica??o;
2. perfil;
3. navega??o por papel;
4. dashboards;
5. turmas;
6. disciplinas;
7. avalia??es;
8. notas;
9. frequ?ncia;
10. biblioteca;
11. hor?rios;
12. notifica??es;
13. chamados.

A integra??o de IA pode ser adicionada posteriormente sem
bloquear o desenvolvimento atual.
