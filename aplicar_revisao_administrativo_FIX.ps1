$ErrorActionPreference = "Stop"

function ReadText($path) {
    if (!(Test-Path $path)) {
        throw "Arquivo não encontrado: $path"
    }
    return Get-Content $path -Raw
}

function WriteText($path, $content) {
    Set-Content $path $content -Encoding UTF8
}

# ============================================================
# 1) MODELS.PY
# ============================================================
$path = "backend/app/database/models.py"
$c = ReadText $path

if ($c -notmatch 'contato1 = Column\(String, nullable=True\)') {
    $anchor = '    cargo_administrativo = Column(String, nullable=True)'
    $insert = @'
    cargo_administrativo = Column(String, nullable=True)
    cpf = Column(String, nullable=True)
    matricula = Column(String, nullable=True)
    contato1 = Column(String, nullable=True)
    contato2 = Column(String, nullable=True)
'@
    $c = $c.Replace($anchor, $insert.TrimEnd())
}

# CPF opcional para professor
$c = $c.Replace(
    '    cpf = Column(String, unique=True, nullable=False)',
    '    cpf = Column(String, unique=True, nullable=True)'
)

if ($c -notmatch 'class AcademicEvent\(Base\):') {
    $c += @'

class AcademicEvent(Base):
    __tablename__ = "academic_events"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    tipo = Column(String, default="Evento", nullable=False)
    visibilidade = Column(String, default="todos", nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
'@
}

WriteText $path $c

# ============================================================
# 2) USERS SCHEMA
# ============================================================
$path = "backend/app/schema/users.py"
$c = ReadText $path

if ($c -notmatch 'contato1: Optional\[str\]') {
    $anchor = '    escola: Optional[str] = None'
    $insert = @'
    escola: Optional[str] = None
    contato1: Optional[str] = None
    contato2: Optional[str] = None
'@
    $c = $c.Replace($anchor, $insert.TrimEnd())
}

WriteText $path $c

# ============================================================
# 3) USERS ROUTER
# ============================================================
$path = "backend/app/router/user/users.py"
$c = ReadText $path

# Torna a checagem de CPF de professor opcional
$c = $c -replace '(?ms)if not cpf_normalizado:\s*raise HTTPException\([^)]*detail="CPF[^"]*"\s*\)', ''

# Se houver query de CPF duplicado, só roda quando houver CPF
if ($c -match 'professor_cpf = \(' -and $c -notmatch 'if cpf_normalizado:\s*professor_cpf =') {
    $pattern = '(?ms)(\s*professor_cpf = \(\s*db\.query\(Teacher\).*?\)\s*if professor_cpf:\s*raise HTTPException\([^\)]*detail="Já existe um professor com este CPF\."[^\)]*\))'
    if ($c -match $pattern) {
        $block = $matches[1]
        $indented = ($block -split "`r?`n" | ForEach-Object { "    " + $_ }) -join "`r`n"
        $replacement = "`r`n        if cpf_normalizado:`r`n" + $indented.TrimStart()
        $c = [regex]::Replace($c, $pattern, $replacement, 1)
    }
}

WriteText $path $c

# ============================================================
# 4) MAIN.PY - CALENDAR ROUTER + MIGRATIONS
# ============================================================
$path = "backend/app/main.py"
$c = ReadText $path

if ($c -notmatch 'calendar_router') {
    $importAnchor = 'from app.router.academic.classroom import router as classroom_router'
    $importInsert = @'
from app.router.academic.classroom import router as classroom_router
from app.router.academic.calendar import router as calendar_router
'@
    $c = $c.Replace($importAnchor, $importInsert.TrimEnd())

    $routerAnchor = 'app.include_router(classroom_router)'
    $routerInsert = @'
app.include_router(classroom_router)
app.include_router(calendar_router)
'@
    $c = $c.Replace($routerAnchor, $routerInsert.TrimEnd())
}

# Insere migrations de users se ainda não existirem
if ($c -notmatch '"users": \[') {
    $subjectLine = '        "subjects": [("categoria", "VARCHAR DEFAULT ''Outras'' NOT NULL")],'
    $usersLine = @'
        "users": [("cpf", "VARCHAR"), ("matricula", "VARCHAR"), ("contato1", "VARCHAR"), ("contato2", "VARCHAR")],
        "subjects": [("categoria", "VARCHAR DEFAULT 'Outras' NOT NULL")],
'@
    $c = $c.Replace($subjectLine, $usersLine.TrimEnd())
}

WriteText $path $c

# ============================================================
# 5) FRONTEND MAIN.JS
# ============================================================
$path = "frontend/js/main.js"
$c = ReadText $path

if ($c -notmatch 'renderAcademicCalendar') {
    $importAnchor = 'import { renderProfile } from "./pages/shared/profile.js";'
    $importInsert = @'
import { renderProfile } from "./pages/shared/profile.js";
import { renderAcademicCalendar } from "./pages/shared/academic-calendar.js";
'@
    $c = $c.Replace($importAnchor, $importInsert.TrimEnd())

    $routeAnchor = '        if (route === "profile") return await renderProfile(container);'
    $routeInsert = @'
        if (route === "profile") return await renderProfile(container);
        if (route === "academic-calendar") return await renderAcademicCalendar(container, user);
'@
    $c = $c.Replace($routeAnchor, $routeInsert.TrimEnd())
}

WriteText $path $c

# ============================================================
# 6) SIDEBAR
# ============================================================
$path = "frontend/js/components/sidebar.js"
$c = ReadText $path

if ($c -notmatch 'route: "academic-calendar"') {
    $anchor = '{ route: "schedules", label: "Horários", icon: "calendar" },'
    $insert = @'
{ route: "schedules", label: "Horários", icon: "calendar" },
        { route: "academic-calendar", label: "Calendário acadêmico", icon: "calendar" },
'@
    $c = $c.Replace($anchor, $insert.TrimEnd())
}

$c = $c.Replace(
    '{ route: "notifications", label: "Mensagens", icon: "message", badge: "notifications" },',
    '{ route: "tickets", label: "Chamados e mensagens", icon: "message" },'
)

WriteText $path $c

Write-Host ""
Write-Host "REVISAO ADMINISTRATIVA APLICADA COM SUCESSO." -ForegroundColor Green
Write-Host ""
Write-Host "Agora rode:"
Write-Host 'git add .'
Write-Host 'git commit -m "feat: revisao completa do perfil administrativo"'
Write-Host 'git push origin main'
