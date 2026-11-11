# Auditoria Mentor.Edu — 16/10/2026

## Escopo testado

Backend FastAPI iniciado e respondendo em `127.0.0.1:8000`. Frontend estático iniciado e respondendo em `127.0.0.1:5500`. CORS validado para o frontend. Foram testados tokens de Aluno, Professor, Administração e Suporte em uma cópia isolada do banco enviado.

## O que funcionou como esperado

- Backend iniciou normalmente e `/` respondeu 200.
- Frontend foi servido normalmente e os arquivos `index.html`, `app.js` e `styles.css` responderam.
- CORS aceitou `http://127.0.0.1:5500` com `Authorization`.
- Aluno A listou somente avaliação da própria turma.
- Aluno A acessou as questões da própria turma; Aluno B foi bloqueado ao tentar acessar/responder a questão da outra turma.
- Resultado individual do aluno respeitou a turma.
- `/answers/me` retorna somente respostas do usuário autenticado.
- Professor vê somente as próprias avaliações pela listagem normal.
- Administração conseguiu acessar `/admin/summary`, avaliações, professores, alunos e turmas.
- Suporte conseguiu acessar `/users/` e o próprio perfil.
- Restrições de perfil em várias rotas principais retornaram 403 corretamente.

## Problemas críticos encontrados

### 1. Gabarito é enviado para o aluno
`GET /assessments/{id}/questions` usa `QuestionResponse`, que inclui `resposta_correta` e `explicacao`. Mesmo que o frontend esconda esses campos, eles continuam chegando pela API. Criar um schema específico para aluno sem gabarito/explicação antes da entrega.

### 2. Rotas duplicadas em `assessment.py` quebram a segurança de ownership
Existem POST/PATCH de questões e GET de resultado individual repetidos no mesmo arquivo. Em teste, Professor A conseguiu adicionar e editar uma questão dentro de uma avaliação do Professor B. Também conseguiu consultar o resultado de um aluno em avaliação de outro professor.

Remover as primeiras versões duplicadas e manter apenas as versões que chamam `get_teacher_assessment(...)`.

### 3. Professor consegue usar turma/disciplina de outro professor ao criar avaliação
`create_assessment()` grava `classroom_id` e `subject_id` recebidos sem conferir se a disciplina pertence ao professor. Em teste, Professor A criou avaliação usando uma disciplina ligada a outro professor.

A criação da avaliação deve localizar `Subject` por `subject_id` + `teacher_id` do professor autenticado e derivar `classroom_id = subject.classroom_id`.

### 4. Rotas institucionais estão públicas
Sem autenticação foi possível listar `/teachers`, `/classrooms` e `/subjects`. `/teachers` expõe inclusive CPF, matrícula e telefone. Também existem outras rotas acadêmicas/biblioteca sem controle de perfil.

Aplicar `require_admin`, `require_teacher`, `require_student` ou uma combinação adequada em todas as rotas.

### 5. Cadastro de Professor cria `User`, mas não cria `Teacher`
Administração/Suporte podem criar uma conta do tipo Professor, porém `register_user()` não cria o registro correspondente na tabela `teachers`. O novo professor pode logar, mas rotas pedagógicas que buscam `Teacher.user_id` podem retornar “Perfil de professor não encontrado”.

Criar o perfil `Teacher` no onboarding institucional ou implementar uma etapa obrigatória de conclusão do perfil docente.

## Problemas importantes

- Backend permite múltiplas respostas para a mesma questão. O frontend revisado evita o segundo envio visualmente, mas a API ainda aceita duplicata. Definir regra oficial e aplicar no banco/serviço.
- `register_teacher` exige apenas usuário autenticado; um Aluno autenticado pode tentar criar perfil de professor. Restringir.
- `DELETE /users/me` permite apagar conta institucional. Preferir desativação feita por Administração/Suporte.
- Administração recebe `ano_letivo: null` nas turmas porque o model usa `ano`; alinhar schema/service.
- Banco contém turmas duplicadas e avaliações antigas com `classroom_id`/`subject_id` igual a 0. Fazer limpeza de dados de teste.
- `academic-record` apresentou erro 500 e está sem proteção adequada.
- `requirements.txt` está em UTF-16; converter para UTF-8 para facilitar deploy/Linux/CI.
- `SECRET_KEY` está fixa no código. Mover para `.env`.
- Há funções duplicadas em `assessment_service.py` (`get_teacher_profile`, `get_teacher_assessment`, `update_assessment`). Limpar.
- Há duplicações de declaração/relationship em `models.py`, como `User.__tablename__` e `Teacher.user`.
- Não há validação de `assessment.ativa` no envio de resposta e ainda não existe prazo de encerramento próprio para avaliação.

## Interface revisada

A versão incluída neste pacote usa:
- principal: bege café com leite `#C9B69A`;
- secundária: preto fosco `#1C1C1C`;
- fundo: bege claro `#EEE6DB`.

### Aluno
Conectados: início com dados reais, avaliações, abertura de avaliação, envio de respostas, minhas respostas, desempenho, histórico e perfil. Chamados e Notificações permanecem identificados como planejados.

### Professor
Conectados: início, minhas turmas, avaliações, alunos, resumo de correções e relatórios. A correção individual ainda precisa de um endpoint que liste respostas pendentes com `answer_id`. A criação visual de avaliação deve ser liberada depois da correção de vínculo Professor → Disciplina → Turma.

### Administração
Conectados: início, usuários, cadastro de aluno/professor, turmas, avaliações e relatórios. Administração continua sem poder editar pedagogicamente as avaliações.

### Suporte
Conectados: início, usuários, cadastro institucional, listagem de Administração e diagnóstico básico do ambiente. Chamados/Notificações ficam preparados para os módulos futuros.

## Prioridade recomendada

1. Remover rotas duplicadas inseguras de avaliações.
2. Ocultar gabarito das respostas enviadas ao aluno.
3. Corrigir vínculo Professor → Disciplina → Turma na criação da avaliação.
4. Fechar rotas públicas e revisar permissões de todos os módulos antigos.
5. Automatizar criação de `Teacher` no cadastro de Professor.
6. Criar endpoint de correções pendentes.
7. Definir regra de resposta única / tentativa.
8. Implementar Chamados.
9. Implementar Notificações e prazos.
10. Integrar Gemini por último.

## Falhas adicionais confirmadas na execução

- `GET /assessments/history/me` retornou 500 depois que o aluno passou a ter histórico. O service retorna apenas `assessment_id`, `titulo`, `subject_id`, `semestre`, `ano_letivo`, `percentual` e `nota_final`, mas `AssessmentHistoryResponse` exige também `classroom_id`, `teacher_id`, `tipo` e `status_desempenho`. Alinhar service e schema.
- `GET /academic-record/{student_id}` retornou 500 porque `academic_record_service.py` usa `Enrollment.student_id`, mas o model `Enrollment` possui `user_id`.
- Em teste isolado, o backend aceitou uma segunda resposta para a mesma questão, confirmando a ausência de regra de tentativa única.
