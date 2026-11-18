from pathlib import Path
import re
import sys

ROOT = Path.cwd()

BACKEND = (
    ROOT
    / "backend"
    / "app"
    / "router"
    / "ai"
    / "mentor.py"
)

PAGE = (
    ROOT
    / "frontend"
    / "js"
    / "pages"
    / "student"
    / "mentor-edu.js"
)

CSS = (
    ROOT
    / "frontend"
    / "css"
    / "mentor-ai-page.css"
)

for path in (BACKEND, PAGE, CSS):
    if not path.exists():
        raise SystemExit(
            f"ERRO: arquivo necessário não encontrado: {path}"
        )

def read(path):
    return path.read_text(
        encoding="utf-8-sig",
        errors="strict",
    )

backend = read(BACKEND)
page = read(PAGE)
css = read(CSS)

original_backend = backend
original_page = page
original_css = css

BACKEND_BLOCK = '\n# === MENTOR EDU ETAPA 6 - ALERTAS INTELIGENTES DO ALUNO ===\n\ndef _mentor_alert_number(value):\n    try:\n        if value is None or value == "":\n            return None\n        number = float(value)\n        if number != number:\n            return None\n        return number\n    except (TypeError, ValueError):\n        return None\n\n\ndef _mentor_student_subjects(metrics: dict) -> list[dict]:\n    raw = metrics.get("desempenho_por_disciplina") or []\n\n    if isinstance(raw, dict):\n        result = []\n        for name, value in raw.items():\n            if isinstance(value, dict):\n                candidate = (\n                    value.get("media_percentual")\n                    if value.get("media_percentual") is not None\n                    else value.get("percentual")\n                    if value.get("percentual") is not None\n                    else value.get("media")\n                )\n            else:\n                candidate = value\n\n            score = _mentor_alert_number(candidate)\n            if score is not None:\n                result.append({\n                    "disciplina": str(name),\n                    "media_percentual": score,\n                })\n        return result\n\n    if not isinstance(raw, list):\n        return []\n\n    result = []\n\n    for item in raw:\n        if not isinstance(item, dict):\n            continue\n\n        name = (\n            item.get("disciplina")\n            or item.get("nome")\n            or item.get("subject")\n            or item.get("name")\n        )\n\n        candidate = (\n            item.get("media_percentual")\n            if item.get("media_percentual") is not None\n            else item.get("percentual")\n            if item.get("percentual") is not None\n            else item.get("media")\n        )\n\n        score = _mentor_alert_number(candidate)\n\n        if name and score is not None:\n            result.append({\n                "disciplina": str(name),\n                "media_percentual": score,\n            })\n\n    return result\n\n\ndef _mentor_student_alerts(metrics: dict) -> list[dict]:\n    """\n    Alertas pedagógicos do próprio aluno.\n    Reutiliza os indicadores acadêmicos existentes e não cria nova chamada de IA.\n    """\n    alerts = []\n\n    average = _mentor_alert_number(\n        metrics.get("media_geral_percentual")\n    )\n\n    attendance_data = metrics.get("frequencia") or {}\n    attendance = None\n\n    if isinstance(attendance_data, dict):\n        attendance = _mentor_alert_number(\n            attendance_data.get("taxa_presenca")\n            if attendance_data.get("taxa_presenca") is not None\n            else attendance_data.get("percentual")\n        )\n\n    subjects = _mentor_student_subjects(metrics)\n    subjects.sort(\n        key=lambda item: item["media_percentual"]\n    )\n\n    # Usa os mesmos cortes já usados no módulo de alertas do professor.\n    if average is not None:\n        if average < 50:\n            alerts.append({\n                "nivel": "critico",\n                "titulo": "Desempenho geral precisa de atenção",\n                "mensagem": (\n                    f"Sua média geral atual é {average:.1f}%. "\n                    "Vale revisar as avaliações recentes e priorizar "\n                    "os conteúdos com maior dificuldade."\n                ),\n                "acao": "Ver minhas notas",\n                "route": "grades",\n                "prioridade": 100,\n            })\n        elif average < 60:\n            alerts.append({\n                "nivel": "atencao",\n                "titulo": "Há espaço para recuperar desempenho",\n                "mensagem": (\n                    f"Sua média geral atual é {average:.1f}%. "\n                    "Uma revisão focada nas disciplinas com menor "\n                    "resultado pode ajudar."\n                ),\n                "acao": "Ver minhas notas",\n                "route": "grades",\n                "prioridade": 80,\n            })\n        elif average >= 85:\n            alerts.append({\n                "nivel": "positivo",\n                "titulo": "Desempenho geral consistente",\n                "mensagem": (\n                    f"Sua média geral atual é {average:.1f}%. "\n                    "Mantenha a rotina e use o Mentor para consolidar "\n                    "os conteúdos."\n                ),\n                "acao": "Ver disciplinas",\n                "route": "subjects",\n                "prioridade": 25,\n            })\n\n    if attendance is not None:\n        if attendance < 75:\n            alerts.append({\n                "nivel": "critico",\n                "titulo": "Frequência merece atenção imediata",\n                "mensagem": (\n                    f"Sua taxa de presença registrada é {attendance:.1f}%. "\n                    "Consulte o resumo de frequência e confira os registros."\n                ),\n                "acao": "Ver frequência",\n                "route": "attendance",\n                "prioridade": 110,\n            })\n        elif attendance < 80:\n            alerts.append({\n                "nivel": "atencao",\n                "titulo": "Acompanhe sua frequência",\n                "mensagem": (\n                    f"Sua taxa de presença registrada é {attendance:.1f}%. "\n                    "Vale acompanhar as próximas aulas e possíveis pendências."\n                ),\n                "acao": "Ver frequência",\n                "route": "attendance",\n                "prioridade": 90,\n            })\n        elif attendance >= 90:\n            alerts.append({\n                "nivel": "positivo",\n                "titulo": "Boa regularidade nas aulas",\n                "mensagem": (\n                    f"Sua taxa de presença registrada é {attendance:.1f}%. "\n                    "A regularidade está contribuindo para a continuidade "\n                    "dos estudos."\n                ),\n                "acao": "Ver frequência",\n                "route": "attendance",\n                "prioridade": 20,\n            })\n\n    if subjects:\n        weakest = subjects[0]\n        score = weakest["media_percentual"]\n        name = weakest["disciplina"]\n\n        if score < 60:\n            alerts.append({\n                "nivel": "critico" if score < 50 else "atencao",\n                "titulo": f"Prioridade atual: {name}",\n                "mensagem": (\n                    f"O indicador disponível para {name} está em {score:.1f}%. "\n                    "Abra a disciplina ou converse com o Mentor para revisar "\n                    "os pontos mais difíceis."\n                ),\n                "acao": "Ver disciplinas",\n                "route": "subjects",\n                "prioridade": 95 if score < 50 else 75,\n            })\n\n    if not alerts:\n        alerts.append({\n            "nivel": "informativo",\n            "titulo": "Sem alerta acadêmico relevante agora",\n            "mensagem": (\n                "Os dados disponíveis não indicam uma prioridade urgente "\n                "neste momento. Continue acompanhando notas, frequência "\n                "e recomendações."\n            ),\n            "acao": "Conversar com o Mentor",\n            "route": "mentor-edu",\n            "prioridade": 10,\n        })\n\n    alerts.sort(\n        key=lambda item: item.get("prioridade", 0),\n        reverse=True,\n    )\n\n    result = []\n    seen = set()\n\n    for item in alerts:\n        title = item.get("titulo")\n\n        if not title or title in seen:\n            continue\n\n        seen.add(title)\n        clean = dict(item)\n        clean.pop("prioridade", None)\n        result.append(clean)\n\n        if len(result) >= 3:\n            break\n\n    return result\n\n\n@router.get("/student/alerts")\ndef student_alerts_v1(\n    current_user: User = Depends(\n        require_student\n    ),\n    db: Session = Depends(get_db),\n):\n    metrics = build_student_metrics(\n        db,\n        current_user,\n    )\n\n    alerts = _mentor_student_alerts(metrics)\n\n    return {\n        "alerts_version": "1.0",\n        "alertas": alerts,\n        "quantidade": len(alerts),\n        "gerado_por": "regras_pedagogicas_v1",\n    }\n'
FRONTEND_FUNCTIONS = '\n// MENTOR_EDU_ALERTS_V6\nfunction mentorAlertLabel(level) {\n    const labels = {\n        critico: "Prioridade",\n        atencao: "Atenção",\n        positivo: "Positivo",\n        informativo: "Info",\n    };\n\n    return labels[level] || "Info";\n}\n\nfunction mentorAlertsMarkup(items) {\n    const alerts = Array.isArray(items)\n        ? items.slice(0, 3)\n        : [];\n\n    if (!alerts.length) {\n        return `\n            <div class="mentor-empty-state">\n                <strong>Sem alertas por enquanto.</strong>\n                <p>O Mentor continuará acompanhando seus indicadores acadêmicos.</p>\n            </div>\n        `;\n    }\n\n    return `\n        <div class="mentor-smart-alert-list">\n            ${alerts.map(item => {\n                const allowed = [\n                    "critico",\n                    "atencao",\n                    "positivo",\n                    "informativo",\n                ];\n\n                const level = allowed.includes(item?.nivel)\n                    ? item.nivel\n                    : "informativo";\n\n                const title =\n                    item?.titulo ||\n                    "Atualização acadêmica";\n\n                const message =\n                    item?.mensagem ||\n                    "";\n\n                const action =\n                    item?.acao ||\n                    "";\n\n                const route =\n                    item?.route ||\n                    "";\n\n                return `\n                    <article class="mentor-smart-alert is-${level}">\n                        <span class="mentor-smart-alert-badge">\n                            ${escapeHtml(mentorAlertLabel(level))}\n                        </span>\n\n                        <div class="mentor-smart-alert-copy">\n                            <strong>${escapeHtml(title)}</strong>\n                            ${message ? `<p>${escapeHtml(message)}</p>` : ""}\n                        </div>\n\n                        ${action && route ? `\n                            <button\n                                type="button"\n                                class="mentor-smart-alert-action"\n                                data-alert-route="${escapeHtml(route)}"\n                            >\n                                ${escapeHtml(action)}\n                                <span aria-hidden="true">→</span>\n                            </button>\n                        ` : ""}\n                    </article>\n                `;\n            }).join("")}\n        </div>\n    `;\n}\n\nfunction applyStudentAlerts(page, data, navigate) {\n    const target = page.querySelector(\n        \'[data-profile-target="alerts"]\'\n    );\n\n    if (!target) return;\n\n    const alerts =\n        data?.alertas ??\n        data?.alerts ??\n        [];\n\n    target.innerHTML =\n        mentorAlertsMarkup(alerts);\n\n    const firstAlert =\n        Array.isArray(alerts)\n            ? alerts[0]\n            : null;\n\n    const summary = page.querySelector(\n        \'[data-section-summary="alertas"]\'\n    );\n\n    if (summary && firstAlert?.titulo) {\n        summary.textContent =\n            firstAlert.titulo;\n    }\n\n    target\n        .querySelectorAll("[data-alert-route]")\n        .forEach(button => {\n            button.addEventListener(\n                "click",\n                () => {\n                    const route =\n                        button.dataset.alertRoute;\n\n                    if (!route) return;\n\n                    if (route === "mentor-edu") {\n                        page\n                            .querySelector("[data-open-chat]")\n                            ?.click();\n                        return;\n                    }\n\n                    navigate(route);\n                },\n            );\n        });\n}\n\nfunction applyStudentAlertsError(page, error) {\n    const target = page.querySelector(\n        \'[data-profile-target="alerts"]\'\n    );\n\n    if (!target) return;\n\n    target.innerHTML = errorMarkup(\n        error?.message ||\n        "Não foi possível carregar os alertas agora.",\n    );\n}\n\nasync function loadStudentAlerts(\n    page,\n    navigate,\n) {\n    const target = page.querySelector(\n        \'[data-profile-target="alerts"]\'\n    );\n\n    if (target) {\n        target.innerHTML =\n            loadingMarkup("Verificando alertas...");\n    }\n\n    try {\n        const data = await api.get(\n            "/mentor-ai/student/alerts"\n        );\n\n        if (!document.body.contains(page)) {\n            return;\n        }\n\n        applyStudentAlerts(\n            page,\n            data,\n            navigate,\n        );\n    } catch (error) {\n        console.error(\n            "[Mentor Edu] Falha ao carregar alertas:",\n            error,\n        );\n\n        if (document.body.contains(page)) {\n            applyStudentAlertsError(\n                page,\n                error,\n            );\n        }\n    }\n}\n'
ALERTS_CSS = '\n/* MENTOR_EDU_ALERTS_V6 */\n.mentor-smart-alert-list {\n    display: grid;\n    gap: 10px;\n}\n\n.mentor-smart-alert {\n    display: grid;\n    grid-template-columns: auto minmax(0, 1fr) auto;\n    align-items: center;\n    gap: 12px;\n    padding: 14px;\n    border: 1px solid #ebe5f2;\n    border-radius: 14px;\n    background: #fff;\n}\n\n.mentor-smart-alert.is-critico {\n    border-color: #fecaca;\n    background: #fffafa;\n}\n\n.mentor-smart-alert.is-atencao {\n    border-color: #fde68a;\n    background: #fffdf5;\n}\n\n.mentor-smart-alert.is-positivo {\n    border-color: #bbf7d0;\n    background: #f8fff9;\n}\n\n.mentor-smart-alert.is-informativo {\n    border-color: #ddd6fe;\n    background: #fbfaff;\n}\n\n.mentor-smart-alert-badge {\n    min-width: 68px;\n    padding: 6px 8px;\n    border-radius: 999px;\n    background: #f3f0f8;\n    color: #6f6478;\n    font-size: 9px;\n    font-weight: 900;\n    letter-spacing: .03em;\n    text-align: center;\n    text-transform: uppercase;\n}\n\n.mentor-smart-alert.is-critico .mentor-smart-alert-badge {\n    background: #fee2e2;\n    color: #b91c1c;\n}\n\n.mentor-smart-alert.is-atencao .mentor-smart-alert-badge {\n    background: #fef3c7;\n    color: #92400e;\n}\n\n.mentor-smart-alert.is-positivo .mentor-smart-alert-badge {\n    background: #dcfce7;\n    color: #166534;\n}\n\n.mentor-smart-alert.is-informativo .mentor-smart-alert-badge {\n    background: #ede9fe;\n    color: #6d28d9;\n}\n\n.mentor-smart-alert-copy {\n    min-width: 0;\n}\n\n.mentor-smart-alert-copy strong {\n    display: block;\n    color: #30283a;\n    font-size: 12px;\n}\n\n.mentor-smart-alert-copy p {\n    margin: 4px 0 0;\n    color: #766d7f;\n    font-size: 10px;\n    line-height: 1.55;\n}\n\n.mentor-smart-alert-action {\n    min-height: 34px;\n    padding: 0 10px;\n    border: 1px solid #e4dcf0;\n    border-radius: 10px;\n    background: #fff;\n    color: #6d28d9;\n    cursor: pointer;\n    font: inherit;\n    font-size: 9px;\n    font-weight: 900;\n    white-space: nowrap;\n}\n\n.mentor-smart-alert-action:hover {\n    border-color: #c4b5fd;\n    background: #faf8ff;\n}\n\n@media (max-width: 720px) {\n    .mentor-smart-alert {\n        grid-template-columns: 1fr;\n        align-items: start;\n    }\n\n    .mentor-smart-alert-badge,\n    .mentor-smart-alert-action {\n        justify-self: start;\n    }\n}\n'
OLD_ALERT_BLOCK = '    {\n        id: "alertas",\n        eyebrow: "Atenção",\n        title: "Alertas inteligentes",\n        icon: "◉",\n        summary: "Avisos relevantes, sem encher a tela de informação.",\n        body: `\n            <div class="mentor-alert-preview">\n                <span class="mentor-alert-dot"></span>\n                <div>\n                    <strong>Alertas inteligentes entram depois do perfil e do chat.</strong>\n                    <p>Esta área será conectada às avaliações, frequência e prioridades acadêmicas.</p>\n                </div>\n            </div>\n        `,\n    },'
NEW_ALERT_BLOCK = '    {\n        id: "alertas",\n        eyebrow: "Atenção",\n        title: "Alertas inteligentes",\n        icon: "◉",\n        summary: "Verificando seus indicadores acadêmicos.",\n        target: "alerts",\n    },'

# -------------------------------------------------
# 1. Backend
# -------------------------------------------------
if (
    "MENTOR EDU ETAPA 6 - ALERTAS INTELIGENTES DO ALUNO"
    not in backend
):
    anchor = '@router.post("/test-student-tutor")'

    pos = backend.find(anchor)

    if pos == -1:
        anchor = '@router.post("/teacher/questions")'
        pos = backend.find(anchor)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei um ponto seguro no mentor.py. "
            "Nenhuma alteração foi salva."
        )

    backend = (
        backend[:pos]
        + BACKEND_BLOCK.strip()
        + "\n\n"
        + backend[pos:]
    )

# -------------------------------------------------
# 2. Funções do frontend
# -------------------------------------------------
if "MENTOR_EDU_ALERTS_V6" not in page:
    anchor = "const sections = ["
    pos = page.find(anchor)

    if pos == -1:
        raise SystemExit(
            "ERRO: não encontrei const sections em mentor-edu.js. "
            "Nenhuma alteração foi salva."
        )

    page = (
        page[:pos]
        + FRONTEND_FUNCTIONS.strip()
        + "\n\n"
        + page[pos:]
    )

# -------------------------------------------------
# 3. Card Alertas
# -------------------------------------------------
if 'target: "alerts"' not in page:
    if OLD_ALERT_BLOCK not in page:
        raise SystemExit(
            "ERRO: não encontrei o bloco atual de Alertas inteligentes. "
            "Nenhuma alteração foi salva."
        )

    page = page.replace(
        OLD_ALERT_BLOCK,
        NEW_ALERT_BLOCK,
        1,
    )

# -------------------------------------------------
# 4. Atualizar análise também atualiza alertas
# -------------------------------------------------
old_refresh_targets = (
    '["profile", "strengths", "attention", "suggestions"]'
)

new_refresh_targets = (
    '["profile", "strengths", "attention", '
    '"suggestions", "alerts"]'
)

if old_refresh_targets in page:
    page = page.replace(
        old_refresh_targets,
        new_refresh_targets,
        1,
    )

refresh_line = (
    '        loadStudentProfile(page, user, { force: true });'
)

refresh_with_alerts = (
    refresh_line
    + "\n"
    + "        loadStudentAlerts(page, navigate);"
)

if (
    refresh_line in page
    and refresh_with_alerts not in page
):
    page = page.replace(
        refresh_line,
        refresh_with_alerts,
        1,
    )

# -------------------------------------------------
# 5. Carregamento inicial
# -------------------------------------------------
old_final = (
    "    loadStudentProfile(page, user);\n"
    "}"
)

new_final = (
    "    loadStudentProfile(page, user);\n"
    "    loadStudentAlerts(page, navigate);\n"
    "}"
)

if (
    "loadStudentAlerts(page, navigate);"
    not in page[-700:]
):
    if old_final not in page:
        raise SystemExit(
            "ERRO: não encontrei o carregamento final do perfil. "
            "Nenhuma alteração foi salva."
        )

    page = page.replace(
        old_final,
        new_final,
        1,
    )

# -------------------------------------------------
# 6. CSS
# -------------------------------------------------
if "MENTOR_EDU_ALERTS_V6" not in css:
    css = (
        css.rstrip()
        + "\n\n"
        + ALERTS_CSS.strip()
        + "\n"
    )

# -------------------------------------------------
# 7. Validações
# -------------------------------------------------
checks = {
    "endpoint": (
        '@router.get("/student/alerts")'
        in backend
    ),
    "função backend": (
        "_mentor_student_alerts"
        in backend
    ),
    "função frontend": (
        "function loadStudentAlerts"
        in page
    ),
    "target alertas": (
        'target: "alerts"'
        in page
    ),
    "carregamento": (
        "loadStudentAlerts(page, navigate);"
        in page
    ),
    "css": (
        "MENTOR_EDU_ALERTS_V6"
        in css
    ),
}

failed = [
    name
    for name, ok in checks.items()
    if not ok
]

if failed:
    raise SystemExit(
        "ERRO: validação da Etapa 6 falhou. "
        "Nenhuma alteração foi salva: "
        + ", ".join(failed)
    )

try:
    compile(
        backend,
        str(BACKEND),
        "exec",
    )
except SyntaxError as exc:
    raise SystemExit(
        "ERRO: o backend ficaria com erro de sintaxe. "
        "Nenhuma alteração foi salva.\n"
        f"Linha {exc.lineno}: {exc.msg}"
    )

if (
    backend == original_backend
    and page == original_page
    and css == original_css
):
    print(
        "ETAPA 6 já está aplicada. "
        "Nenhuma alteração necessária."
    )
    sys.exit(0)

# -------------------------------------------------
# 8. Backups e gravação
# -------------------------------------------------
backups = (
    (
        BACKEND,
        original_backend,
        BACKEND.with_name(
            BACKEND.name
            + ".backup_etapa6_alertas"
        ),
    ),
    (
        PAGE,
        original_page,
        PAGE.with_name(
            PAGE.name
            + ".backup_etapa6_alertas"
        ),
    ),
    (
        CSS,
        original_css,
        CSS.with_name(
            CSS.name
            + ".backup_etapa6_alertas"
        ),
    ),
)

for source_path, source_text, backup in backups:
    if not backup.exists():
        backup.write_text(
            source_text,
            encoding="utf-8",
        )

BACKEND.write_text(
    backend,
    encoding="utf-8",
)

PAGE.write_text(
    page,
    encoding="utf-8",
)

CSS.write_text(
    css,
    encoding="utf-8",
)

print()
print("======================================================")
print(" MENTOR.EDU - ETAPA 6 ALERTAS INTELIGENTES APLICADA")
print("======================================================")
print()
print("Alterados:")
print("- backend/app/router/ai/mentor.py")
print("- frontend/js/pages/student/mentor-edu.js")
print("- frontend/css/mentor-ai-page.css")
print()
print("Novo endpoint:")
print("- GET /mentor-ai/student/alerts")
print()
print("Funcionamento:")
print("- usa dados acadêmicos reais já existentes")
print("- considera média, frequência e disciplina prioritária")
print("- mostra no máximo 3 alertas")
print("- possui atalhos para Notas, Frequência e Disciplinas")
print("- não cria nova chamada de IA ao carregar a página")
print()
print("Validação de sintaxe do backend: OK")
print()
print("Agora reinicie o backend e use Ctrl + F5.")
