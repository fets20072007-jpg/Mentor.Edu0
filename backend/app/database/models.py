from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Float
)
from app.database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, unique=True, index=True)
    senha = Column(String)

    tipo = Column(String)

    bio = Column(String, nullable=True)
    escola = Column(String, nullable=True)
    serie = Column(String, nullable=True)
    idade = Column(Integer, nullable=True)

    objetivo = Column(String, nullable=True)
    materias_favoritas = Column(String, nullable=True)
    dificuldades = Column(String, nullable=True)
    horas_estudo = Column(Integer, nullable=True)
        
    enrollments = relationship(
        "Enrollment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    answers = relationship(
        "StudentAnswer",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    histories = relationship(
        "LearningHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    meta = Column(String)
    horas_dia = Column(Integer)
    materias = Column(String)
    dificuldade = Column(String)
    status = Column(String, default="ativo")

    user_id = Column(Integer, ForeignKey("users.id"))


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    materia = Column(String, nullable=False)
    assunto = Column(String, nullable=False)
    duracao_minutos = Column(Integer, nullable=False)
    dificuldade_sentida = Column(Integer, nullable=True)
    concluida = Column(Boolean, default=False)
    data_sessao = Column(String, nullable=True)
    observacoes = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

class LibraryBook(Base):
    __tablename__ = "library_books"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String, nullable=False)

    autor = Column(String, nullable=False)

    disciplina = Column(String, nullable=False)

    serie = Column(String, nullable=True)

    descricao = Column(String, nullable=True)

    arquivo_pdf = Column(String, nullable=True)

    ativo = Column(Boolean, default=True)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String, nullable=False)

    disciplina = Column(String, nullable=False)

    autor = Column(String, nullable=False)

    editora = Column(String, nullable=True)

    ano = Column(Integer, nullable=True)

    quantidade_capitulos = Column(Integer, default=0)

    pdf_url = Column(String, nullable=True)

    descricao = Column(String, nullable=True)

    chapters = relationship(
        "Chapter",
        back_populates="book",
        cascade="all, delete-orphan"
    )

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String, nullable=False)

    numero = Column(Integer, nullable=False)

    pagina_inicio = Column(Integer)

    pagina_fim = Column(Integer)

    descricao = Column(String)

    book_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=False
    )

    book = relationship(
        "Book",
        back_populates="chapters"
    )

    questions = relationship(
        "Question",
        back_populates="chapter",
        cascade="all, delete-orphan"
    )

    videos = relationship(
        "Video",
        back_populates="chapter",
        cascade="all, delete-orphan"
    )

    pdfs = relationship(
        "PDFMaterial",
        back_populates="chapter",
        cascade="all, delete-orphan"
    )

    examples = relationship(
        "PracticalExample",
        back_populates="chapter",
        cascade="all, delete-orphan"
    )
    

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)

    pergunta = Column(String, nullable=False)

    alternativa_a = Column(String)

    alternativa_b = Column(String)

    alternativa_c = Column(String)

    alternativa_d = Column(String)

    resposta_correta = Column(String)

    explicacao = Column(String)

    dificuldade = Column(String, default="Média")

    chapter_id = Column(
        Integer,
        ForeignKey("chapters.id"),
        nullable=False
    )

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String, nullable=False)

    descricao = Column(String, nullable=True)

    url = Column(String, nullable=False)

    duracao = Column(String, nullable=True)

    plataforma = Column(String, default="YouTube")

    chapter_id = Column(
        Integer,
        ForeignKey("chapters.id"),
        nullable=False
    )

    chapter = relationship(
        "Chapter",
        back_populates="videos"
    )

    
class PDFMaterial(Base):
    __tablename__ = "pdf_materials"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String, nullable=False)

    descricao = Column(String, nullable=True)

    arquivo = Column(String, nullable=False)

    paginas = Column(Integer, nullable=True)

    chapter_id = Column(
        Integer,
        ForeignKey("chapters.id"),
        nullable=False
    )

    chapter = relationship(
        "Chapter",
        back_populates="pdfs"
    )

   

class PracticalExample(Base):
    __tablename__ = "practical_examples"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String, nullable=False)

    contexto = Column(String, nullable=False)

    explicacao = Column(String, nullable=False)

    curso_relacionado = Column(String, nullable=True)

    chapter_id = Column(
        Integer,
        ForeignKey("chapters.id"),
        nullable=False
    )


    chapter = relationship(
        "Chapter",
        back_populates="examples"
    )

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    tipo = Column(String, default="Objetiva")

    enunciado = Column(String, nullable=False)

    alternativa_a = Column(String, nullable=True)
    alternativa_b = Column(String, nullable=True)
    alternativa_c = Column(String, nullable=True)
    alternativa_d = Column(String, nullable=True)

    resposta_correta = Column(String, nullable=True)

    explicacao = Column(String)

    dificuldade = Column(String, default="Médio")

    peso = Column(Float, default=1.0)

    categoria = Column(String, nullable=True)

    criterio_0 = Column(String, nullable=True)
    criterio_25 = Column(String, nullable=True)
    criterio_50 = Column(String, nullable=True)
    criterio_75 = Column(String, nullable=True)
    criterio_100 = Column(String, nullable=True)

    chapter_id = Column(
        Integer,
        ForeignKey("chapters.id"),
        nullable=True
    )

    assessment_id = Column(
        Integer,
        ForeignKey("assessments.id"),
        nullable=True
    )

    chapter = relationship(
        "Chapter",
        back_populates="questions"
    )

    assessment = relationship(
        "Assessment",
        back_populates="questions"
    )

    answers = relationship(
        "StudentAnswer",
        back_populates="question",
        cascade="all, delete-orphan"
    )

class LearningHistory(Base):
    __tablename__ = "learning_history"

    id = Column(Integer, primary_key=True, index=True)

    materia = Column(String, nullable=False)

    percentual = Column(Integer)

    tempo_medio = Column(Integer)

    observacao = Column(String)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="histories"
    )

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    user = relationship("User")

    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    telefone = Column(String)
    especialidade = Column(String, nullable=False)
    carga_horaria = Column(Integer, default=40)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    subjects = relationship(
        "Subject",
        back_populates="teacher",
        cascade="all, delete-orphan"
    )

    assessments = relationship(
        "Assessment",
        back_populates="teacher"
    )

    classrooms = relationship(
    "Classroom",
    back_populates="teacher"
    )
    
    attendances = relationship(
    "Attendance",
    back_populates="teacher"
    )
    user = relationship("User")
   

   

class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String, nullable=False)

    serie = Column(String, nullable=False)

    turno = Column(String, nullable=False)

    sala = Column(String, nullable=False)

    ano = Column(Integer, nullable=False)

    capacidade = Column(Integer, default=40)

    ativa = Column(Boolean, default=True)

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id")
    )

    teacher = relationship(
        "Teacher",
        back_populates="classrooms"
    )

    subjects = relationship(
        "Subject",
        back_populates="classroom",
        cascade="all, delete-orphan"
    )
    
    assessments = relationship(
        "Assessment",
        back_populates="classroom"
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="classroom",
        cascade="all, delete-orphan"
    )

    attendances = relationship(
    "Attendance",
    back_populates="classroom",
    cascade="all, delete-orphan"
    )

    

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String, nullable=False)

    carga_horaria = Column(Integer, default=80)

    descricao = Column(String)

    ativa = Column(Boolean, default=True)

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=False
    )

    classroom_id = Column(
        Integer,
        ForeignKey("classrooms.id"),
        nullable=False
    )

    assessments = relationship(
        "Assessment",
        back_populates="subject"
    )

    teacher = relationship(
        "Teacher",
        back_populates="subjects"
    )

    attendances = relationship(
    "Attendance",
    back_populates="subject",
    cascade="all, delete-orphan"
    )

    classroom = relationship(
        "Classroom",
        back_populates="subjects"

    )
class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)

    data_matricula = Column(
        DateTime,
        default=datetime.utcnow
    )

    ativo = Column(
        Boolean,
        default=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    classroom_id = Column(
        Integer,
        ForeignKey("classrooms.id"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="enrollments"
    )

    classroom = relationship(
        "Classroom",
        back_populates="enrollments"
    )

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    data = Column(DateTime, default=datetime.utcnow)

    status = Column(String, nullable=False)
    # Presente | Falta | Atraso

    justificada = Column(Boolean, default=False)

    motivo = Column(String, nullable=True)

    arquivo = Column(String, nullable=True)

    observacao = Column(String, nullable=True)

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    classroom_id = Column(
        Integer,
        ForeignKey("classrooms.id"),
        nullable=False
    )

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    teacher = relationship(
        "Teacher",
        back_populates="attendances"
    )

    student = relationship(
        "User"
    )

    classroom = relationship(
        "Classroom",
        back_populates="attendances"
    )

    subject = relationship(
        "Subject",
        back_populates="attendances"
    )

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)

    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    tipo = Column(String, nullable=False)

    data = Column(DateTime)

    valor = Column(Float, default=10)

    ativa = Column(Boolean, default=True)

    semestre = Column(Integer, nullable=True)
    ano_letivo = Column(Integer, nullable=True)

    teacher_id = Column(
        Integer,
        ForeignKey("teachers.id"),
        nullable=False
    )

    classroom_id = Column(
        Integer,
        ForeignKey("classrooms.id"),
        nullable=False
    )

    subject_id = Column(
        Integer,
        ForeignKey("subjects.id"),
        nullable=False
    )

    teacher = relationship(
        "Teacher",
        back_populates="assessments"
    )

    classroom = relationship(
        "Classroom",
        back_populates="assessments"
    )

    subject = relationship(
        "Subject",
        back_populates="assessments"
    )

    grades = relationship(
        "Grade",
        back_populates="assessment"
    )

    questions = relationship(
        "Question",
        back_populates="assessment",
        cascade="all, delete-orphan"
    )

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)

    nota = Column(Float, nullable=False)

    observacao = Column(String, nullable=True)

    assessment_id = Column(
        Integer,
        ForeignKey("assessments.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    assessment = relationship(
        "Assessment",
        back_populates="grades"
    )

    student = relationship("User")

class StudentAnswer(Base):
    __tablename__ = "student_answers"

    id = Column(Integer, primary_key=True, index=True)

    resposta = Column(String, nullable=False)

    tempo_resposta = Column(Integer)

    percentual_ia = Column(Float, nullable=True)

    justificativa_ia = Column(String, nullable=True)

    percentual_professor = Column(Float, nullable=True)

    percentual_final = Column(Float, nullable=True)

    pontuacao_obtida = Column(Float, nullable=True)

    corrigida_ia = Column(Boolean, default=False)

    revisada_professor = Column(Boolean, default=False)

    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    question = relationship(
        "Question",
        back_populates="answers"
    )

    user = relationship(
        "User",
        back_populates="answers"
    )