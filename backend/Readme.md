# eduQuest

API construida con FastAPI para gestionar interacciones de chat.

## Requisitos

- Python 3.8 o superior
- [pip](https://pip.pypa.io/en/stable/)

## Instalación

1. Clona el repositorio:
   ```sh
   git clone https://github.com/padulajorge/eduQuest.git
   cd eduQuest
   ```

2. Crea y activa un entorno virtual:
   ```sh
   python -m venv venv
   venv\Scripts\activate   # En Windows
   ```

3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
   ```
   OPENROUTER_API_KEY=tu-api-key
   ```

## Uso

Para iniciar el servidor en modo desarrollo:

```sh
uvicorn main:app --reload
```

La API estará disponible en [http://localhost:8000](http://localhost:8000).

## Endpoints principales

- `/chat/*` — Endpoints relacionados con el chat (ver detalles en `routers/chatApi.py`).

## Notas

- Asegúrate de no compartir tu archivo `.env` ni tu API key.
- Puedes modificar la configuración de rutas en `main.py`.

## Licencia


Endpoint que acepta texto, PDF o DOCX y genera preguntas tipo multiple choice y verdadero/falso.
Para PDFs escaneados (imágenes), soporta OCR con Tesseract.

Parámetros (form-data)

| Campo                   | Tipo     | Requerido | Default           | Descripción                                                                                   |
| ----------------------- | -------- | --------- | ----------------- | --------------------------------------------------------------------------------------------- |
| `contexto`              | `string` | No*       | —                 | Texto base del que generar preguntas. Se usa si **no** 
se envía `file`.                     |
| `file`                  | `file`   | No*       | —                 | Documento `.pdf` o `.docx`. Si se sube archivo, tiene prioridad sobre `contexto`. Máx. 10 MB. |
| `tipo`                  | `string` | No        | `multiple_choice` | `"multiple_choice"` o `"verdadero_falso"`.                                                    |
| `cantidad_preguntas`    | `int`    | No        | `5`               | Cantidad de preguntas a generar.                                                              |
| `opciones_por_pregunta` | `int`    | No        | `4`               | Solo aplica a `multiple_choice`.                                                              |
| `modelo`                | `string` | No        | `gpt-4o`          | Modelo de OpenRouter a usar.                                                                  |
| `force_ocr`             | `bool`   | No        | `false`           | Si es `true`, **fuerza OCR** en PDFs (ver explicación abajo).                                 |
| `ocr_lang`              | `string` | No        | `spa+eng`         | Idiomas del OCR (Tesseract). Se pueden combinar con `+` (ej. `spa`, `eng`, `spa+eng`).        |

Dependencias (requirements)

fastapi
uvicorn
python-dotenv
requests
python-multipart
pypdf
python-docx
pdf2image
pytesseract
pillow

Uso en Swagger

Levantar: uvicorn main:app --reload

Ir a: http://127.0.0.1:8000/docs

Probar POST /chat/generar-preguntas

Caso texto: completar contexto (sin file).

Caso archivo: adjuntar PDF/DOCX (activar force_ocr si es escaneado).


Errores comunes

¿Porque no funciona el POST cuando envio solo texto de contexto?

La api espera que el cuerpo de la peticion envie la misma SIN la variable "file = null", simplemente enviar la peticion sin la variable "file".

400 Texto insuficiente / archivo no soportado / PDF sin contenido legible.

413 Archivo supera el tamaño máximo permitido (10 MB).

500 Falta OPENROUTER_API_KEY o error al parsear la respuesta del modelo.

¿qué es el OCR, qué hace force_ocr, y cómo funciona ocr_lang en LA API?

OCR (Optical Character Recognition) = Reconocimiento Óptico de Caracteres.
Es una tecnología que lee texto en imágenes (por ejemplo, un PDF escaneado o una foto de un documento) y convierte esas letras visuales en texto real que tu programa puede procesar.

¿Cuándo activar force_ocr?

Es recomendable activarlo cuando el PDF es un escaneo fisico(fotocopia, apunte, escaneado, foto), tambien si el PDF tiene texto pero muy desordenado o ilegible o en casos de no saber si tiene texto o imagenes, 

Recomendacion a la hora de usar force_ocr

Probar sin OCR Primero, y si devuelve "Texto Insuficiente", reintentar con force_ocr= True (force_ocr hace el proceso mas lento, pero es la unica forma de obtener texto legible si el PDF no lo contiene internamente)


¿Qué es ocr_lang?

ocr_lang define en qué idiomas buscar letras y palabras durante el reconocimiento OCR.
El motor pytesseract (basado en Tesseract OCR) necesita saber qué alfabetos y diccionarios usar.

Ejemplo:

ocr_lang="spa+eng"

Esto significa:

Intentá reconocer español (spa) y inglés (eng) al mismo tiempo


