from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# =========================================================
# CONFIGURACAO DE ACESSO
# =========================================================

class AssessmentAccessUpdate(BaseModel):

    data_abertura: Optional[datetime] = None

    data_encerramento: Optional[datetime] = None

    liberar_resultado: Optional[bool] = None

    liberar_prova: Optional[bool] = None

    liberar_gabarito: Optional[bool] = None


# =========================================================
# RESPOSTA DE CONFIGURACAO
# =========================================================

class AssessmentAccessResponse(BaseModel):

    assessment_id: int

    data_abertura: Optional[datetime] = None

    data_encerramento: Optional[datetime] = None

    liberar_resultado: bool

    liberar_prova: bool

    liberar_gabarito: bool

    status: str


# =========================================================
# DISPONIBILIDADE PARA ALUNO
# =========================================================

class AssessmentAvailabilityResponse(BaseModel):

    assessment_id: int

    status: str

    pode_responder: bool

    data_abertura: Optional[datetime] = None

    data_encerramento: Optional[datetime] = None

    resultado_liberado: bool

    prova_liberada: bool

    gabarito_liberado: bool


# =========================================================
# PROVA RESPONDIDA
# =========================================================

class AssessmentSubmissionItem(BaseModel):

    question_id: int

    enunciado: str

    resposta: Optional[str] = None


# =========================================================
# GABARITO
# =========================================================

class AssessmentAnswerKeyItem(BaseModel):

    question_id: int

    enunciado: str

    resposta_correta: Optional[str] = None

    explicacao: Optional[str] = None