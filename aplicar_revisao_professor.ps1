$ErrorActionPreference = "Stop"

function ReadText($path) {
  if (!(Test-Path $path)) { throw "Arquivo nao encontrado: $path" }
  return Get-Content $path -Raw
}
function WriteText($path, $content) {
  Set-Content $path $content -Encoding UTF8
}

# ---------- main.py: include password router + assessment migrations ----------
$path = "backend/app/main.py"
$c = ReadText $path

if ($c -notmatch 'password_router') {
  $c = $c.Replace(
    'from app.router.user.users import router as users_router',
    "from app.router.user.users import router as users_router`r`nfrom app.router.user.password import router as password_router"
  )
  $c = $c.Replace(
    'app.include_router(users_router)',
    "app.include_router(users_router)`r`napp.include_router(password_router)"
  )
}

if ($c -notmatch '"assessments": \[') {
  $anchor = '"subjects": [("categoria", "VARCHAR DEFAULT ''Outras'' NOT NULL")],'
  $insert = $anchor + "`r`n        " + '"assessments": [("arquivo", "VARCHAR"), ("arquivo_nome", "VARCHAR")],'
  $c = $c.Replace($anchor, $insert)
}
WriteText $path $c

# ---------- models.py: Assessment attachment columns ----------
$path = "backend/app/database/models.py"
$c = ReadText $path
if ($c -notmatch 'arquivo_nome = Column\(String, nullable=True\)') {
  $old = '    tipo = Column(String, nullable=False)'
  $new = @'
    tipo = Column(String, nullable=False)
    arquivo = Column(String, nullable=True)
    arquivo_nome = Column(String, nullable=True)
'@
  $c = $c.Replace($old, $new.TrimEnd())
}
WriteText $path $c

# ---------- schema assessment ----------
$path = "backend/app/schema/assessment.py"
$c = ReadText $path
if ($c -notmatch 'arquivo_nome: Optional\[str\]') {
  $c = $c.Replace(
    '    tipo: str',
    "    tipo: str`r`n    arquivo: Optional[str] = None`r`n    arquivo_nome: Optional[str] = None"
  )
  # The replacement hits create/response/update; fix duplicated defaults on response/update is valid Pydantic.
}
WriteText $path $c

# ---------- assessment service create ----------
$path = "backend/app/services/academic/assessment_service.py"
$c = ReadText $path
if ($c -notmatch 'arquivo=assessment\.arquivo') {
  $c = $c.Replace(
    '        tipo=assessment.tipo,',
    "        tipo=assessment.tipo,`r`n        arquivo=assessment.arquivo,`r`n        arquivo_nome=assessment.arquivo_nome,"
  )
}
WriteText $path $c

Write-Host ""
Write-Host "REVISAO DO PROFESSOR APLICADA." -ForegroundColor Green
Write-Host "Agora rode:"
Write-Host 'git add .'
Write-Host 'git commit -m "feat: revisao do perfil do professor e criacao de avaliacoes"'
Write-Host 'git push origin main'
