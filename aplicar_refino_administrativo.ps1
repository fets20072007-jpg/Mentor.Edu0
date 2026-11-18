$ErrorActionPreference = "Stop"

$dashboard = "frontend/dashboard.html"
if (!(Test-Path $dashboard)) {
    throw "Não encontrei frontend/dashboard.html. Rode este script na raiz do Mentor.Edu."
}

$content = Get-Content $dashboard -Raw -Encoding UTF8

if ($content -notmatch 'admin-polish\.css') {
    if ($content -match '<link rel="stylesheet" href="css/responsive.css">') {
        $content = $content.Replace(
            '<link rel="stylesheet" href="css/responsive.css">',
            '<link rel="stylesheet" href="css/admin-polish.css?v=20.1">' + "`r`n    " + '<link rel="stylesheet" href="css/responsive.css">'
        )
    } else {
        throw "Não encontrei o ponto de inclusão dos estilos no dashboard.html."
    }

    Set-Content $dashboard $content -Encoding UTF8
}

Write-Host ""
Write-Host "REFINO VISUAL ADMINISTRATIVO APLICADO." -ForegroundColor Green
Write-Host ""
Write-Host "Agora rode:"
Write-Host 'git add frontend/dashboard.html frontend/css/admin-polish.css frontend/js/pages/shared/profile.js'
Write-Host 'git commit -m "feat: refina perfil e visual administrativo"'
Write-Host 'git push origin main'
