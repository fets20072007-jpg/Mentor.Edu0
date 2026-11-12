$ErrorActionPreference = "Stop"

$main = "backend/app/main.py"

if (!(Test-Path $main)) {
    throw "Nao encontrei backend/app/main.py. Rode este script na raiz do projeto Mentor.Edu."
}

$content = Get-Content $main -Raw

$marker = @'
app = FastAPI(
'@

if ($content -notmatch [regex]::Escape($marker.Trim())) {
    throw "Nao encontrei a criacao do FastAPI no main.py."
}

$middleware = @'

# =========================================================
# DESATIVA CACHE DO FRONTEND DURANTE O DESENVOLVIMENTO
# =========================================================
@app.middleware("http")
async def disable_frontend_cache(request, call_next):
    response = await call_next(request)
    path = request.url.path.lower()

    if (
        path == "/"
        or path.endswith(".html")
        or path.endswith(".js")
        or path.endswith(".css")
    ):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response

'@

# Insere o middleware depois do fechamento do app = FastAPI(...)
# localiza a primeira ocorrencia do bloco que termina em "\n)"
$pattern = '(?s)(app = FastAPI\(.+?\n\))'
if ($content -match $pattern) {
    if ($content -notmatch 'disable_frontend_cache') {
        $content = [regex]::Replace(
            $content,
            $pattern,
            ('$1' + $middleware),
            1
        )
    }
} else {
    throw "Nao consegui localizar o bloco app = FastAPI(...)."
}

Set-Content $main $content -Encoding UTF8

Write-Host ""
Write-Host "HOTFIX APLICADO." -ForegroundColor Green
Write-Host "Arquivo alterado: backend/app/main.py"
Write-Host ""
Write-Host "Agora rode:"
Write-Host 'git add backend/app/main.py'
Write-Host 'git commit -m "fix: desativa cache do frontend durante desenvolvimento"'
Write-Host 'git push origin main'
