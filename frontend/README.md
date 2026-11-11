# Mentor.Edu — Frontend

Frontend modular em HTML, CSS e JavaScript ES Modules, integrado ao backend FastAPI.

## Executar localmente

Com o backend em `http://127.0.0.1:8000`:

```powershell
cd frontend
python -m http.server 5500
```

Abra `http://127.0.0.1:5500`.

## Estrutura principal

- `index.html`: login institucional;
- `dashboard.html`: shell autenticado;
- `css/`: tokens, layout, componentes, páginas e responsividade;
- `js/api/`: acesso centralizado ao backend;
- `js/components/`: sidebar, topbar e componentes compartilhados;
- `js/pages/`: dashboards e páginas por perfil;
- `docs/visual-references/`: referências visuais oficiais aprovadas;
- `legacy/pre-dia16/`: protótipos antigos preservados apenas como histórico.

## Status

- Dia 16: fundação modular, login, shell, dashboards e identidade visual — concluído.
- Dia 17: páginas funcionais do Aluno e integração com endpoints acadêmicos — implementado para teste local.
- Dia 18: Professor, Administração e Suporte — próximo.

## Regras visuais

A fonte oficial de especificação é `backend/docs/FRONTEND_SPEC.md`.

Os dashboards iniciais são deliberadamente minimalistas: detalhes aparecem depois que o usuário entra no módulo por meio de `Ver` ou pela sidebar.

Google e Microsoft aparecem no login por coerência visual, mas ficam desabilitados enquanto o backend não possuir OAuth oficial.
