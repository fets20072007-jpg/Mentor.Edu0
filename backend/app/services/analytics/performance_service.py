from app.database.models import StudentAnswer


def calculate_performance(respostas):

    total = len(respostas)

    if total == 0:

        return {

            "total_questoes": 0,

            "acertos": 0,

            "erros": 0,

            "percentual": 0,

            "tempo_medio": 0,

            "nivel": "Sem dados"

        }

    acertos = sum(

        1

        for r in respostas

        if r.correta

    )

    erros = total - acertos

    percentual = round(

        (acertos / total) * 100,

        2

    )

    tempos = [

        r.tempo_resposta

        for r in respostas

        if r.tempo_resposta is not None

    ]

    if len(tempos) > 0:

        tempo_medio = round(

            sum(tempos) / len(tempos),

            2

        )

    else:

        tempo_medio = 0

    if percentual >= 90:

        nivel = "Excelente"

    elif percentual >= 75:

        nivel = "Bom"

    elif percentual >= 60:

        nivel = "Regular"

    else:

        nivel = "Precisa Melhorar"

    return {

        "total_questoes": total,

        "acertos": acertos,

        "erros": erros,

        "percentual": percentual,

        "tempo_medio": tempo_medio,

        "nivel": nivel

    }