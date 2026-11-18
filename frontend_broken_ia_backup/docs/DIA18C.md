# Dia 18C — Suporte

Versão cumulativa do frontend: Aluno + Professor + Administração + Suporte.

## Implementado
- Dashboard operacional do Suporte com métricas reais.
- Central de chamados: filtros, busca, status (Aberto / Em análise / Resolvido) e registro de solução.
- Diretório de usuários com filtros e busca, sem expor dados pedagógicos.
- Diretório específico de professores.
- Biblioteca institucional: cadastro e listagem de livros.
- Capítulos: seleção de livro, listagem e cadastro de capítulos.
- Configurações: diagnóstico local somente com informações existentes; não foram inventadas ações sem endpoint no backend.

## Regra de segurança preservada
O perfil Suporte permanece operacional. Não recebe páginas de notas, avaliações, frequência, desempenho ou demais dados pedagógicos dos alunos.
