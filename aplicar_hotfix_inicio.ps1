$ErrorActionPreference = "Stop"

$dashboard = "frontend/dashboard.html"
if (!(Test-Path $dashboard)) {
    throw "Não encontrei frontend/dashboard.html. Rode este script na raiz do Mentor.Edu."
}

$content = Get-Content $dashboard -Raw -Encoding UTF8

if ($content -notmatch 'sidebar-active-fix\.css') {
    $anchor = '<link rel="stylesheet" href="css/responsive.css">'
    $insert = '<link rel="stylesheet" href="css/sidebar-active-fix.css?v=20.3">' + "`r`n    " + $anchor

    if ($content.Contains($anchor)) {
        $content = $content.Replace($anchor, $insert)
    } else {
        throw "Não encontrei css/responsive.css no dashboard.html."
    }

    Set-Content $dashboard $content -Encoding UTF8
}

Write-Host ""
Write-Host "HOTFIX DO INICIO APLICADO COM SUCESSO." -ForegroundColor Green
Write-Host ""
Write-Host "Agora rode:"
Write-Host 'git add frontend/dashboard.html frontend/css/sidebar-active-fix.css'
Write-Host 'git commit -m "fix: ajusta proporcao do item ativo da sidebar"'
Write-Host 'git push origin main'
