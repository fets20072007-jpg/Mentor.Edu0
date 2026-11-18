from pathlib import Path

ROOT = Path(".")
FRONT = ROOT / "frontend"

if not FRONT.exists():
    raise SystemExit(
        "Não encontrei a pasta frontend. Rode este script na raiz do Mentor.Edu."
    )

REPLACEMENTS = {'DisponÃveis': 'Disponíveis', 'HistÃ³rico': 'Histórico', 'HistÃ³rico acadêmico': 'Histórico acadêmico', 'SessÃµes de estudo': 'Sessões de estudo', 'HistÃ³rico AcadÃªmico': 'Histórico Acadêmico', 'HistÃ³rico acadÃªmico': 'Histórico acadêmico', 'AvaliaÃ§Ãµes': 'Avaliações', 'AvaliaÃ§Ã£o': 'Avaliação', 'FrequÃªncia': 'Frequência', 'RecomendaÃ§Ãµes': 'Recomendações', 'ConfiguraÃ§Ãµes': 'Configurações', 'NotificaÃ§Ãµes': 'Notificações', 'CalendÃ¡rio acadÃªmico': 'Calendário acadêmico', 'CalendÃ¡rio AcadÃªmico': 'Calendário Acadêmico', 'HorÃ¡rios': 'Horários', 'ConversaÃ§Ãµes': 'Conversações', 'SugestÃµes': 'Sugestões', 'PontuaÃ§Ã£o': 'Pontuação', 'PrÃ³xima': 'Próxima', 'PrÃ³ximo': 'Próximo', 'MÃ©dia': 'Média', 'mÃ©dia': 'média', 'AcadÃªmico': 'Acadêmico', 'acadÃªmico': 'acadêmico', 'DisponÃ\xadveis': 'Disponíveis', 'SessÃ£o': 'Sessão', 'sessÃ£o': 'sessão', 'SessÃµes': 'Sessões', 'sessÃµes': 'sessões', 'InformaÃ§Ãµes': 'Informações', 'informaÃ§Ãµes': 'informações', 'OpÃ§Ãµes': 'Opções', 'opÃ§Ãµes': 'opções', 'AtenÃ§Ã£o': 'Atenção', 'atenÃ§Ã£o': 'atenção', 'EvoluÃ§Ã£o': 'Evolução', 'evoluÃ§Ã£o': 'evolução', 'OrganizaÃ§Ã£o': 'Organização', 'organizaÃ§Ã£o': 'organização'}
EXTENSIONS = {".html", ".js", ".css", ".json", ".txt"}

changed = []
remaining = []

for path in FRONT.rglob("*"):
    if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
        continue

    original = path.read_text(
        encoding="utf-8-sig",
        errors="ignore",
    )
    fixed = original

    for bad, good in REPLACEMENTS.items():
        fixed = fixed.replace(bad, good)

    if fixed != original:
        backup = path.with_suffix(
            path.suffix + ".backup_textos_v1_3"
        )
        if not backup.exists():
            backup.write_text(
                original,
                encoding="utf-8",
            )

        path.write_text(
            fixed,
            encoding="utf-8",
        )
        changed.append(str(path))

    # Procura restos de mojibake depois das correções.
    final_text = fixed
    for number, line in enumerate(
        final_text.splitlines(),
        start=1,
    ):
        if "Ã" in line or "Â" in line or "â€" in line:
            remaining.append(
                (str(path), number, line.strip()[:180])
            )

print("")
print("FIX DE ACENTUAÇÃO V1.3 APLICADO COM SUCESSO.")
print("")

print("Arquivos corrigidos:")
if changed:
    for item in changed:
        print("-", item)
else:
    print("- nenhum arquivo precisou de alteração")

print("")
if remaining:
    print("ATENÇÃO: ainda encontrei possíveis textos corrompidos:")
    for path, line_no, content in remaining[:50]:
        print(f"- {path}:{line_no} -> {content}")
    if len(remaining) > 50:
        print(f"- ... e mais {len(remaining)-50} ocorrência(s)")
else:
    print("Nenhum mojibake comum restante foi encontrado no frontend.")

print("")
print("Textos principais esperados:")
print("- Disponíveis")
print("- Histórico")
print("- Histórico acadêmico")
print("- Sessões de estudo")
print("- Recomendações")
print("- Horários")
print("- Notificações")
print("")
print("Backend e banco: nenhuma alteração.")
