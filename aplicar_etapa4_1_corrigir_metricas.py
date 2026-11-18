from pathlib import Path

ROOT = Path('.')
PAGE = ROOT / 'frontend' / 'js' / 'pages' / 'student' / 'mentor-edu.js'

if not PAGE.exists():
    raise SystemExit('Não encontrei frontend/js/pages/student/mentor-edu.js.')

text = PAGE.read_text(encoding='utf-8-sig', errors='strict')
MARKER = 'MENTOR_EDU_METRICS_FIX_V4_1'

if MARKER in text:
    print('ETAPA 4.1 já está aplicada.')
    raise SystemExit(0)

old = '    const average =\n        metrics?.media_geral ??\n        metrics?.media ??\n        metrics?.average ??\n        metrics?.nota_media ??\n        null;\n\n    const attendance =\n        metrics?.frequencia_percentual ??\n        metrics?.frequencia ??\n        metrics?.attendance ??\n        metrics?.presenca ??\n        null;\n'
new = '    // MENTOR_EDU_METRICS_FIX_V4_1\n    const averageRaw =\n        metrics?.media_geral ??\n        metrics?.media ??\n        metrics?.average ??\n        metrics?.nota_media ??\n        null;\n\n    const attendanceRaw =\n        metrics?.frequencia_percentual ??\n        metrics?.frequencia ??\n        metrics?.attendance ??\n        metrics?.presenca ??\n        null;\n\n    const average = metricNumber(averageRaw);\n    const attendance = metricNumber(attendanceRaw);\n'

if old not in text:
    raise SystemExit('Não encontrei o bloco de métricas esperado da Etapa 4. Nenhuma alteração foi gravada.')

new_text = text.replace(old, new, 1)

if 'const attendance = metricNumber(attendanceRaw);' not in new_text:
    raise SystemExit('A validação falhou. Nenhuma alteração foi gravada.')

backup = PAGE.with_name(PAGE.name + '.backup_etapa4_1_metricas')
if not backup.exists():
    backup.write_text(text, encoding='utf-8')

PAGE.write_text(new_text, encoding='utf-8')

print('')
print('ETAPA 4.1 — MÉTRICAS CORRIGIDAS COM SUCESSO.')
print('')
print('Alterado somente:')
print('- frontend/js/pages/student/mentor-edu.js')
print('')
print('Corrigido:')
print('- frequência em objeto -> percentual numérico')
print('- média em objeto -> valor numérico')
print('- elimina [object Object]%')
print('')
print('Use Ctrl + F5 e clique em Atualizar análise.')
