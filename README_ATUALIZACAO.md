# Como aplicar esta atualização visual

Copie a pasta `frontend` deste pacote sobre a pasta `frontend` do seu projeto Mentor.Edu.

Para manter o Swagger na mesma identidade visual, copie também:

`backend/app/static/swagger-custom.css`

sobre o arquivo de mesmo nome no projeto.

A atualização não altera banco de dados nem serviços backend.

## Executar

Terminal 1:

```powershell
cd "C:\Users\franc\Documents\Mentor.Edu\backend"
python -m uvicorn app.main:app --reload
```

Terminal 2:

```powershell
cd "C:\Users\franc\Documents\Mentor.Edu\frontend"
python -m http.server 5500
```

Abra `http://127.0.0.1:5500`.
