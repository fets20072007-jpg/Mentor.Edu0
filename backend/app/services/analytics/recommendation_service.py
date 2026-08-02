from app.database.models import User


def generate_schedule(user: User):

    cronograma = []

    horas = user.horas_estudo or 2

    favoritas = []

    if user.materias_favoritas:

        favoritas = [

            materia.strip()

            for materia in

            user.materias_favoritas.split(",")

        ]

    dificuldades = []

    if user.dificuldades:

        dificuldades = [

            materia.strip()

            for materia in

            user.dificuldades.split(",")

        ]

    prioridade = []

    prioridade.extend(dificuldades)

    prioridade.extend(favoritas)

    if len(prioridade) == 0:

        prioridade = [

            "Matemática",

            "Português",

            "História"

        ]

    dias = [

        "Segunda",

        "Terça",

        "Quarta",

        "Quinta",

        "Sexta"

    ]

    for dia in dias:

        cronograma.append({

            "dia": dia,

            "horas": horas,

            "materias": prioridade[:3]

        })

    return cronograma