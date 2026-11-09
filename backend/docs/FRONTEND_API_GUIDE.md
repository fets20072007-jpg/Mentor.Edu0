# Mentor.Edu — Guia de Integração do Frontend

Este documento relaciona as principais telas do frontend
aos endpoints já existentes no backend.

---

# Autenticação

## Tela de Login

Usar:

`POST /auth/login`

Após autenticação:

`GET /users/me`

O frontend não deve solicitar que o usuário escolha seu perfil.

O perfil vem do backend.

Fluxo:

Login
→ token JWT
→ `/users/me`
→ redirecionamento conforme `tipo`

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

O aluno não escolhe disciplinas individualmente.

---

## Minha turma / matrícula

- `GET /enrollments/me`

---

## Avaliações

- `GET /assessments/`
- `GET /assessments/{assessment_id}`
- `GET /assessments/{assessment_id}/questions`
- `GET /assessments/{assessment_id}/availability/me`
- `GET /assessments/{assessment_id}/submission/me`

Responder questão:

- `POST /answers/questions/{question_id}`

---

## Resultado de avaliação

- `GET /assessments/{assessment_id}/results/me`

Quando autorizado:

- `GET /assessments/{assessment_id}/answer-key/me`

---

## Histórico de avaliações

- `GET /assessments/history/me`
- `GET /assessments/history/me/filter`

---

## Evolução

- `GET /assessments/summary/me`
- `GET /assessments/summary/me/subjects`
- `GET /assessments/summary/me/evolution`

---

## Notas

- `GET /grades/me`

---

## Frequência

- `GET /attendance/me`
- `GET /attendance/me/summary`
- `GET /attendance/{attendance_id}`
- `PATCH /attendance/{attendance_id}/justify`

---

## Histórico acadêmico

- `GET /academic-record/me`

---

## Horários

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

## Sessões de estudo

- `POST /study-sessions/`
- `GET /study-sessions/`
- `GET /study-sessions/{session_id}`
- `PUT /study-sessions/{session_id}`
- `DELETE /study-sessions/{session_id}`

---

## Notificações

- `GET /notifications/me`
- `GET /notifications/me/unread-count`
- `PATCH /notifications/me/read-all`
- `PATCH /notifications/{notification_id}/read`

O frontend deverá exibir badge dinâmico para notificações não lidas.

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

A autorização depende da atuação do professor ou do vínculo como DT.

---

## Frequência

- `POST /attendance/`
- `GET /attendance/teacher/me`
- `GET /attendance/teacher/pending`
- `GET /attendance/classroom/{classroom_id}`
- `GET /attendance/classroom/{classroom_id}/summary`
- `PATCH /attendance/{attendance_id}`

---

## Avaliações

- `POST /assessments`
- `GET /assessments/`
- `GET /assessments/{assessment_id}`
- `PATCH /assessments/{assessment_id}`

---

## Questáes da avaliação

- `POST /assessments/{assessment_id}/questions`
- `PATCH /assessments/{assessment_id}/questions/{question_id}`
- `GET /assessments/{assessment_id}/questions/teacher`

---

## Liberação da avaliação

- `PATCH /assessments/{assessment_id}/access`

---

## Resultados

- `GET /assessments/{assessment_id}/results`
- `GET /assessments/{assessment_id}/results/students/{student_id}`

---

## Correção subjetiva

- `GET /answers/teacher/pending`
- `PATCH /answers/{answer_id}/review`

---

## Notas

- `POST /grades`
- `GET /grades/assessment/{assessment_id}`
- `PATCH /grades/{grade_id}`
- `GET /grades/{grade_id}`

---

## Análise pedagógica

- `GET /assessments/teacher/summary/classrooms`
- `GET /assessments/teacher/difficulties/students`
- `GET /assessments/teacher/students/performance`
- `GET /assessments/teacher/students/{student_id}/difficulties`
- `GET /assessments/teacher/questions/difficulties`
- `GET /assessments/teacher/students/{student_id}/analysis-data`

---

## Histórico de aluno

- `GET /academic-record/{student_id}`

O acesso depende da atuação do professor ou vínculo como DT.

---

## Banco de questões

- `POST /library/question-bank`
- `GET /library/question-bank/me`
- `GET /library/question-bank/shared`
- `GET /library/question-bank/{question_id}`
- `PATCH /library/question-bank/{question_id}`
- `DELETE /library/question-bank/{question_id}`

---

# Administração

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

## Matrículas

- `POST /enrollments`
- `GET /enrollments`
- `PATCH /enrollments/student/{student_id}/classroom`

---

## Horários

- `POST /schedules`
- `GET /schedules`
- `GET /schedules/classroom/{classroom_id}`
- `PATCH /schedules/{schedule_id}`
- `DELETE /schedules/{schedule_id}`

---

## Avaliações

- `GET /admin/assessments`
- `GET /admin/assessments/{assessment_id}`

---

## Frequência institucional

- `GET /attendance/`

---

## Notas institucionais

- `GET /grades/`

---

# Suporte

## Usuários

- `GET /users/`
- `POST /users/register`

O Suporte pode criar:

- Administração;
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

O Suporte não deve possuir acesso ao conteúdo pedagógico protegido.

---

# Componentes globais do frontend

## Badge de notificações

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

Disponível para usuários autenticados.

Criar:

`POST /tickets`

Consultar próprios:

`GET /tickets/me`

---

# IA

Ainda não integrar no frontend definitivo.

Status:

**Pendente de implementação pelo colaborador.**

As telas relacionadas podem inicialmente:

- ficar ocultas;
- ficar marcadas como futura funcionalidade;
- utilizar apenas os recursos determinísticos já existentes.

---

# Regra de integração

O frontend nunca deve decidir sozinho se um usuário possui
permissão para acessar um recurso.

A interface pode esconder botões, mas a autorização oficial
sempre pertence ao backend.

---

# Estado para início do frontend

O frontend pode começar utilizando:

1. autenticação;
2. perfil;
3. navegação por papel;
4. dashboards;
5. turmas;
6. disciplinas;
7. avaliações;
8. notas;
9. frequência;
10. biblioteca;
11. horários;
12. notificações;
13. chamados.

A integração de IA pode ser adicionada posteriormente sem
bloquear o desenvolvimento atual.
