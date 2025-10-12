from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Form
import os, io, re, json, requests
from dotenv import load_dotenv
from typing import Optional
from pypdf import PdfReader
from docx import Document as DocxDocument
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image

load_dotenv()
router = APIRouter()

# ======================
#     CONFIGURACIÓN
# ======================
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_DEFAULT = "gpt-4o"
MAX_FILE_MB = 10

# ======================
#  FUNCIONES AUXILIARES
# ======================


def _clean_text(text: str) -> str:
    text = text.replace("\r", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    return text.strip()


def _extract_pdf_text(file_bytes: bytes) -> str:
    try:
        with io.BytesIO(file_bytes) as buf:
            reader = PdfReader(buf)
            if getattr(reader, "is_encrypted", False):
                try:
                    reader.decrypt("")
                except Exception:
                    pass
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return _clean_text(text)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error leyendo PDF: {type(e).__name__}: {e}"
        )


def _extract_docx_text(file_bytes: bytes) -> str:
    try:
        with io.BytesIO(file_bytes) as buf:
            doc = DocxDocument(buf)
        return _clean_text("\n".join(p.text for p in doc.paragraphs))
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error leyendo DOCX: {type(e).__name__}: {e}"
        )


def _ocr_pdf_bytes(file_bytes: bytes, lang="spa+eng") -> str:
    # 🔹 Configurá tu ruta a Tesseract si no está en PATH
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    try:
        images = convert_from_bytes(file_bytes, dpi=200)
        text = "\n".join(pytesseract.image_to_string(img, lang=lang) for img in images)
        return _clean_text(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR falló: {e}")


def _build_prompt(contexto: str, tipo: str, cantidad: int, opciones: int) -> str:
    return f"""
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
      "opciones": ["A","B","C","D"],  // solo si aplica
      "respuesta_correcta": "texto u opción correcta"
    }}
  ]
}}
""".strip()


def _call_openrouter(prompt: str, model: str):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY no configurada")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": "Sos un generador de preguntas en formato JSON estricto.",
            },
            {"role": "user", "content": prompt},
        ],
    }
    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    try:
        result = resp.json()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Respuesta no válida de la API: {e}"
        )
    if "choices" not in result or not result["choices"]:
        raise HTTPException(status_code=500, detail=f"Respuesta vacía: {result}")
    try:
        contenido = result["choices"][0]["message"]["content"]
        return json.loads(contenido)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parseando JSON: {e}")


# ======================
#     ENDPOINT FINAL
# ======================


@router.post(
    "/generar-preguntas",
    summary="Genera preguntas desde texto, PDF o DOCX (con OCR opcional)",
)
async def generar_preguntas(
    contexto: Optional[str] = Form(None),
    tipo: str = Form("multiple_choice"),
    cantidad_preguntas: int = Form(5),
    opciones_por_pregunta: int = Form(4),
    modelo: str = Form(MODEL_DEFAULT),
    file: Optional[UploadFile] = File(None),
    force_ocr: bool = Form(False),
    ocr_lang: str = Form("spa+eng"),
):
    """
    Permite generar preguntas:
    - a partir de texto (`contexto`)
    - o subiendo un documento PDF/DOCX (usa OCR si se requiere)
    """
    texto_final = ""

    # 1️⃣ Si sube un archivo
    if file:
        name = (file.filename or "").lower()
        content = await file.read()
        if len(content) > MAX_FILE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413, detail=f"El archivo excede {MAX_FILE_MB} MB"
            )

        if name.endswith(".pdf"):
            texto_final = _extract_pdf_text(content)
            if force_ocr or len(texto_final) < 50:
                texto_final = _ocr_pdf_bytes(content, lang=ocr_lang)
        elif name.endswith(".docx"):
            texto_final = _extract_docx_text(content)
        else:
            raise HTTPException(status_code=400, detail="Solo se aceptan .pdf o .docx")

    # 2️⃣ Si envía texto plano
    elif contexto:
        texto_final = contexto

    # 3️⃣ Validación
    if not texto_final or len(texto_final) < 30:
        raise HTTPException(
            status_code=400,
            detail="Texto insuficiente o archivo sin contenido legible.",
        )

    # 4️⃣ Crear prompt y llamar al modelo
    prompt = _build_prompt(texto_final, tipo, cantidad_preguntas, opciones_por_pregunta)
    return _call_openrouter(prompt, modelo)
