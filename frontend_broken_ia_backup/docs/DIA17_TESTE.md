# Dia 17 — Checklist de teste do perfil Aluno

1. Inicie o backend em `http://127.0.0.1:8000`.
2. Inicie o frontend com `python -m http.server 5500` dentro de `frontend`.
3. Entre com uma conta real do tipo `Aluno`.
4. Confirme que a dashboard continua minimalista.
5. Teste os módulos pela sidebar:
   - Disciplinas;
   - Avaliações;
   - Histórico e resultados de avaliações;
   - Notas;
   - Frequência;
   - Justificativas;
   - Histórico acadêmico;
   - Plano de estudos;
   - Sessões de estudo;
   - Biblioteca;
   - Horários;
   - Recomendações;
   - Notificações;
   - Chamados;
   - Perfil.
6. Em Avaliações, teste uma avaliação aberta se houver. O frontend deve respeitar o status retornado pelo backend.
7. Em Frequência, justificativa só deve ser enviada para `falta_pendente` e dentro da regra do backend.
8. Se alguma área estiver vazia porque o banco não possui dados, o estado vazio é esperado e não representa falha do frontend.

Não faça commit antes do teste local.
