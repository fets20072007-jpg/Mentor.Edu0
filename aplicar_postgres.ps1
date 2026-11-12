$ErrorActionPreference = "Stop"

$root = Get-Location
$main = Join-Path $root "backend/app/main.py"
$req  = Join-Path $root "backend/requirements.txt"

if (!(Test-Path $main)) { throw "Nao encontrei backend/app/main.py. Rode este script na raiz do Mentor.Edu." }
if (!(Test-Path $req))  { throw "Nao encontrei backend/requirements.txt. Rode este script na raiz do Mentor.Edu." }

Copy-Item $main "$main.bak-postgres" -Force
Copy-Item $req  "$req.bak-postgres" -Force

# 1) Importa inspect do SQLAlchemy
$content = Get-Content $main -Raw
$content = $content -replace 'from sqlalchemy import text(\r?\n)', 'from sqlalchemy import text, inspect$1'

# 2) Troca o bloco PRAGMA (SQLite-only) por introspeccao compativel com SQLite/PostgreSQL.
$old = @'
    with engine.begin() as conn:
        for table, columns in migrations.items():
            existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})"))}
            for name, ddl in columns:
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
'@

$new = @'
    with engine.begin() as conn:
        inspector = inspect(conn)
        for table, columns in migrations.items():
            existing = {
                column["name"]
                for column in inspector.get_columns(table)
            }
            for name, ddl in columns:
                if name not in existing:
                    # PostgreSQL usa TIMESTAMP no lugar de DATETIME.
                    safe_ddl = (
                        ddl.replace("DATETIME", "TIMESTAMP")
                        if engine.dialect.name == "postgresql"
                        else ddl
                    )
                    conn.execute(
                        text(
                            f"ALTER TABLE {table} "
                            f"ADD COLUMN {name} {safe_ddl}"
                        )
                    )
'@

if ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
} else {
    # Regex tolerante a CRLF/LF e espacamento.
    $pattern = '(?ms)    with engine\.begin\(\) as conn:\s*\r?\n        for table, columns in migrations\.items\(\):\s*\r?\n            existing = \{row\[1\] for row in conn\.execute\(text\(f"PRAGMA table_info\(\{table\}\)"\)\)\}\s*\r?\n            for name, ddl in columns:\s*\r?\n                if name not in existing:\s*\r?\n                    conn\.execute\(text\(f"ALTER TABLE \{table\} ADD COLUMN \{name\} \{ddl\}"\)\)'
    if ($content -match $pattern) {
        $content = [regex]::Replace($content, $pattern, $new.TrimEnd(), 1)
    } else {
        throw "Nao encontrei o bloco PRAGMA esperado no main.py. O arquivo pode ter mudado."
    }
}

Set-Content $main $content -Encoding UTF8

# 3) Driver PostgreSQL para SQLAlchemy (Python 3.14 compativel)
$reqContent = Get-Content $req -Raw
if ($reqContent -notmatch '(?m)^psycopg2-binary==') {
    Add-Content $req "`npsycopg2-binary==2.9.13"
}

Write-Host ""
Write-Host "HOTFIX POSTGRES APLICADO COM SUCESSO." -ForegroundColor Green
Write-Host "Arquivos alterados:"
Write-Host "  backend/app/main.py"
Write-Host "  backend/requirements.txt"
Write-Host ""
Write-Host "Backups:"
Write-Host "  backend/app/main.py.bak-postgres"
Write-Host "  backend/requirements.txt.bak-postgres"
Write-Host ""
Write-Host "Agora rode:"
Write-Host '  git add backend/app/main.py backend/requirements.txt'
Write-Host '  git commit -m "feat: adiciona suporte a Postgres persistente"'
Write-Host '  git push origin main'
