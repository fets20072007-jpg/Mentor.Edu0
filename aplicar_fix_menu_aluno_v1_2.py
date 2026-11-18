from pathlib import Path

ROOT = Path(".")
FRONT = ROOT / "frontend"
CSS = FRONT / "mentor-ai-student.css"

if not FRONT.exists():
    raise SystemExit("Não encontrei a pasta frontend.")
if not CSS.exists():
    raise SystemExit(
        "Não encontrei frontend/mentor-ai-student.css. "
        "Aplique primeiro o frontend da IA do aluno."
    )

css = CSS.read_text(encoding="utf-8-sig", errors="strict")
marker = "/* MENTOR_AI_MENU_FIX_V1_2 */"
menu_fix = '\n/* MENTOR_AI_MENU_FIX_V1_2 */\n#mentor-ai-nav-item{\n  box-sizing:border-box !important;\n  width:100% !important;\n  min-height:42px !important;\n  margin:0 !important;\n  padding:0 18px !important;\n  display:flex !important;\n  align-items:center !important;\n  justify-content:flex-start !important;\n  gap:12px !important;\n  border:0 !important;\n  border-radius:0 !important;\n  outline:0 !important;\n  background:transparent !important;\n  background-image:none !important;\n  box-shadow:none !important;\n  color:#fff !important;\n  font:inherit !important;\n  font-size:13px !important;\n  font-weight:600 !important;\n  line-height:1 !important;\n  text-align:left !important;\n  cursor:pointer !important;\n  opacity:1 !important;\n}\n\n#mentor-ai-nav-item:hover{\n  background:rgba(255,255,255,.12) !important;\n}\n\n#mentor-ai-nav-item:focus-visible{\n  background:rgba(255,255,255,.15) !important;\n  outline:2px solid rgba(255,255,255,.55) !important;\n  outline-offset:-2px !important;\n}\n\n#mentor-ai-nav-item > span,\n#mentor-ai-nav-item *{\n  color:#fff !important;\n}\n\n#mentor-ai-nav-item .mentor-ai-nav-icon{\n  width:20px !important;\n  height:20px !important;\n  min-width:20px !important;\n  display:inline-grid !important;\n  place-items:center !important;\n  border:0 !important;\n  border-radius:0 !important;\n  background:transparent !important;\n  color:#fff !important;\n  font-size:14px !important;\n  line-height:1 !important;\n}\n\naside #mentor-ai-nav-item,\nnav #mentor-ai-nav-item,\n.sidebar #mentor-ai-nav-item,\n[class*="sidebar"] #mentor-ai-nav-item{\n  background-color:transparent !important;\n  color:#fff !important;\n}\n'

if marker not in css:
    CSS.write_text(css.rstrip() + "\n\n" + menu_fix + "\n", encoding="utf-8")

replacements = {'HistÃ³rico acadÃªmico': 'Histórico acadêmico', 'HistÃ³rico AcadÃªmico': 'Histórico Acadêmico', 'RecomendaÃ§Ãµes': 'Recomendações', 'AvaliaÃ§Ãµes': 'Avaliações', 'FrequÃªncia': 'Frequência', 'ConfiguraÃ§Ãµes': 'Configurações', 'NotificaÃ§Ãµes': 'Notificações', 'CalendÃ¡rio acadÃªmico': 'Calendário acadêmico', 'CalendÃ¡rio AcadÃªmico': 'Calendário Acadêmico', 'HorÃ¡rios': 'Horários', 'ConversaÃ§Ãµes': 'Conversações', 'SugestÃµes': 'Sugestões', 'PontuaÃ§Ã£o': 'Pontuação', 'MÃ©dia': 'Média', 'PrÃ³xima': 'Próxima', 'PrÃ³ximo': 'Próximo', 'acadÃªmico': 'acadêmico', 'AcadÃªmico': 'Acadêmico'}
extensions = {".html", ".js", ".css", ".json"}
changed_files = []

for path in FRONT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in extensions:
        continue

    original = path.read_text(encoding="utf-8-sig", errors="ignore")
    fixed = original

    for bad, good in replacements.items():
        fixed = fixed.replace(bad, good)

    if fixed != original:
        backup = path.with_suffix(path.suffix + ".backup_encoding_v1_2")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")

        path.write_text(fixed, encoding="utf-8")
        changed_files.append(str(path))

print("")
print("FIX MENU DO ALUNO V1.2 APLICADO COM SUCESSO.")
print("")
print("Correções:")
print("- Mentor Edu agora segue o padrão visual da barra lateral roxa")
print("- removido fundo branco do item Mentor Edu")
print("- alinhamento, altura e espaçamento ajustados")
print("- mojibakes conhecidos do menu corrigidos")
print("")
print("Arquivos com texto corrigido:")
if changed_files:
    for item in changed_files:
        print("-", item)
else:
    print("- nenhum texto corrompido adicional encontrado")
print("")
print("Backend e banco: nenhuma alteração.")
