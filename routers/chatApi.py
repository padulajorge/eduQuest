from fastapi import Request, APIRouter
import requests
import os
from dotenv import load_dotenv

# Carga variables de entorno desde .env (por ejemplo, la API key)
load_dotenv()
router = APIRouter()

# Obtiene la clave de API y configura el endpoint y modelo a usar
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "gpt-4o"  # Modelo por defecto, puede cambiarse por otro compatible


@router.post("/")
async def generar_preguntas(request: Request):
    """
    Genera preguntas a partir de un texto (contexto) según los parámetros enviados por el usuario.
    Espera un JSON con:
        - contexto: texto base para generar preguntas
        - tipo: "multiple_choice" o "verdadero_falso"
        - cantidad_preguntas: cuántas preguntas generar
        - opciones_por_pregunta: solo si es multiple_choice
    Devuelve un JSON con las preguntas generadas.
    """
    try:
        data = await request.json()
    except Exception as e:
        # Error si el cuerpo no es JSON válido
        return {
            "error": "El cuerpo de la petición no es JSON válido o está vacío.",
            "detalle": str(e),
        }

    # Extrae parámetros del cuerpo, con valores por defecto si faltan
    contexto = data.get("contexto", "")
    tipo = data.get("tipo", "multiple_choice")
    cantidad = data.get("cantidad_preguntas", 5)
    opciones = data.get("opciones_por_pregunta", 4)

    if not contexto:
        return {"error": "Debe incluirse un campo 'contexto' con el texto base."}

    # Construye el prompt para el modelo de lenguaje
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

    # Prepara el payload para la API de OpenRouter
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

    # Llama a la API externa para generar las preguntas
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)

    try:
        result = response.json()
    except Exception as e:
        # Error si la respuesta no es JSON válido
        return {
            "error": "La respuesta no es JSON válido",
            "detalle": str(e),
            "texto_original": response.text,
        }

    # Verifica que la respuesta tenga la estructura esperada
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
