from fastapi import Request, APIRouter
import requests
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "gpt-4o"  # o cualquier modelo compatible con JSON (ej: openai/gpt-4-turbo)


@router.post("/")
async def generar_preguntas(request: Request):
    """
    Genera preguntas a partir de un texto (contexto) según los parámetros enviados por el usuario:
    {
        "contexto": "texto sobre fauna/flora...",
        "tipo": "multiple_choice" o "verdadero_falso",
        "cantidad_preguntas": 5,
        "opciones_por_pregunta": 4 (solo si es multiple_choice)
    }
    """
    try:
        data = await request.json()
    except Exception as e:
        return {
            "error": "El cuerpo de la petición no es JSON válido o está vacío.",
            "detalle": str(e),
        }

    # Extrae los parámetros enviados por el usuario en el cuerpo JSON de la petición.
    # Si algún parámetro no está presente, se asigna un valor por defecto:
    # - contexto: texto base para generar preguntas (por defecto, cadena vacía)
    # - tipo: tipo de preguntas ("multiple_choice" por defecto)
    # - cantidad: número de preguntas a generar (por defecto, 5)
    # - opciones: número de opciones por pregunta (por defecto, 4)
    contexto = data.get("contexto", "")
    tipo = data.get("tipo", "multiple_choice")
    cantidad = data.get("cantidad_preguntas", 5)
    opciones = data.get("opciones_por_pregunta", 4)

    if not contexto:
        return {"error": "Debe incluirse un campo 'contexto' con el texto base."}

    # Construcción dinámica del prompt
    prompt = f"""
        Usando el siguiente texto de contexto:
        \"\"\"{contexto}\"\"\"

        Genera {cantidad} preguntas del tipo {tipo}.
        {"Cada pregunta debe tener " + str(opciones) + " opciones posibles si es multiple choice." if tipo == "multiple_choice" else ""}
        La respuesta correcta debe estar indicada.

        El resultado DEBE estar en formato JSON ESTRICTO con esta estructura:

        {{
        "preguntas": [
            {{
            "tipo": "multiple_choice" | "verdadero_falso",
            "pregunta": "texto de la pregunta",
            "opciones": ["A", "B", "C", "D"], // solo si aplica
            "respuesta_correcta": "texto u opción correcta"
            }}
        ]
        }}
        """

    payload = {
        "model": MODEL,
        "response_format": {"type": "json_object"},  # Fuerza formato JSON válido
        "messages": [
            {
                "role": "system",
                "content": "Sos un generador de preguntas en formato JSON estricto.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)

    try:
        result = response.json()
    except Exception as e:
        return {
            "error": "La respuesta no es JSON válido",
            "detalle": str(e),
            "texto_original": response.text,
        }

    # Verificación de estructura esperada
    if "choices" not in result or not result["choices"]:
        return {"error": "Respuesta inesperada de la API", "respuesta": result}

    try:
        contenido = result["choices"][0]["message"]["content"]
        # Si el modelo devolvió un string JSON, lo parseamos para enviar objeto al frontend
        import json

        return json.loads(contenido)
    except Exception as e:
        # Si no es un JSON válido, devolvemos el texto para debug
        return {
            "error": "El modelo no devolvió JSON válido",
            "detalle": str(e),
            "contenido": result["choices"][0]["message"]["content"],
        }
