$ErrorActionPreference = "Stop"

$path = "backend/app/database/models.py"
if (!(Test-Path $path)) {
    throw "Nao encontrei backend/app/database/models.py. Rode este script na raiz do Mentor.Edu."
}

$content = Get-Content $path -Raw

$old = @'
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha = Column(String)
    tipo = Column(String, nullable=False)
    arquivo = Column(String, nullable=True)
    arquivo_nome = Column(String, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
'@

$new = @'
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha = Column(String)
    tipo = Column(String, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
'@

if ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
} else {
    # Fallback tolerante a CRLF/LF
    $pattern = '(?ms)(class User\(Base\):.*?tipo = Column\(String, nullable=False\)\r?\n)\s*arquivo = Column\(String, nullable=True\)\r?\n\s*arquivo_nome = Column\(String, nullable=True\)\r?\n'
    if ($content -match $pattern) {
        $content = [regex]::Replace($content, $pattern, '$1', 1)
    } else {
        throw "Nao encontrei os campos arquivo/arquivo_nome dentro do modelo User."
    }
}

Set-Content $path $content -Encoding UTF8

Write-Host ""
Write-Host "HOTFIX APLICADO COM SUCESSO." -ForegroundColor Green
Write-Host "Removidos de User: arquivo, arquivo_nome"
Write-Host "Assessment permanece com os campos de anexo."
Write-Host ""
Write-Host "Agora rode:"
Write-Host 'git add backend/app/database/models.py'
Write-Host 'git commit -m "fix: remove campos de anexo indevidos do usuario"'
Write-Host 'git push origin main'
