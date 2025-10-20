# routers/quizApi.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union

router = APIRouter()

# ===== Almacén en memoria (MVP) =====
# Estructura del diccionario QUIZZES:
# QUIZZES[quiz_id] = {
#   "difficulty": "medium",
#   "questions": [ {id,type,prompt,choices?} ],
#   "answer_key": { question_id: correct_value }
# }
QUIZZES: Dict[str, Dict[str, Any]] = {}


# ===== Schemas =====
class AnswerItem(BaseModel):
    """
    Representa una respuesta individual a una pregunta de un quiz.
    - question_id: ID de la pregunta.
    - answer: Respuesta dada (str para opción múltiple, bool para verdadero/falso).
    """

    question_id: str
    answer: Union[str, bool]  # str para MCQ (opt1/opt2/..), bool para TF


class SubmitAnswersRequest(BaseModel):
    """
    Modelo para la solicitud de envío de respuestas a un quiz.
    - quiz_id: ID del cuestionario.
    - answers: Lista de respuestas proporcionadas por el usuario.
    """

    quiz_id: str = Field(..., description="ID del cuestionario generado previamente")
    answers: List[AnswerItem]


class FeedbackItem(BaseModel):
    """
    Representa la retroalimentación para una pregunta respondida.
    - question_id: ID de la pregunta.
    - correct: Si la respuesta fue correcta.
    - expected: Respuesta esperada.
    - explanation: Explicación o comentario.
    """

    question_id: str
    correct: bool
    expected: Union[str, bool]
    explanation: str


class SubmitAnswersResponse(BaseModel):
    """
    Respuesta al enviar respuestas de un quiz.
    - quiz_id: ID del cuestionario.
    - total: Número total de preguntas.
    - correct: Número de respuestas correctas.
    - score: Puntaje obtenido (porcentaje).
    - feedback: Lista de retroalimentación por pregunta.
    """

    quiz_id: str
    total: int
    correct: int
    score: float
    feedback: List[FeedbackItem]


def _evaluate(
    questions: List[Dict[str, Any]],
    answer_key: Dict[str, Any],
    user_map: Dict[str, Any],
):
    """
    Evalúa las respuestas del usuario comparándolas con las correctas.
    Retorna el total de preguntas, número de aciertos, puntaje y feedback detallado.
    """
    feedback = []
    ok = 0
    total = len(questions)
    for q in questions:
        qid = q["id"]
        expected = answer_key.get(qid)
        user = user_map.get(qid)
        if q["type"] == "mcq":
            is_ok = user == expected
            expl = (
                "Respuesta correcta."
                if is_ok
                else "La opción correcta es la marcada en la solución."
            )
        else:
            is_ok = bool(user) == bool(expected)
            expl = (
                "Afirmación correctamente evaluada."
                if is_ok
                else "Revisa el enunciado."
            )
        ok += int(is_ok)
        feedback.append(
            FeedbackItem(
                question_id=qid, correct=is_ok, expected=expected, explanation=expl
            )
        )
    score = round(100.0 * ok / max(1, total), 2)
    return total, ok, score, feedback


@router.post("/quiz/answer", response_model=SubmitAnswersResponse)
def answer_quiz(payload: SubmitAnswersRequest):
    """
    Endpoint para enviar respuestas a un quiz y obtener la evaluación.
    - payload: Solicitud con el ID del quiz y las respuestas.
    Retorna el puntaje y feedback detallado.
    """
    data = QUIZZES.get(payload.quiz_id)
    if not data:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")
    user_map = {a.question_id: a.answer for a in payload.answers}
    total, ok, score, fb = _evaluate(data["questions"], data["answer_key"], user_map)
    return SubmitAnswersResponse(
        quiz_id=payload.quiz_id, total=total, correct=ok, score=score, feedback=fb
    )


# Endpoint adicional para obtener el quiz sin respuestas (público)
class QuizPublicResponse(BaseModel):
    """
    Respuesta pública para obtener los datos de un quiz (sin respuestas).
    - quiz_id: ID del cuestionario.
    - difficulty: Dificultad del quiz.
    - questions: Lista de preguntas (sin respuestas correctas).
    """

    quiz_id: str
    difficulty: str
    questions: list  # sin respuestas


@router.get("/quiz/{quiz_id}", response_model=QuizPublicResponse)
def get_quiz_public(quiz_id: str):
    """
    Endpoint para obtener los datos públicos de un quiz (sin respuestas correctas).
    - quiz_id: ID del cuestionario.
    """
    data = QUIZZES.get(quiz_id)
    if not data:
        raise HTTPException(status_code=404, detail="Quiz no encontrado")
    return QuizPublicResponse(
        quiz_id=quiz_id,
        difficulty=data["difficulty"],
        questions=data["questions"],  # acá no viene answer_key
    )
