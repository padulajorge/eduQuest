# routers/documentsApi.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document as DocxDocument
import io, re
import random
import traceback
import uuid


# Rutas para manejo de documentos: subir y extraer texto de PDF y DOCX
router = APIRouter()

ALLOWED_EXTS = {".pdf", ".docx"}
MAX_FILE_MB = 10  # límite razonable para MVP


def _ext_ok(filename: str) -> bool:
    fn = filename.lower()
    return any(fn.endswith(ext) for ext in ALLOWED_EXTS)


def _clean_text(text: str) -> str:
    # Normaliza: colapsa múltiples espacios/saltos y recorta
    text = text.replace("\r", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    return text.strip()


def _extract_pdf(file_bytes: bytes) -> Dict[str, Any]:
    try:
        with io.BytesIO(file_bytes) as buf:
            reader = PdfReader(buf)
            # Algunos PDFs vienen cifrados pero permiten decrypt("")
            if getattr(reader, "is_encrypted", False):
                try:
                    reader.decrypt("")  # best-effort
                except Exception:
                    pass

            pages = len(reader.pages)
            chunks = []
            for i in range(pages):
                try:
                    page = reader.pages[i]
                    t = page.extract_text() or ""
                except Exception:
                    t = ""
                chunks.append(t)
            raw = "\n".join(chunks)
            return {"pages": pages, "text_raw": raw}
    except Exception as e:
        # Reenvía como error controlado
        raise HTTPException(
            status_code=400, detail=f"Error leyendo PDF: {type(e).__name__}: {e}"
        )


def _extract_docx(file_bytes: bytes) -> Dict[str, Any]:
    with io.BytesIO(file_bytes) as buf:
        doc = DocxDocument(buf)
        paras = [p.text for p in doc.paragraphs if p.text]
        raw = "\n".join(paras)
        return {
            "paragraphs": len(paras),
            "text_raw": raw,
        }


class ExtractResponse(BaseModel):
    filename: str
    kind: str
    size_bytes: int
    meta: Dict[str, Any]
    text: str
    word_count: int


@router.post("/docs/extract", response_model=ExtractResponse)
async def extract_text(file: UploadFile = File(...)):
    # Validaciones básicas
    if not _ext_ok(file.filename):
        raise HTTPException(status_code=400, detail="Solo se aceptan .pdf y .docx")
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_MB:
        raise HTTPException(status_code=413, detail=f"Archivo excede {MAX_FILE_MB} MB")

    # Extrae según tipo
    if file.filename.lower().endswith(".pdf"):
        meta = _extract_pdf(content)
        kind = "pdf"
    else:
        meta = _extract_docx(content)
        kind = "docx"

    cleaned = _clean_text(meta.get("text_raw", ""))
    words = len(cleaned.split()) if cleaned else 0

    return ExtractResponse(
        filename=file.filename,
        kind=kind,
        size_bytes=len(content),
        meta={k: v for k, v in meta.items() if k != "text_raw"},
        text=cleaned,
        word_count=words,
    )


# Versión batch (opcional): múltiples archivos a la vez
class BatchItem(BaseModel):
    filename: str
    kind: str
    size_bytes: int
    word_count: int


class BatchResponse(BaseModel):
    items: List[BatchItem]
    total_files: int
    total_words: int


@router.post("/docs/extract-batch", response_model=BatchResponse)
async def extract_text_batch(files: List[UploadFile] = File(...)):
    items: List[BatchItem] = []
    total_words = 0

    for file in files:
        if not _ext_ok(file.filename):
            raise HTTPException(
                status_code=400, detail=f"Archivo no permitido: {file.filename}"
            )
        content = await file.read()
        size_mb = len(content) / (1024 * 1024)
        if size_mb > MAX_FILE_MB:
            raise HTTPException(
                status_code=413, detail=f"{file.filename} excede {MAX_FILE_MB} MB"
            )

        if file.filename.lower().endswith(".pdf"):
            meta = _extract_pdf(content)
            kind = "pdf"
        else:
            meta = _extract_docx(content)
            kind = "docx"

        cleaned = _clean_text(meta.get("text_raw", ""))
        words = len(cleaned.split()) if cleaned else 0
        total_words += words

        items.append(
            BatchItem(
                filename=file.filename,
                kind=kind,
                size_bytes=len(content),
                word_count=words,
            )
        )

    return BatchResponse(items=items, total_files=len(items), total_words=total_words)

    # Ruta para generar el quiz en una misma llamada


Difficulty = Literal["easy", "medium", "hard"]

# ====== Helper simple para generar preguntas (MVP rule-based) ======
SPANISH_STOPWORDS = {
    "el",
    "la",
    "los",
    "las",
    "un",
    "una",
    "unos",
    "unas",
    "de",
    "del",
    "al",
    "y",
    "o",
    "u",
    "en",
    "con",
    "por",
    "para",
    "como",
    "que",
    "se",
    "su",
    "sus",
    "a",
    "es",
    "son",
    "ser",
    "fue",
    "fueron",
    "más",
    "menos",
    "muy",
    "ya",
    "no",
    "sí",
    "si",
    "pero",
    "porque",
    "cuando",
    "donde",
    "lo",
    "le",
    "les",
    "mi",
    "mis",
    "tu",
    "tus",
    "nuestro",
    "nuestra",
    "esto",
    "esta",
    "este",
    "estos",
    "estas",
    "eso",
    "esa",
    "ese",
    "esos",
    "esas",
}


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?¡¿])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _tokens(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{3,}", text)


def _keywords(text: str) -> List[str]:
    toks = _tokens(text)
    toks = [t for t in toks if t.lower() not in SPANISH_STOPWORDS and len(t) >= 5]
    seen, out = set(), []
    for t in toks:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out


def _make_mcq(
    sentence: str, pool_words: List[str], rnd: random.Random, difficulty: Difficulty
):
    words = _keywords(sentence) or pool_words or ["concepto"]
    target = rnd.choice(words)
    blanked = re.sub(
        rf"\b{re.escape(target)}\b", "_____", sentence, flags=re.IGNORECASE, count=1
    )
    prompt = f"Complete la palabra que falta en la oración: {blanked}"

    sim_candidates = [
        w
        for w in pool_words
        if w.lower() != target.lower() and abs(len(w) - len(target)) <= 2
    ]
    rnd.shuffle(sim_candidates)
    distractors = {"easy": 2, "medium": 3, "hard": 4}[difficulty]
    distractors = sim_candidates[:distractors]
    base_pool = [w for w in pool_words if w.lower() != target.lower()]
    while len(distractors) < 3 and base_pool:
        distractors.append(base_pool.pop())
    options = [target] + distractors[:3]
    rnd.shuffle(options)
    choices = [{"id": f"opt{i+1}", "text": opt} for i, opt in enumerate(options)]
    answer_id = next(c["id"] for c in choices if c["text"] == target)
    return prompt, choices, answer_id


def _make_tf(sentence: str, rnd: random.Random):
    is_true = rnd.random() < 0.5
    s = sentence
    if not is_true:
        if re.search(r"\d+", s):
            s = re.sub(r"(\d+)", lambda m: str(int(m.group(1)) + 1), s, count=1)
        else:
            s = re.sub(
                r"\b(es|son|era|fue)\b", "no es", s, flags=re.IGNORECASE, count=1
            )
    prompt = f"Verdadero o Falso: {s}"
    return prompt, is_true


def _generate_questions(
    text: str, difficulty: Difficulty, num_mcq: int, num_tf: int, seed: Optional[int]
):
    rnd = random.Random(seed)
    sentences = _split_sentences(text)
    if not sentences:
        raise HTTPException(
            status_code=400, detail="No se detectaron oraciones en el documento."
        )
    pool = _keywords(text)
    if len(pool) < 10:
        pool = list(dict.fromkeys(_tokens(text)))  # fallback
    rnd.shuffle(sentences)

    questions = []
    answer_key = {}

    # MCQ
    count = 0
    for s in sentences:
        if count >= num_mcq:
            break
        prompt, choices, correct = _make_mcq(s, pool, rnd, difficulty)
        qid = f"mcq-{uuid.uuid4().hex[:8]}"
        questions.append(
            {"id": qid, "type": "mcq", "prompt": prompt, "choices": choices}
        )
        answer_key[qid] = correct
        count += 1

    # TF
    count = 0
    for s in sentences:
        if count >= num_tf:
            break
        prompt, truth = _make_tf(s, rnd)
        qid = f"tf-{uuid.uuid4().hex[:8]}"
        questions.append({"id": qid, "type": "tf", "prompt": prompt})
        answer_key[qid] = truth
        count += 1

    return questions, answer_key


# ====== Schema de respuesta ======
class GenerateFromDocResponse(BaseModel):
    quiz_id: str
    difficulty: Difficulty
    questions: List[dict]
    # Devolvemos la clave de respuestas para debug. En producción, ocultarla.
    answer_key: dict


# ====== Endpoint principal: subir doc y recibir quiz ======
@router.post("/docs/generate-quiz", response_model=GenerateFromDocResponse)
async def generate_quiz_from_doc(
    file: UploadFile = File(...),
    difficulty: Difficulty = "medium",
    num_mcq: int = 5,
    num_tf: int = 5,
    seed: Optional[int] = None,
):
    # 1) Validaciones/extensión/tamaño
    if not _ext_ok(file.filename):
        raise HTTPException(status_code=400, detail="Solo se aceptan .pdf y .docx")
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_MB:
        raise HTTPException(status_code=413, detail=f"Archivo excede {MAX_FILE_MB} MB")

    # 2) Extraer texto
    if file.filename.lower().endswith(".pdf"):
        meta = _extract_pdf(content)
    else:
        meta = _extract_docx(content)
    cleaned = _clean_text(meta.get("text_raw", ""))

    if len(cleaned) < 30:
        raise HTTPException(
            status_code=400,
            detail="El texto extraído es demasiado corto para generar preguntas.",
        )

    # 3) Generar preguntas
    questions, answer_key = _generate_questions(
        cleaned, difficulty, num_mcq, num_tf, seed
    )

    # 4) Responder
    return GenerateFromDocResponse(
        quiz_id=str(uuid.uuid4()),
        difficulty=difficulty,
        questions=questions,  # 🔒 No incluye soluciones dentro de cada pregunta
    )

    # 5) Guardar en memoria (MVP)
    quiz_id = str(uuid.uuid4())
    from routers.quizApi import QUIZZES  # import local para evitar ciclo de import

    QUIZZES[quiz_id] = {
        "difficulty": difficulty,
        "questions": questions,
        "answer_key": answer_key,
    }

    # 6) Responder (si querés, quita answer_key en prod)
    return GenerateFromDocResponse(
        quiz_id=quiz_id,
        difficulty=difficulty,
        questions=questions,
    )
