from datetime import date, datetime, time

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.models import (
    Assessment,
    Question,
    StudentAnswer,
    User,
    Teacher,
    Classroom,
    Subject, 
    Enrollment
)

# =========================================================
# AVALIAÃ‡Ã•ES
# =========================================================

def create_assessment(
    db: Session,
    user_id: int,
    assessment
):
    # Localiza o perfil Teacher do usuÃ¡rio autenticado
    teacher = (
        db.query(Teacher)
        .filter(Teacher.user_id == user_id)
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor nÃ£o encontrado."
        )

    # A disciplina precisa pertencer ao professor autenticado
    subject = (
        db.query(Subject)
        .filter(
            Subject.id == assessment.subject_id,
            Subject.teacher_id == teacher.id
        )
        .first()
    )

    if not subject:
        raise HTTPException(
            status_code=403,
            detail="Disciplina nÃ£o encontrada ou nÃ£o pertence a este professor."
        )

    # A turma vem da prÃ³pria disciplina
    classroom = subject.classroom

    if not classroom:
        raise HTTPException(
            status_code=400,
            detail="A disciplina nÃ£o estÃ¡ vinculada a uma turma."
        )

    nova = Assessment(
        titulo=assessment.titulo,
        descricao=assessment.descricao,
        tipo=assessment.tipo,
        arquivo=assessment.arquivo,
        arquivo_nome=assessment.arquivo_nome,
        data=assessment.data,
        valor=assessment.valor,

        ativa=assessment.ativa,
        semestre=assessment.semestre,
        ano_letivo=assessment.ano_letivo,

        teacher_id=teacher.id,
        subject_id=subject.id,

        # NÃ£o vem mais do formulÃ¡rio
        classroom_id=classroom.id
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)

    return nova


def get_all_assessments(
    db: Session
):
    return db.query(Assessment).all()


def get_assessment_by_id(
    db: Session,
    assessment_id: int
):
    assessment = (
        db.query(Assessment)
        .filter(Assessment.id == assessment_id)
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="AvaliaÃ§Ã£o nÃ£o encontrada."
        )

    return assessment


def update_assessment(
    db: Session,
    assessment_id: int,
    data,
    teacher_user_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == teacher_user_id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor nÃ£o encontrado."
        )

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id,
            Assessment.teacher_id == teacher.id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="AvaliaÃ§Ã£o nÃ£o encontrada ou nÃ£o pertence a este professor."
        )

    update_data = data.model_dump(
        exclude_unset=True
    )
    
    # A turma nunca pode ser alterada diretamente
    update_data.pop("classroom_id", None)

    # Se o professor estiver alterando a disciplina
    if "subject_id" in update_data:

        subject_id = update_data["subject_id"]

        subject = (
            db.query(Subject)
            .filter(
                Subject.id == subject_id,
                Subject.teacher_id == teacher.id
            )
            .first()
        )

        if not subject:
            raise HTTPException(
                status_code=403,
                detail="Disciplina nÃ£o encontrada ou nÃ£o pertence a este professor."
            )

        classroom = subject.classroom

        if not classroom:
            raise HTTPException(
                status_code=400,
                detail="A disciplina nÃ£o estÃ¡ vinculada a uma turma."
            )

        # Atualiza os dois juntos
        assessment.subject_id = subject.id
        assessment.classroom_id = classroom.id

        # Evita processar subject_id novamente abaixo
        update_data.pop("subject_id")

    for field, value in update_data.items():
        setattr(
            assessment,
            field,
            value
        )

    db.commit()
    db.refresh(assessment)

    return assessment


# =========================================================
# RESULTADO INDIVIDUAL
# =========================================================

def get_student_assessment_result(
    db: Session,
    assessment_id: int,
    user_id: int
):
    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="AvaliaÃ§Ã£o nÃ£o encontrada."
        )

        # -----------------------------------------------------
    # LOCALIZA O ALUNO
    # -----------------------------------------------------

    student = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Aluno nÃ£o encontrado."
        )

    tipo = (
        student.tipo
        or ""
    ).strip().lower()

    if tipo != "aluno":
        raise HTTPException(
            status_code=404,
            detail="Aluno nÃ£o encontrado."
        )

    # -----------------------------------------------------
    # SEGURANÃ‡A:
    # RESULTADO SOMENTE DA TURMA DO ALUNO
    # -----------------------------------------------------

    # -----------------------------------------------------
    # SEGURANÃ‡A:
    # O ALUNO PRECISA POSSUIR MATRÃCULA NA TURMA
    # DA AVALIAÃ‡ÃƒO.
    #
    # Aqui nÃ£o exigimos matrÃ­cula ativa porque o aluno
    # tambÃ©m pode consultar resultados histÃ³ricos.
    # -----------------------------------------------------

    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == student.id,
            Enrollment.classroom_id == assessment.classroom_id
        )
        .first()
    )

    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Resultado nÃ£o encontrado ou sem acesso."
        )

    questions = (
        db.query(Question)
        .filter(
            Question.assessment_id == assessment_id
        )
        .all()
    )

    if not questions:
        return {
            "assessment_id": assessment_id,
            "user_id": user_id,

            "total_questoes": 0,
            "questoes_respondidas": 0,
            "questoes_corrigidas": 0,
            "questoes_pendentes": 0,

            "pontos_obtidos": 0,
            "pontos_possiveis": 0,

            "percentual": 0,
            "nota_final": 0
        }

    question_ids = [
        question.id
        for question in questions
    ]

    answers = (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.user_id == user_id,
            StudentAnswer.question_id.in_(
                question_ids
            )
        )
        .order_by(StudentAnswer.id)
        .all()
    )

    # Se houver mais de uma resposta para uma questÃ£o,
    # utiliza a mais recente.
    latest_answers = {}

    for answer in answers:
        latest_answers[
            answer.question_id
        ] = answer

    total_questoes = len(questions)

    questoes_respondidas = len(
        latest_answers
    )

    questoes_corrigidas = 0

    pontos_obtidos = 0.0

    pontos_possiveis = sum(
        question.peso or 1
        for question in questions
    )

    for answer in latest_answers.values():

        if answer.percentual_final is not None:

            questoes_corrigidas += 1

            pontos_obtidos += (
                answer.pontuacao_obtida or 0
            )

    # Aqui "pendente" significa:
    # respondeu, mas ainda nÃ£o foi corrigida.
    questoes_pendentes = (
        questoes_respondidas
        - questoes_corrigidas
    )

    if pontos_possiveis > 0:

        percentual = (
            pontos_obtidos
            / pontos_possiveis
        ) * 100

    else:

        percentual = 0

    nota_final = (
        percentual / 100
    ) * (
        assessment.valor or 10
    )

    return {
        "assessment_id": assessment_id,
        "user_id": user_id,

        "total_questoes": total_questoes,
        "questoes_respondidas": questoes_respondidas,
        "questoes_corrigidas": questoes_corrigidas,
        "questoes_pendentes": questoes_pendentes,

        "pontos_obtidos": round(
            pontos_obtidos,
            2
        ),

        "pontos_possiveis": round(
            pontos_possiveis,
            2
        ),

        "percentual": round(
            percentual,
            2
        ),

        "nota_final": round(
            nota_final,
            2
        )
    }


# =========================================================
# RESULTADO DE UM ALUNO PARA O PROFESSOR
# =========================================================

def get_student_result_for_teacher(
    db: Session,
    assessment_id: int,
    student_id: int
):
    return get_student_assessment_result(
        db,
        assessment_id,
        student_id
    )


# =========================================================
# RESULTADOS DA TURMA
# =========================================================

def get_assessment_results(
    db: Session,
    assessment_id: int
):
    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="AvaliaÃ§Ã£o nÃ£o encontrada."
        )

    questions = (
        db.query(Question)
        .filter(
            Question.assessment_id
            == assessment_id
        )
        .all()
    )

    if not questions:
        return []

    question_ids = [
        question.id
        for question in questions
    ]

    answers = (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.question_id.in_(
                question_ids
            )
        )
        .all()
    )

    student_ids = list(
        {
            answer.user_id
            for answer in answers
        }
    )

    results = []

    for student_id in student_ids:

        result = (
            get_student_assessment_result(
                db,
                assessment_id,
                student_id
            )
        )

        student = (
            db.query(User)
            .filter(
                User.id == student_id
            )
            .first()
        )

        results.append({
            "user_id": student_id,

            "nome": (
                student.nome
                if student
                else "Aluno"
            ),

            "percentual":
                result["percentual"],

            "nota_final":
                result["nota_final"],

            "questoes_respondidas":
                result[
                    "questoes_respondidas"
                ],

            "questoes_corrigidas":
                result[
                    "questoes_corrigidas"
                ],

            "questoes_pendentes":
                result[
                    "questoes_pendentes"
                ]
        })

    return results


# =========================================================
# HISTÃ“RICO DO ALUNO
# =========================================================

def get_student_assessment_history(
    db: Session,
    user_id: int
):
    assessments = (
        db.query(Assessment)
        .all()
    )

    history = []

    for assessment in assessments:

        questions = (
            db.query(Question)
            .filter(
                Question.assessment_id
                == assessment.id
            )
            .all()
        )

        if not questions:
            continue

        question_ids = [
            question.id
            for question in questions
        ]

        answer = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.user_id
                == user_id,

                StudentAnswer.question_id.in_(
                    question_ids
                )
            )
            .first()
        )

        # NÃ£o coloca no histÃ³rico
        # avaliaÃ§Ãµes nunca respondidas.
        if not answer:
            continue

        result = (
            get_student_assessment_result(
                db,
                assessment.id,
                user_id
            )
        )

        percentual = float(result["percentual"] or 0)

        history.append({
            "assessment_id": assessment.id,
            "titulo": assessment.titulo,
            "subject_id": assessment.subject_id,
            "classroom_id": assessment.classroom_id,
            "teacher_id": assessment.teacher_id,
            "tipo": assessment.tipo,
            "semestre": assessment.semestre,
            "ano_letivo": assessment.ano_letivo,
            "percentual": percentual,
            "nota_final": float(result["nota_final"] or 0),
            "status_desempenho": classificar_desempenho(percentual)
        })

    return history


# =========================================================
# CLASSIFICAÃ‡ÃƒO DE DESEMPENHO
# =========================================================

def classificar_desempenho(
    percentual: float
):

    if percentual < 50:
        return "Baixo"

    if percentual < 70:
        return "Regular"

    if percentual < 85:
        return "Bom"

    return "Excelente"


# =========================================================
# HISTÃ“RICO DO ALUNO COM FILTROS
# =========================================================

def get_student_assessment_history_filtered(
    db: Session,
    user_id: int,

    subject_id: int | None = None,
    semestre: int | None = None,
    ano_letivo: int | None = None,

    classroom_id: int | None = None,
    teacher_id: int | None = None,

    tipo: str | None = None,

    data_inicio: date | None = None,
    data_fim: date | None = None,

    status_desempenho: str | None = None
):

    assessments_query = (
        db.query(Assessment)
    )

    # DISCIPLINA
    if subject_id is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.subject_id
                == subject_id
            )
        )

    # SEMESTRE
    if semestre is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.semestre
                == semestre
            )
        )

    # ANO LETIVO
    if ano_letivo is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.ano_letivo
                == ano_letivo
            )
        )

    # TURMA
    if classroom_id is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.classroom_id
                == classroom_id
            )
        )

    # PROFESSOR
    if teacher_id is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.teacher_id
                == teacher_id
            )
        )

    # TIPO DE AVALIAÃ‡ÃƒO
    if tipo is not None:

        assessments_query = (
            assessments_query.filter(
                Assessment.tipo
                == tipo
            )
        )

    # DATA INICIAL
    if data_inicio is not None:

        inicio = datetime.combine(
            data_inicio,
            time.min
        )

        assessments_query = (
            assessments_query.filter(
                Assessment.data >= inicio
            )
        )

    # DATA FINAL
    if data_fim is not None:

        fim = datetime.combine(
            data_fim,
            time.max
        )

        assessments_query = (
            assessments_query.filter(
                Assessment.data <= fim
            )
        )

    assessments = (
        assessments_query.all()
    )

    history = []

    for assessment in assessments:

        questions = (
            db.query(Question)
            .filter(
                Question.assessment_id
                == assessment.id
            )
            .all()
        )

        if not questions:
            continue

        question_ids = [
            question.id
            for question in questions
        ]

        answer = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.user_id
                == user_id,

                StudentAnswer.question_id.in_(
                    question_ids
                )
            )
            .first()
        )

        # O aluno nÃ£o respondeu
        # essa avaliaÃ§Ã£o.
        if not answer:
            continue

        result = (
            get_student_assessment_result(
                db,
                assessment.id,
                user_id
            )
        )

        status = (
            classificar_desempenho(
                result["percentual"]
            )
        )

        if status_desempenho is not None:

            if (
                status.lower()
                != status_desempenho.lower()
            ):
                continue

        history.append({
            "assessment_id":
                assessment.id,

            "titulo":
                assessment.titulo,

            "subject_id":
                assessment.subject_id,

            "classroom_id":
                assessment.classroom_id,

            "teacher_id":
                assessment.teacher_id,

            "tipo":
                assessment.tipo,

            "semestre":
                assessment.semestre,

            "ano_letivo":
                assessment.ano_letivo,

            "percentual":
                result["percentual"],

            "nota_final":
                result["nota_final"],

            "status_desempenho":
                status
        })

    return history

def get_student_summary(
    db: Session,
    user_id: int
):
    history = get_student_assessment_history(
        db,
        user_id
    )

    if not history:
        return {
            "avaliacoes_realizadas": 0,
            "media_geral": 0,
            "percentual_medio": 0,
            "melhor_nota": None,
            "pior_nota": None,
            "melhor_percentual": None,
            "pior_percentual": None,
            "status_geral": "Sem dados"
        }

    notas = [
        item["nota_final"]
        for item in history
    ]

    percentuais = [
        item["percentual"]
        for item in history
    ]

    media_geral = (
        sum(notas)
        / len(notas)
    )

    percentual_medio = (
        sum(percentuais)
        / len(percentuais)
    )

    return {
        "avaliacoes_realizadas":
            len(history),

        "media_geral":
            round(media_geral, 2),

        "percentual_medio":
            round(percentual_medio, 2),

        "melhor_nota":
            round(max(notas), 2),

        "pior_nota":
            round(min(notas), 2),

        "melhor_percentual":
            round(max(percentuais), 2),

        "pior_percentual":
            round(min(percentuais), 2),

        "status_geral":
            classificar_desempenho(
                percentual_medio
            )
    }

def get_student_summary_by_subject(
    db: Session,
    user_id: int
):
    history = get_student_assessment_history(
        db,
        user_id
    )

    subjects = {}

    for item in history:
        subject_id = item["subject_id"]

        if subject_id not in subjects:
            subjects[subject_id] = {
                "notas": [],
                "percentuais": []
            }

        subjects[subject_id]["notas"].append(
            item["nota_final"]
        )

        subjects[subject_id]["percentuais"].append(
            item["percentual"]
        )

    results = []

    for subject_id, data in subjects.items():

        media = (
            sum(data["notas"])
            / len(data["notas"])
        )

        percentual_medio = (
            sum(data["percentuais"])
            / len(data["percentuais"])
        )

        results.append({
            "subject_id": subject_id,

            "avaliacoes_realizadas":
                len(data["notas"]),

            "media":
                round(media, 2),

            "percentual_medio":
                round(percentual_medio, 2),

            "status":
                classificar_desempenho(
                    percentual_medio
                )
        })

    return results

def get_student_evolution(
    db: Session,
    user_id: int
):
    history = get_student_assessment_history(
        db,
        user_id
    )

    periods = {}

    for item in history:
        ano = item["ano_letivo"]
        semestre = item["semestre"]

        key = (ano, semestre)

        if key not in periods:
            periods[key] = {
                "notas": [],
                "percentuais": []
            }

        periods[key]["notas"].append(
            item["nota_final"]
        )

        periods[key]["percentuais"].append(
            item["percentual"]
        )

    results = []

    for (ano, semestre), data in sorted(periods.items()):

        media = (
            sum(data["notas"])
            / len(data["notas"])
        )

        percentual_medio = (
            sum(data["percentuais"])
            / len(data["percentuais"])
        )

        results.append({
            "ano_letivo": ano,
            "semestre": semestre,

            "avaliacoes_realizadas":
                len(data["notas"]),

            "media":
                round(media, 2),

            "percentual_medio":
                round(percentual_medio, 2),

            "status":
                classificar_desempenho(
                    percentual_medio
                )
        })

    return results

# =========================================================
# ESCOPO PEDAGÃ“GICO DO PROFESSOR / DT
# =========================================================

def get_teacher_accessible_classroom_ids(
    db: Session,
    teacher: Teacher
):
    # Turmas onde o professor leciona
    taught_classrooms = (
        db.query(Subject.classroom_id)
        .filter(
            Subject.teacher_id == teacher.id
        )
        .all()
    )

    taught_ids = {
        item[0]
        for item in taught_classrooms
        if item[0] is not None
    }

    # Turmas onde ele Ã© Diretor de Turma
    dt_classrooms = (
        db.query(Classroom.id)
        .filter(
            Classroom.teacher_id == teacher.id
        )
        .all()
    )

    dt_ids = {
        item[0]
        for item in dt_classrooms
        if item[0] is not None
    }

    return taught_ids | dt_ids


def get_teacher_scope_assessments_query(
    db: Session,
    teacher: Teacher
):
    dt_classrooms = (
        db.query(Classroom.id)
        .filter(
            Classroom.teacher_id == teacher.id
        )
        .all()
    )

    dt_classroom_ids = [
        item[0]
        for item in dt_classrooms
    ]

    # Professor comum:
    # apenas avaliaÃ§Ãµes prÃ³prias.
    #
    # DT:
    # avaliaÃ§Ãµes prÃ³prias +
    # avaliaÃ§Ãµes de qualquer disciplina da turma DT.
    if dt_classroom_ids:

        return (
            db.query(Assessment)
            .filter(
                or_(
                    Assessment.teacher_id == teacher.id,
                    Assessment.classroom_id.in_(
                        dt_classroom_ids
                    )
                )
            )
        )

    return (
        db.query(Assessment)
        .filter(
            Assessment.teacher_id == teacher.id
        )
    )


def ensure_student_in_teacher_scope(
    db: Session,
    teacher: Teacher,
    student_id: int
):
    student = (
        db.query(User)
        .filter(
            User.id == student_id
        )
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Aluno nÃ£o encontrado."
        )

    tipo = (
        student.tipo
        or ""
    ).strip().lower()

    if tipo != "aluno":
        raise HTTPException(
            status_code=404,
            detail="Aluno nÃ£o encontrado."
        )

    classroom_ids = (
        get_teacher_accessible_classroom_ids(
            db,
            teacher
        )
    )

    if not classroom_ids:
        raise HTTPException(
            status_code=403,
            detail="Professor sem acesso a alunos."
        )

    # NÃ£o exigimos matrÃ­cula ativa aqui,
    # pois anÃ¡lises podem envolver histÃ³rico acadÃªmico.
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == student.id,
            Enrollment.classroom_id.in_(
                classroom_ids
            )
        )
        .first()
    )

    if not enrollment:
        raise HTTPException(
            status_code=403,
            detail=(
                "Este aluno nÃ£o pertence ao "
                "escopo pedagÃ³gico deste professor."
            )
        )

    return student

def get_teacher_classroom_summary(
    db: Session,
    user_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(Teacher.user_id == user_id)
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor nÃ£o encontrado."
        )

    assessments = (
        get_teacher_scope_assessments_query(
        db,
        teacher
    )
    .all()
)

    classrooms = {}

    for assessment in assessments:

        classroom_id = assessment.classroom_id

        if classroom_id not in classrooms:
            classrooms[classroom_id] = {
                "avaliacoes": 0,
                "student_ids": set(),
                "notas": [],
                "percentuais": []
            }

        classrooms[classroom_id]["avaliacoes"] += 1

        questions = (
            db.query(Question)
            .filter(
                Question.assessment_id == assessment.id
            )
            .all()
        )

        if not questions:
            continue

        question_ids = [
            question.id
            for question in questions
        ]

        answers = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.question_id.in_(
                    question_ids
                )
            )
            .all()
        )

        student_ids = {
            answer.user_id
            for answer in answers
        }

        for student_id in student_ids:

            result = get_student_assessment_result(
                db,
                assessment.id,
                student_id
            )

            classrooms[classroom_id][
                "student_ids"
            ].add(student_id)

            classrooms[classroom_id][
                "notas"
            ].append(
                result["nota_final"]
            )

            classrooms[classroom_id][
                "percentuais"
            ].append(
                result["percentual"]
            )

    results = []

    for classroom_id, data in classrooms.items():

        if data["notas"]:

            media = (
                sum(data["notas"])
                / len(data["notas"])
            )

            percentual_medio = (
                sum(data["percentuais"])
                / len(data["percentuais"])
            )

            status = classificar_desempenho(
                percentual_medio
            )

        else:
            media = 0
            percentual_medio = 0
            status = "Sem dados"

        results.append({
            "classroom_id": classroom_id,

            "avaliacoes_criadas":
                data["avaliacoes"],

            "alunos_avaliados":
                len(data["student_ids"]),

            "media_turma":
                round(media, 2),

            "percentual_medio":
                round(percentual_medio, 2),

            "status":
                status
        })

    return results

def get_teacher_students_difficulties(
    db: Session,
    user_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == user_id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor nÃ£o encontrado."
        )

    assessments = (
        get_teacher_scope_assessments_query(
        db,
        teacher
    )
    .all()
)

    students = {}

    for assessment in assessments:

        questions = (
            db.query(Question)
            .filter(
                Question.assessment_id == assessment.id
            )
            .all()
        )

        if not questions:
            continue

        question_ids = [
            question.id
            for question in questions
        ]

        answers = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.question_id.in_(
                    question_ids
                )
            )
            .all()
        )

        student_ids = {
            answer.user_id
            for answer in answers
        }

        for student_id in student_ids:

            result = get_student_assessment_result(
                db,
                assessment.id,
                student_id
            )

            if student_id not in students:
                students[student_id] = {
                    "notas": [],
                    "percentuais": []
                }

            students[student_id][
                "notas"
            ].append(
                result["nota_final"]
            )

            students[student_id][
                "percentuais"
            ].append(
                result["percentual"]
            )

    results = []

    for student_id, data in students.items():

        media = (
            sum(data["notas"])
            / len(data["notas"])
        )

        percentual_medio = (
            sum(data["percentuais"])
            / len(data["percentuais"])
        )

        student = (
            db.query(User)
            .filter(
                User.id == student_id
            )
            .first()
        )

        results.append({
            "student_id": student_id,

            "nome": (
                student.nome
                if student
                else "Aluno"
            ),

            "avaliacoes_realizadas":
                len(data["notas"]),

            "media":
                round(media, 2),

            "percentual_medio":
                round(percentual_medio, 2),

            "status":
                classificar_desempenho(
                    percentual_medio
                )
        })

    # menor percentual primeiro
    results.sort(
        key=lambda item: item[
            "percentual_medio"
        ]
    )

    return results

def get_teacher_students_performance(
    db: Session,
    user_id: int,
    nome: str | None = None,
    status: str | None = None,
    subject_id: int | None = None,
    categoria: str | None = None,
    classroom_id: int | None = None,
    semestre: int | None = None,
    ano_letivo: int | None = None,
    ordem: str = "menor_media"
):
    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == user_id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor nÃ£o encontrado."
        )

    assessments_query = (
    get_teacher_scope_assessments_query(
        db,
        teacher
    )
)


    # filtros da avaliaÃ§Ã£o
    if subject_id is not None:
        assessments_query = assessments_query.filter(
            Assessment.subject_id == subject_id
        )

    if classroom_id is not None:
        assessments_query = assessments_query.filter(
            Assessment.classroom_id == classroom_id
        )

    if semestre is not None:
        assessments_query = assessments_query.filter(
            Assessment.semestre == semestre
        )

    if ano_letivo is not None:
        assessments_query = assessments_query.filter(
            Assessment.ano_letivo == ano_letivo
        )

    assessments = assessments_query.all()

    students = {}

    for assessment in assessments:

        questions_query = (
            db.query(Question)
            .filter(
                Question.assessment_id == assessment.id
            )
        )

        # filtro por conteÃºdo/categoria
        if categoria:
            questions_query = questions_query.filter(
                Question.categoria.ilike(
                    f"%{categoria}%"
                )
            )

        questions = questions_query.all()

        if not questions:
            continue

        question_ids = [
            question.id
            for question in questions
        ]

        answers = (
            db.query(StudentAnswer)
            .filter(
                StudentAnswer.question_id.in_(
                    question_ids
                )
            )
            .all()
        )

        student_ids = {
            answer.user_id
            for answer in answers
        }

        for student_id in student_ids:

            student = (
                db.query(User)
                .filter(
                    User.id == student_id
                )
                .first()
            )

            if not student:
                continue

            # filtro por nome
            if nome:
                if (
                    nome.strip().lower()
                    not in student.nome.lower()
                ):
                    continue

            # calcula desempenho apenas
            # nas questÃµes filtradas
            student_answers = [
                answer
                for answer in answers
                if answer.user_id == student_id
            ]

            total_pontos_possiveis = 0
            total_pontos_obtidos = 0

            respondeu_alguma = False

            for question in questions:

                peso = question.peso or 1.0

                total_pontos_possiveis += peso

                answer = next(
                    (
                        a
                        for a in student_answers
                        if a.question_id == question.id
                    ),
                    None
                )

                if answer:
                    respondeu_alguma = True

                    total_pontos_obtidos += (
                        answer.pontuacao_obtida or 0
                    )

            if not respondeu_alguma:
                continue

            if total_pontos_possiveis > 0:
                percentual = (
                    total_pontos_obtidos
                    / total_pontos_possiveis
                ) * 100
            else:
                percentual = 0

            nota = (
                percentual
                / 100
            ) * (assessment.valor or 10)

            if student_id not in students:
                students[student_id] = {
                    "nome": student.nome,
                    "notas": [],
                    "percentuais": []
                }

            students[student_id][
                "notas"
            ].append(
                nota
            )

            students[student_id][
                "percentuais"
            ].append(
                percentual
            )

    results = []

    for student_id, data in students.items():

        media = (
            sum(data["notas"])
            / len(data["notas"])
        )

        percentual_medio = (
            sum(data["percentuais"])
            / len(data["percentuais"])
        )

        student_status = classificar_desempenho(
            percentual_medio
        )

        # filtro por status
        if status:
            if (
                student_status.lower()
                != status.strip().lower()
            ):
                continue

        results.append({
            "student_id": student_id,

            "nome": data["nome"],

            "avaliacoes_realizadas":
                len(data["notas"]),

            "media":
                round(media, 2),

            "percentual_medio":
                round(percentual_medio, 2),

            "status":
                student_status
        })

    # ordenaÃ§Ã£o
    if ordem == "maior_media":

        results.sort(
            key=lambda item: item["media"],
            reverse=True
        )

    elif ordem == "nome":

        results.sort(
            key=lambda item: item[
                "nome"
            ].lower()
        )

    else:

        # padrÃ£o:
        # menor mÃ©dia primeiro
        results.sort(
            key=lambda item: item["media"]
        )

    return results

def get_student_content_difficulties(
    db: Session,
    teacher_user_id: int,
    student_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(Teacher.user_id == teacher_user_id)
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor nÃ£o encontrado."
        )

    student = ensure_student_in_teacher_scope(
    db=db,
    teacher=teacher,
    student_id=student_id
)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Aluno nÃ£o encontrado."
        )

    assessments = (
    get_teacher_scope_assessments_query(
        db,
        teacher
    )
    .all()
)
    contents = {}

    for assessment in assessments:

        questions = (
            db.query(Question)
            .filter(
                Question.assessment_id == assessment.id
            )
            .all()
        )

        for question in questions:

            # questÃµes sem categoria nÃ£o entram
            if not question.categoria:
                continue

            answer = (
                db.query(StudentAnswer)
                .filter(
                    StudentAnswer.question_id == question.id,
                    StudentAnswer.user_id == student_id
                )
                .order_by(
                    StudentAnswer.id.desc()
                )
                .first()
            )

            if not answer:
                continue

            key = (
                assessment.subject_id,
                question.categoria
            )

            if key not in contents:
                contents[key] = {
                    "percentuais": [],
                    "questoes_respondidas": 0
                }

            contents[key][
                "questoes_respondidas"
            ] += 1

            percentual = (
                answer.percentual_final
                if answer.percentual_final is not None
                else 0
            )

            contents[key][
                "percentuais"
            ].append(
                percentual
            )

    results = []

    for (
        subject_id,
        categoria
    ), data in contents.items():

        percentual_medio = (
            sum(data["percentuais"])
            / len(data["percentuais"])
        )

        results.append({
            "subject_id":
                subject_id,

            "categoria":
                categoria,

            "questoes_respondidas":
                data["questoes_respondidas"],

            "percentual_medio":
                round(percentual_medio, 2),

            "status":
                classificar_desempenho(
                    percentual_medio
                )
        })

    # pior conteÃºdo primeiro
    results.sort(
        key=lambda item:
            item["percentual_medio"]
    )

    return results

def classificar_dificuldade_questao(
    percentual_erro: float
):
    if percentual_erro >= 75:
        return "Muito alta"

    if percentual_erro >= 50:
        return "Alta"

    if percentual_erro >= 25:
        return "MÃ©dia"

    return "Baixa"

def get_teacher_questions_difficulties(
    db: Session,
    teacher_user_id: int,
    subject_id: int | None = None,
    classroom_id: int | None = None,
    categoria: str | None = None,
    student_id: int | None = None,
    semestre: int | None = None,
    ano_letivo: int | None = None
):
    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == teacher_user_id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor nÃ£o encontrado."
        )

    assessments_query = (
    get_teacher_scope_assessments_query(
        db,
        teacher
    )
)
    if student_id is not None:

        ensure_student_in_teacher_scope(
            db=db,
            teacher=teacher,
            student_id=student_id
        )

    if subject_id is not None:
        assessments_query = assessments_query.filter(
            Assessment.subject_id == subject_id
        )

    if classroom_id is not None:
        assessments_query = assessments_query.filter(
            Assessment.classroom_id == classroom_id
        )

    if semestre is not None:
        assessments_query = assessments_query.filter(
            Assessment.semestre == semestre
        )

    if ano_letivo is not None:
        assessments_query = assessments_query.filter(
            Assessment.ano_letivo == ano_letivo
        )

    assessments = assessments_query.all()

    results = []

    for assessment in assessments:

        questions_query = (
            db.query(Question)
            .filter(
                Question.assessment_id == assessment.id
            )
        )

        if categoria:
            questions_query = questions_query.filter(
                Question.categoria.ilike(
                    f"%{categoria}%"
                )
            )

        questions = questions_query.all()

        for question in questions:

            answers_query = (
                db.query(StudentAnswer)
                .filter(
                    StudentAnswer.question_id == question.id
                )
            )

            if student_id is not None:
                answers_query = answers_query.filter(
                    StudentAnswer.user_id == student_id
                )

            answers = answers_query.all()

            if not answers:
                continue

            total_respostas = 0
            respostas_com_erro = 0

            latest_answers = {}

            for answer in answers:
                current = latest_answers.get(
                    answer.user_id
                )

                if (
                    current is None
                    or answer.id > current.id
                ):
                    latest_answers[
                        answer.user_id
                    ] = answer

            for answer in latest_answers.values():

                if answer.percentual_final is None:
                    continue

                total_respostas += 1

                if answer.percentual_final < 50:
                    respostas_com_erro += 1

            if total_respostas == 0:
                continue

            percentual_erro = (
                respostas_com_erro
                / total_respostas
            ) * 100

            results.append({
                "question_id":
                    question.id,

                "categoria":
                    question.categoria,

                "total_respostas":
                    total_respostas,

                "respostas_com_erro":
                    respostas_com_erro,

                "percentual_erro":
                    round(
                        percentual_erro,
                        2
                    ),

                "dificuldade":
                    classificar_dificuldade_questao(
                        percentual_erro
                    )
            })

    results.sort(
        key=lambda item:
            item["percentual_erro"],
        reverse=True
    )

    return results

def get_student_analysis_data(
    db: Session,
    teacher_user_id: int,
    student_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == teacher_user_id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor nÃ£o encontrado."
        )

    student = ensure_student_in_teacher_scope(
        db=db,
        teacher=teacher,
        student_id=student_id
    )
    # -------------------------------------------------
    # ConteÃºdos com dificuldade
    # -------------------------------------------------

    difficulties = get_student_content_difficulties(
        db=db,
        teacher_user_id=teacher_user_id,
        student_id=student_id
    )

    # inicialmente consideramos como dificuldade
    # apenas Baixo e Regular
    critical_contents = [
        item
        for item in difficulties
        if item["status"] in [
            "Baixo",
            "Regular"
        ]
    ]

    # -------------------------------------------------
    # QuestÃµes crÃ­ticas
    # -------------------------------------------------

    questions = get_teacher_questions_difficulties(
        db=db,
        teacher_user_id=teacher_user_id,
        student_id=student_id
    )

    critical_questions = [
        {
            "question_id":
                item["question_id"],

            "categoria":
                item["categoria"],

            "percentual_erro":
                item["percentual_erro"]
        }
        for item in questions
        if item["percentual_erro"] >= 50
    ]

    # -------------------------------------------------
    # Desempenho geral desse aluno
    # -------------------------------------------------

    performance = get_teacher_students_performance(
        db=db,
        user_id=teacher_user_id
    )

    student_performance = next(
        (
            item
            for item in performance
            if item["student_id"]
            == student_id
        ),
        None
    )

    if student_performance:
        media_geral = (
            student_performance["media"]
        )

        percentual_medio = (
            student_performance[
                "percentual_medio"
            ]
        )

        status = (
            student_performance[
                "status"
            ]
        )

    else:
        media_geral = 0
        percentual_medio = 0
        status = "Sem dados"

    return {
        "student_id":
            student_id,

        "nome":
            student.nome,

        "media_geral":
            media_geral,

        "percentual_medio":
            percentual_medio,

        "status":
            status,

        "conteudos_com_dificuldade":
            critical_contents,

        "questoes_criticas":
            critical_questions
    }



def get_teacher_profile(
    db: Session,
    user_id: int
):
    teacher = (
        db.query(Teacher)
        .filter(
            Teacher.user_id == user_id
        )
        .first()
    )

    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Perfil de professor nÃ£o encontrado."
        )

    return teacher


def get_teacher_assessment(
    db: Session,
    assessment_id: int,
    teacher_user_id: int
):
    teacher = get_teacher_profile(
        db=db,
        user_id=teacher_user_id
    )

    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id,
            Assessment.teacher_id == teacher.id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail=(
                "AvaliaÃ§Ã£o nÃ£o encontrada ou "
                "nÃ£o pertence a este professor."
            )
        )

    return assessment

def get_assessments_for_user(
   db: Session,
    current_user: User
):
    tipo = (
        current_user.tipo
        or ""
    ).strip().lower()

    # =====================================================
    # ADMINISTRAÃ‡ÃƒO
    # Pode visualizar todas as avaliaÃ§Ãµes.
    # =====================================================

    if tipo in [
        "administracao",
        "administraÃ§Ã£o"
    ]:
        return (
            db.query(Assessment)
            .order_by(
                Assessment.id.desc()
            )
            .all()
        )

    # =====================================================
    # PROFESSOR
    #
    # Professor comum:
    # vÃª somente as avaliaÃ§Ãµes criadas por ele.
    #
    # DT:
    # tambÃ©m pode CONSULTAR avaliaÃ§Ãµes da turma
    # pela qual Ã© responsÃ¡vel.
    #
    # Isso NÃƒO dÃ¡ permissÃ£o para editar avaliaÃ§Ãµes
    # de outros professores.
    # =====================================================

    if tipo == "professor":

        teacher = (
            db.query(Teacher)
            .filter(
                Teacher.user_id == current_user.id
            )
            .first()
        )

        if not teacher:
            raise HTTPException(
                status_code=404,
                detail="Perfil de professor nÃ£o encontrado."
            )

        dt_classrooms = (
            db.query(Classroom)
            .filter(
                Classroom.teacher_id == teacher.id
            )
            .all()
        )

        dt_classroom_ids = [
            classroom.id
            for classroom in dt_classrooms
        ]

        if dt_classroom_ids:

            return (
                db.query(Assessment)
                .filter(
                    or_(
                        Assessment.teacher_id == teacher.id,
                        Assessment.classroom_id.in_(
                            dt_classroom_ids
                        )
                    )
                )
                .order_by(
                    Assessment.id.desc()
                )
                .all()
            )

        return (
            db.query(Assessment)
            .filter(
                Assessment.teacher_id == teacher.id
            )
            .order_by(
                Assessment.id.desc()
            )
            .all()
        )

    # =====================================================
    # ALUNO
    #
    # Usa a matrÃ­cula ativa como fonte oficial da turma.
    # VÃª somente avaliaÃ§Ãµes ativas da prÃ³pria turma.
    # =====================================================

    if tipo == "aluno":

        enrollment = (
            db.query(Enrollment)
            .filter(
                Enrollment.user_id == current_user.id,
                Enrollment.ativo == True
            )
            .first()
        )

        if not enrollment:
            return []

        return (
            db.query(Assessment)
            .filter(
                Assessment.classroom_id
                == enrollment.classroom_id,

                Assessment.ativa == True
            )
            .order_by(
                Assessment.id.desc()
            )
            .all()
        )

    # =====================================================
    # SUPORTE / OUTROS PERFIS
    # =====================================================

    raise HTTPException(
        status_code=403,
        detail="Perfil sem permissÃ£o para acessar avaliaÃ§Ãµes."
    )

def get_assessment_for_user(
    db: Session,
    assessment_id: int,
    current_user: User
):
    assessments = get_assessments_for_user(
        db=db,
        current_user=current_user
    )

    for assessment in assessments:
        if assessment.id == assessment_id:
            return assessment

    raise HTTPException(
        status_code=404,
        detail="AvaliaÃ§Ã£o nÃ£o encontrada ou sem acesso."
    )   
