# Mentor.Edu — Estado Técnico do Projeto

## 1. Visão geral

O Mentor.Edu é uma plataforma educacional voltada ao acompanhamento
acadêmico, avaliação, personalização do ensino e organização escolar.

O backend foi desenvolvido com FastAPI, SQLAlchemy e SQLite.

Estado atual:

**BACKEND PRINCIPAL PRONTO PARA INTEGRAÇÃO COM O FRONTEND**

A única grande funcionalidade pendente é a integração de Inteligência
Artificial, que depende de um componente externo ainda em desenvolvimento.

---

## 2. Estrutura atual do backend

Auditoria realizada no Dia 13:

- 145 rotas registradas
- 100 endpoints GET
- 22 endpoints POST
- 15 endpoints PATCH
- 3 endpoints PUT
- 5 endpoints DELETE
- 38 arquivos de routers
- 47 arquivos de services
- 53 arquivos de schemas

---

## 3. Tecnologias

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT
- OAuth2 Password Flow
- Pydantic
- Uvicorn

Configurações sensíveis são carregadas através de variáveis de ambiente.

---

## 4. Perfis

### Aluno

Pode acessar seus próprios:

- dados acadêmicos;
- disciplinas;
- matrícula;
- avaliações;
- respostas;
- resultados;
- notas;
- frequência;
- horários;
- histórico;
- biblioteca;
- notificações;
- chamados;
- planos e sessões de estudo.

### Professor

Possui acesso pedagógico relacionado às disciplinas e turmas em que atua.

Pode trabalhar com:

- avaliações;
- questões;
- respostas;
- correções;
- notas;
- frequência;
- análise de desempenho;
- biblioteca;
- banco de questões.

### Diretor de Turma

DT não é um papel de usuário separado.

O vínculo é realizado através de:

`Classroom.teacher_id`

Um professor definido como DT possui leitura acadêmica ampliada
sobre os estudantes da turma sob sua responsabilidade.

### Administração

Responsável pela gestão institucional:

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

- usuários;
- professores;
- chamados;
- estrutura da biblioteca.

Suporte não possui acesso aos dados pedagógicos dos alunos.

---

## 5. Estrutura acadêmica

A estrutura principal é:

Aluno
→ Matrícula ativa
→ Turma
→ Disciplinas da turma

O aluno não escolhe disciplinas individualmente.

Uma disciplina possui:

- turma;
- professor responsável;
- nome;
- carga horária;
- estado ativo/inativo.

---

## 6. Avaliações

O módulo de avaliações contempla:

- criação;
- edição;
- questões;
- respostas;
- correções;
- notas;
- resultados;
- histórico;
- análise de desempenho;
- dificuldade por aluno;
- dificuldade por questão;
- evolução acadêmica.

Também existem controles de disponibilidade:

- data de abertura;
- data de encerramento;
- liberação da prova;
- liberação do resultado;
- liberação do gabarito.

---

## 7. Frequência

O sistema permite:

- lançamento pelo professor;
- consulta por aluno;
- consulta por turma;
- resumo de frequência;
- justificativas;
- pendências;
- edição controlada.

O professor possui janela de até 24 horas para editar determinados
registros de frequência.

---

## 8. Biblioteca

Estrutura principal:

Book
→ Chapter
→ Exercise
→ Video
→ PDF
→ PracticalExample

Também existe banco de questões próprio do professor.

Leitura pedagógica:

- Aluno
- Professor
- Administração

Suporte possui apenas funções estruturais autorizadas.

---

## 9. Notificações

O sistema possui:

- notificações individuais;
- leitura individual;
- marcar todas como lidas;
- contador de não lidas.

O frontend utilizará o contador para badges dinâmicos.

---

## 10. Chamados

Qualquer usuário autenticado pode abrir chamados.

Suporte possui:

- fila de chamados;
- contador de pendentes;
- alteração de status;
- registro de solução.

---

## 11. Horários

Os horários relacionam uma disciplina a:

- dia da semana;
- horário inicial;
- horário final.

Existem validações de conflito para:

- turma;
- professor.

---

## 12. Segurança

A auditoria do Dia 11 confirmou:

- autenticação JWT centralizada;
- verificação de conta ativa;
- login sem enumeração de e-mails;
- mensagem genérica para credenciais inválidas;
- desativação lógica de usuários;
- proteção por perfil;
- proteção de conteúdo pedagógico;
- bloqueio pedagógico do Suporte;
- Swagger desabilitado em produção;
- OpenAPI desabilitado em produção;
- segredo JWT armazenado via `.env`.

---

## 13. Banco de dados

Principais tabelas:

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

## 14. Estruturas candidatas a legado

### library_books

Existe modelo e tabela, porém a biblioteca ativa utiliza:

`books`

A estrutura `library_books` não deve ser removida sem migração e
auditoria específica.

### Routers não registrados

- app.router.ai.chat
- app.router.education.books
- app.router.education.lesson_plan
- app.router.education.questions

Esses arquivos podem representar código antigo ou funcionalidades futuras.

Não devem ser excluídos automaticamente.

---

## 15. Inteligência Artificial

Status:

**PENDENTE**

A integração depende de um componente desenvolvido por colaborador externo.

O backend e o frontend não precisam aguardar essa implementação.

A IA poderá ser integrada posteriormente através de uma camada própria
de serviço sem alterar a arquitetura acadêmica principal.

---

## 16. Documentação técnica existente

- `docs/BACKEND_MAP.md`
- `docs/FRONTEND_API_GUIDE.md`
- `docs/PROJECT_STATUS.md`

---

## 17. Situação do cronograma

- Dias 1–8: funcionalidades principais do backend concluídas
- Dia 9: limpeza estrutural concluída
- Dia 10: configuração e preparação para deploy concluídas
- Dia 11: segurança concluída
- Dia 12: IA adiada por dependência externa
- Dia 13: mapeamento técnico concluído
- Dia 14: consolidação documental concluída
- Dia 15: planejamento do frontend
- Dia 16 em diante: desenvolvimento e integração do frontend

---

## 18. Próxima etapa

A próxima etapa oficial é o frontend.

A ordem recomendada será:

Login
→ identificação automática do perfil
→ estrutura visual global
→ navegação lateral
→ dashboards por perfil
→ integração das funcionalidades
→ testes de integração
→ refinamento visual
→ IA quando disponível

---

## Estado final do backend nesta etapa

**Backend acadêmico e institucional pronto para início da integração frontend.**

**IA permanece como módulo adicional pendente e não bloqueante.**
