# Mentor.Edu — Dia 18A

Frontend do perfil Professor integrado ao backend existente.

## Implementado
- Minhas turmas
- Direção de turma (DT)
- Disciplinas
- Minhas avaliações
- Criação de avaliação
- Resultados
- Correções pendentes
- Liberação de acesso às avaliações
- Registro de frequência
- Pendências e resumo de frequência
- Notas por avaliação
- Banco de questões próprio e compartilhado
- Biblioteca pedagógica
- Desempenho das turmas
- Dificuldades
- Evolução dos estudantes
- Horários
- Chamados e Perfil continuam compartilhados com a base do Dia 17

## Regra arquitetural mantida
As páginas não fazem fetch direto. Toda integração passa pelos módulos em `js/api/` e pelo `api/client.js`.

## Continuação
Dia 18B deve partir desta pasta e adicionar Administração, mantendo integralmente o Dia 18A.
