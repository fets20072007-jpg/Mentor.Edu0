from app.database.models import StudentAnswer


def generate_smart_recommendation(respostas):

    total = len(respostas)

    erros = sum(

        1

        for r in respostas

        if not r.correta

    )

    if total == 0:

        return [

            {

                "materia": "Sem dados",

                "motivo": "O aluno ainda não respondeu questões.",

                "livro": "-",

                "capitulo": "-",

                "paginas": "-",

                "video": "-",

                "exercicios": 0,

                "exemplo_pratico": "-"

            }

        ]

    percentual_erros = erros / total

    if percentual_erros >= 0.5:

        return [

            {

                "materia": "Matemática",

                "motivo": "Grande quantidade de erros.",

                "livro": "Matemática Moderna",

                "capitulo": "Capítulo 4",

                "paginas": "52-63",

                "video": "Equação do 2º Grau",

                "exercicios": 10,

                "exemplo_pratico": "Aplicação em Engenharia"

            }

        ]

    return [

        {

            "materia": "Continue",

            "motivo": "Bom desempenho.",

            "livro": "Revisão Geral",

            "capitulo": "Livre",

            "paginas": "-",

            "video": "Revisão",

            "exercicios": 5,

            "exemplo_pratico": "Continue praticando"

        }

    ]